# File Research: sources/cow-pools/openzfs/module/zfs/zio_inject.c

Read coverage: complete file, 1199 lines.

Purpose: ZFS fault injection registry and runtime handlers used by ZIO, ARC, vdev, import/export, and test tooling.

Main responsibilities:
- Maintains global `inject_handlers` list guarded by `inject_lock`.
- Tracks global `zio_injection_enabled` and delay-specific `inject_delay_count`.
- Registers, lists, and clears injection records via `zio_inject_fault()`, `zio_inject_list_next()`, and `zio_clear_fault()`.
- Implements matching and injection for data faults, decrypt faults, panic faults, device faults, label faults, ignored writes, I/O delay, ready-stage delay, import delay, and export delay.

Handler model:
- Each `inject_handler_t` has an ID, optional held `spa_t`, optional pool name for import/export delay, a `zinject_record_t`, delay lanes, and list linkage.
- Normal handlers take an injection reference on the SPA so the pool cannot disappear from the namespace while the handler exists.
- Import/export delay handlers match by pool name and intentionally do not hold an SPA.
- Delay-I/O handlers allocate lane arrays to model limited-concurrency latency injection.

Matching:
- `freq_triggered()` supports legacy 0-100 frequencies and scaled percentage frequencies.
- `zio_match_handler()` matches MOS metadata by type or exact objset/object/level/blkid/DVA/error ranges and updates match/inject counters.
- `zio_match_dva()` maps a physical vdev child ZIO back to the matching BP DVA index.
- `zio_match_iotype()` matches read/write/free/flush/trim/probe or all standard I/O types.

Runtime injection paths:
- `zio_handle_fault_injection()` injects data read errors, excluding non-logical I/O, non-read I/O, and rebuild checksum cases.
- `zio_handle_decrypt_injection()` injects authentication/decryption failures for matching bookmarks.
- `zio_handle_device_injection()` and `zio_handle_device_injections()` inject vdev/device errors, failfast behavior, retry marking, ENXIO open failure aux state, and EILSEQ bit flips.
- `zio_handle_label_injection()` injects label-region errors by translating relative label offsets to the active label copy.
- `zio_handle_ignored_writes()` probabilistically strips vdev I/O stages from syncing writes to simulate hardware accepting but losing writes.
- `spa_handle_ignored_writes()` validates ignored-write duration windows.
- `zio_handle_io_delay()` assigns matching vdev I/O to the soonest available delay lane and returns a target completion timestamp.
- `zio_handle_ready_delay()` delays logical I/O before READY when configured.
- `zio_handle_import_delay()` and `zio_handle_export_delay()` apply one-shot pool-level pauses.

Registration details:
- `zio_inject_fault()` validates delay lane/timer values, optionally unloads SPA, optionally converts byte ranges to blkids with `zio_calculate_range()`, enforces single import/export delay per pool, allocates handler state, inserts it under writer lock, increments enabled counters, and optionally flushes ARC.
- `zio_calculate_range()` resolves dataset/object/dnode and converts byte ranges and indirect levels into block ID ranges.
- `zio_clear_fault()` removes the handler, releases delay lanes, pool-name strings, SPA injection references, and decrements global counters.

Lifecycle:
- `zio_inject_init()` initializes lock, delay mutex, and list.
- `zio_inject_fini()` destroys them.
- Kernel exports expose injection state and public handler APIs.

Key dependencies:
- Called throughout `zio.c` at decompression/decryption, checksum verification, ready stage, vdev issue/done, ignored writes, and delay paths.
- Uses ARC flushing, SPA namespace/ref management, vdev label math, dnode lookup, and ZFS ioctl injection records.
