# subset-b-001052 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/ataflop.c -->
# sources/distributed-fs/ceph-client/drivers/block/ataflop.c

## Purpose

`ataflop.c` is the Atari floppy block driver for WD1772-compatible floppy hardware. It exposes Atari floppy drives through the legacy floppy block major, implements blk-mq request submission, talks directly to Atari DMA/FDC/PSG hardware registers, supports multiple disk geometries, handles media-change detection, and provides floppy ioctls for geometry and track formatting.

The driver is highly state-machine oriented. A single global in-flight request is translated into drive, side, track, sector, DMA address, and command state; subsequent FDC interrupts, timers, and completion callbacks advance or abort that state.

## Important APIs, Types, and Data

- `struct atari_disk_type` describes geometry: format name, sectors per track, total blocks, FDC speed, and track stretch.
- `struct atari_floppy_struct unit[FD_MAX_UNITS]` stores per-drive connection status, current media type, cached head position, write-protect state, blk-mq tag set, disks for geometry minors, ref/open state, and retry count.
- `minor2disktype[]` maps block minors to predefined media formats and maximum drive classes.
- Global request state includes `fd_request`, `SelectedDrive`, `ReqCmd`, `ReqBlock`, `ReqSide`, `ReqTrack`, `ReqSector`, `ReqCnt`, `ReqData`, `ReqBuffer`, `Probing`, `NeedSeek`, and formatting flags.
- `DMABuffer` and `TrackBuffer` are Atari ST-RAM DMA buffers. `TrackBuffer` caches whole tracks for reads when enabled.
- Timers: `motor_off_timer`, `readtrack_timer`, `timeout_timer`, and `fd_timer` handle drive deselection, multi-sector read progress, FDC timeouts, and media-change polling.
- Block operations are `floppy_fops` (`open`, `release`, `ioctl`, `check_events`) and blk-mq ops are `ataflop_mq_ops.queue_rq = ataflop_queue_rq`.
- Hardware helpers are the `FDC_READ` and `FDC_WRITE` macros plus Atari-specific globals such as `dma_wd`, `sound_ym`, `st_dma_ext_dmahi`, and `stdma_*`.

## Control Flow

Initialization starts in `atari_floppy_init()`. It rejects non-Atari machines, allocates one blk-mq tag set per possible drive, preallocates the default disk for each drive, chooses track-buffer policy, allocates ST-RAM for DMA/track buffering, adds default disks, probes hardware with `config_types()`, and registers `FLOPPY_MAJOR` with on-demand minor probing through `ataflop_probe()`.

`ataflop_probe()` lazily allocates and registers additional format minors. `ataflop_alloc_disk()` creates the `gendisk`, sets `FLOPPY_MAJOR`, one minor, no partitions, media-change events, `floppy_fops`, and a conservative maximum capacity.

Request submission enters `ataflop_queue_rq()`. The function serializes on `ataflop_lock`, refuses a second request while `fd_request` is live, claims Atari shared DMA via `stdma_try_lock()`, initializes the request, disables FDC interrupts while state is prepared, selects or probes a disk geometry, sets global request parameters with `setup_req_params()`, and starts the hardware state machine with `do_fd_action()`.

`do_fd_action()` first services reads from the whole-track cache when possible, then ensures the right drive is selected, calibrates if the track is unknown, seeks if the head is elsewhere, formats if a format command is active, or starts sector I/O with `fd_rwsec()`.

The normal read/write path is asynchronous:

- `fd_calibrate()` issues `RESTORE`; `fd_calibrate_done()` records track 0 or retries on failure.
- `fd_seek()` writes the target track and issues `SEEK`; `fd_seek_done()` updates `unit[].track` or restarts error handling.
- `fd_rwsec()` programs DMA, side, sector, FDC command, and timeout, then waits for an interrupt.
- `floppy_irq()` swaps out `FloppyIRQHandler`, reads FDC status, and calls the active completion routine.
- `fd_rwsec_done()` cancels whole-track timer state and calls `fd_rwsec_done1()`.
- `fd_rwsec_done1()` validates DMA/FDC status, handles autoprobe geometry fallback, copies data between DMA buffers and request memory, advances to the next sector, or completes the request and calls `finish_fdc()`.

Whole-track reads use `read_track`, `MultReadInProgress`, and `fd_readtrack_check()`. The timer samples the DMA address; if enough bytes have landed in the track buffer, it forces an FDC interrupt and completes the read without waiting for the controller to time out on the first nonexistent sector.

Formatting is handled by `fd_locked_ioctl(FDFMTTRK)` and `do_format()`. The queue is frozen/quiesced, shared DMA is locked, raw track data is synthesized into `TrackBuffer`, `IsFormatting` is set, and `do_fd_action()` drives `fd_writetrack()`/`fd_writetrack_done()` until `format_wait` completes.

`finish_fdc()` performs a dummy seek when needed to make the write-protect bit meaningful for future media-change checks, then `finish_fdc_done()` restarts media-change polling, starts delayed motor-off deselection, and releases ST-DMA.

## State and Persistence Behavior

Persistent kernel-visible state is block device state, drive geometry, open counts, and media-change flags. No disk metadata is persisted by the driver except data and formatting written to media.

Geometry state can be transient (`user_params[]` via `FDSETPRM`) or default/permanent for the life of the driver instance (`default_params[]` via `FDDEFPRM`). Media revalidation clears current geometry unless a default geometry is present. Capacity is updated from the active geometry with `set_capacity()`.

The whole-track cache is invalidated on writes, format operations, media changes, and some ioctl flush paths by setting `BufferDrive = -1`. Media changes are inferred through write-protect bit transitions, simulated changes (`fake_change`), and conservative reporting for write-protected media.

The current FDC/head position is cached in `unit[].track`; it is set to `-1` on uncertainty so the next request recalibrates.

## Dependencies and Integration Points

- Linux block layer: blk-mq, `gendisk`, `request_queue`, media-change events, block device operations, request completion/requeue helpers.
- Legacy floppy userspace ABI: `linux/fd.h` ioctls such as `FDGETPRM`, `FDSETPRM`, `FDDEFPRM`, `FDFMTTRK`, `FDCLRPRM`, `FDFLUSH`.
- Atari platform APIs and registers: MFP FDC interrupt, shared ST-DMA locking, Atari ST-RAM allocation, PSG port selection, FDC speed control, DMA cache maintenance.
- Boot/module parameters: `UseTrackbuffer`, `UserSteprate[]`, and non-module `floppy=` setup.
- On-demand block-device probing through `__register_blkdev(FLOPPY_MAJOR, "fd", ataflop_probe)`.

## Risks and Edge Cases

- The driver relies on many global variables for the single active request. Correct serialization through `ataflop_lock`, `fd_request`, and ST-DMA ownership is critical.
- Interrupt/timer races are explicitly handled in `fd_readtrack_check()`, `fd_times_out()`, and handler swapping, but remain a high-risk area because FDC interrupts, timer callbacks, and request completion all share global state.
- Media-change detection is inherently approximate on Atari hardware because it relies on write-protect behavior, so the driver intentionally reports conservative changes for write-protected media.
- Autoprobing changes `UDT` and capacity during error handling. Incorrect probing or stale capacity can affect request bounds and user-visible geometry.
- DMA buffer handling differs between extended DMA-capable hardware and systems requiring bounce buffers. Cache maintenance and physical address programming are correctness-critical.
- Formatting freezes/quiesces the queue and shares the same hardware state machine; failure paths must unquiesce/unfreeze and release FDC/DMA state.
- Cleanup appears to free `DMABuffer` but not separately free `TrackBuffer`, because `TrackBuffer` is an offset into the same allocation.

## Test Signals

- Build on Atari/m68k configurations with `CONFIG_ATARI`-compatible platform support and block layer changes enabled.
- Probe path: verify default disks register, on-demand geometry minors register, disconnected drives fail cleanly, and non-Atari init returns `-ENODEV`.
- I/O path: read/write across sector, side, and track boundaries; forced retries; recalibration after `RECALIBRATE_ERRORS`; final failure after `MAX_ERRORS`.
- Autoprobe: read unknown media and confirm geometry fallback, capacity updates, and no stale track buffer use.
- Media change: write-protect transition, fake changes from flush/format, `disk_check_media_change()` and `floppy_revalidate()` behavior.
- Formatting: `FDFMTTRK` with valid and invalid descriptors, write-protected media, and queue freeze/unfreeze on success and failure.
- Race tests around timeout firing near interrupt completion and whole-track read timer completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/ataflop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/brd.c -->
# sources/distributed-fs/ceph-client/drivers/block/brd.c

## Purpose

`brd.c` implements the RAM-backed block device driver. Each ramdisk stores written pages in a sparse xarray keyed by page-sized sector ranges, reads unwritten pages as zeroes, supports page-granular discard, exposes optional debugfs page counts, and registers the historical ramdisk major with optional on-demand device allocation.

## Important APIs, Types, and Data

- `struct brd_device` holds the ramdisk number, `gendisk`, global list node, xarray of backing pages, and `brd_nr_pages` debug/accounting counter.
- `brd_lookup_page()` performs an RCU xarray lookup and safely grabs a page reference with retry handling.
- `brd_insert_page()` allocates a zeroed highmem page and atomically inserts it into the xarray with `__xa_cmpxchg()`.
- `brd_rw_bvec()` processes one bio segment fragment capped to a brd page boundary.
- `brd_do_discard()` erases fully page-aligned page ranges from the xarray.
- `brd_submit_bio()` is the block I/O entry point.
- Module parameters: `rd_nr`, `rd_size`, and `max_part`.
- `brd_alloc()`, `brd_probe()`, `brd_cleanup()`, `brd_init()`, and `brd_exit()` manage device lifecycle.

## Control Flow

`brd_init()` normalizes `max_part`, creates the `ramdisk_pages` debugfs directory, registers `RAMDISK_MAJOR` with `brd_probe()` as an on-demand probe callback, and allocates `rd_nr` initial devices.

`brd_alloc()` creates one `struct brd_device`, initializes its xarray, creates a debugfs `u64` page counter if debugfs setup succeeded, allocates a disk with queue limits, assigns `brd_fops`, sets capacity to `rd_size * 2` sectors, and calls `add_disk()`.

Normal I/O reaches `brd_submit_bio()`. Discard bios are handled by `brd_do_discard()` and completed immediately. Read/write bios loop over `brd_rw_bvec()` until `bio->bi_iter.bi_size` is exhausted, then call `bio_endio()`.

`brd_rw_bvec()` calculates the target brd page and offset from `bi_sector`, limits the operation to the rest of that page, looks up the existing page, allocates on write if missing, maps the bio vector locally, copies bytes into or out of the page, zero-fills reads from missing pages, advances the bio iterator, and drops the page reference. Allocation failure reports `bio_wouldblock_error()` for `REQ_NOWAIT` allocation misses or `bio_io_error()` otherwise.

`brd_do_discard()` rounds the requested sector range inward to full brd pages, erases pages under xarray lock, drops page references, and decrements `brd_nr_pages`.

Cleanup removes debugfs, deletes/puts disks, frees all xarray pages, destroys xarrays, and frees device structs.

## State and Persistence Behavior

The device contents are volatile memory only. Written pages persist until discarded, the module exits, the device is destroyed, or memory is reclaimed by explicit driver teardown. Unwritten sectors are implicit zeroes and consume no memory.

The xarray is the authoritative content store. `brd_nr_pages` tracks currently allocated backing pages for debugfs visibility. No backing storage, metadata, or recovery path exists.

## Dependencies and Integration Points

- Linux block layer: `gendisk`, `block_device_operations.submit_bio`, queue limits, capacity, dynamic block-major probing.
- Memory APIs: highmem pages, local bvec mapping, xarray with RCU and explicit xarray lock.
- Debugfs: optional `ramdisk_pages/ramN` counters.
- Kernel boot/module compatibility: `ramdisk_size=` setup when built in, `MODULE_ALIAS_BLOCKDEV_MAJOR(RAMDISK_MAJOR)`, and alias `rd`.

## Risks and Edge Cases

- `brd_lookup_page()` must handle concurrent erasure and page ref acquisition correctly; its retry loop is central to avoiding use-after-free.
- `brd_insert_page()` allocates before xarray insertion. Concurrent writers may race; the cmpxchg path drops the unused page and returns the existing page with a reference.
- Discard erases only full page-aligned ranges, so partial-page discard does not zero partial sectors.
- Memory growth is proportional to written pages and bounded only by allocation failure. Large writes can exhaust memory.
- Queue limits advertise `BLK_FEAT_NOWAIT`, so `REQ_NOWAIT` paths must fail with would-block semantics when allocation cannot proceed.
- `brd_alloc()` creates debugfs entries before disk allocation; cleanup relies on recursive debugfs removal during module cleanup rather than per-device removal on early allocation failure.

## Test Signals

- Build with ramdisk support as built-in and module.
- Create initial and on-demand `/dev/ramN` devices and verify capacity/minor spacing with several `max_part` values.
- Read unwritten sectors and verify zero-fill.
- Write, read back, discard aligned ranges, and verify discarded pages read zero and page counters decrease.
- Exercise unaligned discard to confirm only full pages are removed.
- Use `REQ_NOWAIT` write paths under memory pressure to verify would-block completion.
- Concurrent read/write/discard stress to shake xarray reference and erase races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/brd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/Kconfig

## Purpose

This Kconfig file defines configuration for the DRBD replicated block device driver and its fault-injection option. It gates DRBD on procfs and networking support, selects required helper libraries, and documents the driver as a network RAID-1 style replicated block device for high-availability clusters.

## Important Options

- `BLK_DEV_DRBD`: tristate option for DRBD support. It depends on `PROC_FS && INET`, selects `LRU_CACHE` and `CRC32`, and can be built in, modular, or disabled.
- `DRBD_FAULT_INJECTION`: boolean option depending on `BLK_DEV_DRBD`. It enables sysfs/module-parameter driven simulated faults for metadata I/O, data I/O, bitmap allocation, peer request allocation, and receive-side corruption.
- A comment explains that DRBD is disabled when `PROC_FS` or `INET` is not selected.

## Control Flow and Integration

Kconfig has no runtime control flow, but it shapes compilation:

- `BLK_DEV_DRBD=m/y` causes the Makefile to build `drbd.o`.
- Selecting `LRU_CACHE` is required by the activity log and resync extent caches.
- Selecting `CRC32` supports checksum paths used by DRBD metadata/activity-log code.
- Optional fault injection compiles hooks used by DRBD paths such as metadata I/O, bitmap allocation, and request allocation.

## State and Persistence Behavior

The file does not store runtime state. Its choices affect whether DRBD code exists in the kernel and whether fault injection parameters exist at runtime.

## Dependencies

- `PROC_FS`: required for DRBD proc integration.
- `INET`: required because DRBD replication uses networking.
- `LRU_CACHE` and `CRC32`: selected helper functionality.
- The help text notes that authentication additionally requires `CRYPTO_HMAC` and a hash function, but those are not hard dependencies in this option.

## Risks and Edge Cases

- Authentication support is documented but not selected automatically; a configuration can enable DRBD without the crypto options needed for authenticated connections.
- The disabled comment only appears for missing `PROC_FS` or `INET`; users may still need other runtime tooling and cluster management outside kernel config.
- Fault injection is powerful and can simulate corruption; it must remain test-only.

## Test Signals

- Kconfig dependency tests with `PROC_FS=n`, `INET=n`, and both enabled.
- Build DRBD built-in and module configurations.
- Build with and without `DRBD_FAULT_INJECTION` and verify sysfs/module fault controls appear only when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/Makefile

## Purpose

This Makefile defines how the DRBD kernel object is composed. It aggregates DRBD source objects into `drbd.o`, conditionally includes debugfs support, and links the final object according to `CONFIG_BLK_DEV_DRBD`.

## Important Build Rules

- `drbd-y` includes core objects: `drbd_buildtag.o`, `drbd_bitmap.o`, `drbd_proc.o`, `drbd_worker.o`, `drbd_receiver.o`, `drbd_req.o`, `drbd_actlog.o`, `drbd_main.o`, `drbd_strings.o`, `drbd_nl.o`, `drbd_interval.o`, and `drbd_state.o`.
- `drbd-$(CONFIG_DEBUG_FS) += drbd_debugfs.o` includes debugfs instrumentation only when debugfs is configured.
- `obj-$(CONFIG_BLK_DEV_DRBD) += drbd.o` builds DRBD according to the tristate selected in Kconfig.

## Control Flow and Integration

There is no runtime control flow. The file controls object composition. The ordering places build tag and bitmap/proc objects first, followed by worker, receiver, request, activity-log, main, strings, netlink, interval, and state components. Debugfs is compile-time optional while the header provides stubs for non-debugfs builds.

## State and Persistence Behavior

No runtime state is stored here. Build selection affects which runtime code paths are present.

## Dependencies

- Consumes `CONFIG_BLK_DEV_DRBD` from `Kconfig`.
- Consumes `CONFIG_DEBUG_FS` from the broader kernel config.
- Assumes all listed DRBD source files participate in one module/built-in object.

## Risks and Edge Cases

- Adding a new DRBD translation unit requires updating `drbd-y`; missing objects can surface as unresolved symbols or disabled functionality.
- Debugfs code must remain optional and all callers must tolerate stubbed debugfs functions when `CONFIG_DEBUG_FS=n`.
- Build tag logic depends on `drbd_buildtag.o` always being present.

## Test Signals

- Build with `CONFIG_BLK_DEV_DRBD=n/m/y`.
- Build with `CONFIG_DEBUG_FS=n/y` and confirm `drbd_debugfs.o` is included only with debugfs.
- Module build should expose a coherent `drbd.ko` with all required symbols resolved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_actlog.c -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_actlog.c

## Purpose

`drbd_actlog.c` implements DRBD metadata I/O helpers, the activity log transaction machinery, and the resync extent coordination layer. The activity log records recently active 4 MiB data extents in an on-disk ring so DRBD can recover after crashes without resyncing the entire device. The same file also updates the out-of-sync bitmap in response to application writes, successful resync, and failed resync, and it arbitrates write exclusion between application I/O and resync I/O.

## Important APIs, Types, and Data

- `struct al_transaction_on_disk` is the 4 KiB big-endian activity-log transaction block. It stores magic, transaction number, CRC32C, transaction type, update count, AL context size/start slot, update slot/extent arrays, and context snapshot entries.
- `drbd_md_get_buffer()` / `drbd_md_put_buffer()` serialize access to `device->md_io.page` with `md_io.in_use` and `misc_wait`.
- `drbd_md_sync_page_io()` and `_drbd_md_sync_page_io()` perform synchronous 4 KiB metadata reads/writes with optional flush/FUA, timeout handling, and fault injection.
- `drbd_al_begin_io_fastpath()`, `drbd_al_begin_io_prepare()`, `drbd_al_begin_io_commit()`, `drbd_al_begin_io()`, `drbd_al_begin_io_nonblock()`, and `drbd_al_complete_io()` manage activity-log extent references around application I/O.
- `__al_write_transaction()` and `al_write_transaction()` serialize dirty AL changes to the on-disk transaction ring, including hinted bitmap writeout.
- `drbd_al_initialize()` initializes the on-disk AL ring.
- `__drbd_change_sync()` plus `update_sync_bits()` update bitmap bits for `SET_IN_SYNC`, `SET_OUT_OF_SYNC`, and `RECORD_RS_FAILED`.
- `drbd_rs_begin_io()`, `drbd_try_rs_begin_io()`, `drbd_rs_complete_io()`, `drbd_rs_cancel_all()`, and `drbd_rs_del_all()` manage resync LRU extents and write exclusion flags.
- Shared state includes `device->act_log`, `device->resync`, `device->al_lock`, `device->al_wait`, `device->al_tr_number`, `device->al_tr_cycle`, `device->resync_locked`, `device->resync_wenr`, `device->rs_failed`, and resync progress marks.

## Control Flow

Application write admission starts by translating the request interval to AL extent numbers. The fast path can acquire one already-available extent nonblocking through `_al_get()`. The normal path waits for every required extent with `drbd_al_begin_io_prepare()`, notes whether any LRU cache entry changed, and commits if a transaction is needed.

`drbd_al_begin_io_commit()` serializes AL transactions with `lc_try_lock_for_transaction()`. If `pending_changes` remain and `disk_conf->al_updates` permits writes, `al_write_transaction()` writes them to disk. The LRU cache is then marked committed and waiters are woken. `drbd_al_complete_io()` later drops references on all AL extents touched by the request.

`__al_write_transaction()` constructs one transaction block from `act_log->to_be_changed`, marks bitmap pages associated with evicted AL extents for writeout, writes context entries from the AL LRU, advances `al_tr_cycle`, computes CRC32C over the block, writes hinted bitmap pages first, and then writes the AL block to the metadata area if configured. The on-disk sector is derived from transaction number, stripe count, stripe size, metadata offset, and AL offset.

Metadata I/O goes through `drbd_md_sync_page_io()`. It validates metadata sector ranges, prepares a one-page bio against `md_bdev`, gets an ldev reference for normal cases, sets completion fields, optionally injects faults, submits the bio, and waits until completion, force-detach, or disk timeout. Timeout calls `drbd_chk_io_error()` with force-detach semantics.

Bitmap sync updates enter `__drbd_change_sync()`. It validates request size, maps sector ranges to bitmap bit ranges, rounds differently for clearing in-sync bits versus setting out-of-sync/failure bits, gets a local disk reference, and calls `update_sync_bits()`. `update_sync_bits()` chunks by resync extent, modifies bitmap bits through `drbd_bm_*`, updates cached `bm_extent` counters under `al_lock`, advances resync progress marks, schedules lazy on-disk bitmap updates, and wakes AL waiters.

Resync I/O exclusion uses the resync LRU. `drbd_rs_begin_io()` sleeps until `_bme_get()` can lock a bitmap extent, waits for all corresponding AL extents to become inactive unless throttling gives priority to application I/O, then sets `BME_LOCKED`. `drbd_try_rs_begin_io()` performs a nonblocking version with a remembered half-locked extent in `resync_wenr`. `drbd_rs_complete_io()` drops the resync extent reference and clears `BME_LOCKED`, `BME_NO_WRITES`, and `BME_PRIORITY` when the last reference leaves.

## State and Persistence Behavior

The activity log persists to the DRBD metadata area as a ring of 4 KiB transaction blocks. Each transaction includes update deltas and a rolling context snapshot so the log can be reconstructed after crash. Transaction blocks are big endian and protected by CRC32C.

The out-of-sync bitmap is persistent but managed by `drbd_bitmap.c`; this file decides when bitmap pages must be written before AL updates and when lazy bitmap progress updates should be scheduled. Hinted bitmap writeout ties AL eviction to bitmap persistence so evicted extents do not lose dirty state.

Resync LRU state (`rs_left`, `rs_failed`, lock flags) is in-memory cache state. It can be recounted from the bitmap when a cache entry is reused or detected inconsistent.

## Dependencies and Integration Points

- `drbd_int.h` for core DRBD structs, state, wait queues, LRU cache, metadata layout, and logging helpers.
- `linux/crc32c.h` for AL transaction checksum.
- Block layer bios for metadata I/O.
- LRU cache helpers (`lc_get`, `lc_try_get`, `lc_committed`, `lc_put`, `lc_del`, `lc_reset`).
- Bitmap APIs from `drbd_bitmap.c`, especially `drbd_bm_mark_for_writeout()`, `drbd_bm_write_hinted()`, bit set/clear/count, and total weight.
- State and worker integration through `drbd_chk_io_error()`, `drbd_device_post_work()`, `RS_PROGRESS`, `RS_DONE`, and connection protocol version checks.
- Fault injection through `drbd_insert_fault()` when enabled.

## Risks and Edge Cases

- Metadata buffer serialization is strict: callers must hold the one `md_io` buffer exactly once, and completion also decrements `md_io.in_use` for submitted bios.
- AL transaction error handling has a FIXME around canceling failed LRU changes after write failure; committed state may need careful review when metadata I/O fails.
- Sector range checks log out-of-range metadata access but still rely on lower-level error handling.
- Resync and application writes contend through AL and resync LRU flags. Mistakes can allow writes into `BME_NO_WRITES` ranges or deadlock resync waiters.
- `update_rs_extent()` recounts when counters go inconsistent, but counter underflow or stale cache state is a sign of subtle concurrency races.
- Nonblocking AL begin can partially acquire extent references and stores continuation in `partially_in_al_next_enr`; callers must resume and complete correctly.
- Lazy bitmap update timing can defer persistence; crash behavior depends on the AL/bitmap ordering guarantees.

## Test Signals

- Metadata I/O tests for read/write success, timeout, force-detach, and injected metadata faults.
- AL transaction tests that cross one extent and multiple extents, including pending-change commit and `al_updates=0`.
- Crash/restart style tests verifying AL ring recovery after writes and bitmap hinted writeout.
- Resync/application write contention tests for `BME_NO_WRITES`, `BME_PRIORITY`, throttling, and nonblocking retry behavior.
- Sync bit update tests for aligned and unaligned sectors, full-device end-sector rounding, failed resync accounting, and lazy bitmap update scheduling.
- Lockdep/KCSAN stress around `al_lock`, `al_wait`, LRU cache refcounts, and disk detach while metadata I/O is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_actlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_bitmap.c -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_bitmap.c

## Purpose

`drbd_bitmap.c` implements DRBD's in-memory and on-disk out-of-sync bitmap. One bitmap bit represents a 4 KiB block of replicated storage. The file handles bitmap allocation, resize, locking, bit mutation, counting, search, endian-stable transfer, dirty-page tracking, and asynchronous bitmap I/O to the DRBD metadata area.

## Important APIs, Types, and Data

- `struct drbd_bitmap` owns the page array, `bm_lock`, `bm_change`, bitmap page I/O wait queue, dirty/hint arrays, bit/word/page counts, capacity, set-bit count, flags, and lock debugging fields.
- Page-private bits encode page index and state: `BM_PAGE_IO_LOCK`, `BM_PAGE_IO_ERROR`, `BM_PAGE_NEED_WRITEOUT`, `BM_PAGE_LAZY_WRITEOUT`, and `BM_PAGE_HINT_WRITEOUT`.
- Public lock/lifecycle APIs: `drbd_bm_init()`, `drbd_bm_cleanup()`, `drbd_bm_lock()`, `drbd_bm_unlock()`, `drbd_bm_resize()`, and `drbd_bm_capacity()`.
- Public bitmap status APIs: `_drbd_bm_total_weight()`, `drbd_bm_total_weight()`, `drbd_bm_words()`, `drbd_bm_bits()`, `drbd_bm_find_next()`, `_drbd_bm_find_next()`, `_drbd_bm_find_next_zero()`, `drbd_bm_test_bit()`, `drbd_bm_count_bits()`, and `drbd_bm_e_weight()`.
- Public mutation APIs: `drbd_bm_merge_lel()`, `drbd_bm_get_lel()`, `drbd_bm_set_all()`, `drbd_bm_clear_all()`, `drbd_bm_set_bits()`, `drbd_bm_clear_bits()`, and `_drbd_bm_set_bits()`.
- I/O APIs: `drbd_bm_read()`, `drbd_bm_write()`, `drbd_bm_write_all()`, `drbd_bm_write_lazy()`, `drbd_bm_write_copy_pages()`, and `drbd_bm_write_hinted()`.
- AL integration APIs: `drbd_bm_reset_al_hints()` and `drbd_bm_mark_for_writeout()`.

## Control Flow

`drbd_bm_init()` allocates and initializes the bitmap object but not its pages. `drbd_bm_resize()` is called when device capacity changes. It serializes through `drbd_bm_lock()`, computes the number of bits and 64-bit-aligned words needed, verifies on-disk metadata has enough bitmap space when a local disk exists, reallocates the page-pointer array and pages, copies existing pages, initializes new ranges either set or clear, updates capacity/count metadata under `bm_lock`, clears surplus bits beyond capacity, frees truncated pages, recounts on shrink, and unlocks.

Bit operations map page-sized chunks with `kmap_atomic()`. `bm_change_bits_to()` and `__bm_change_bits_to()` update individual bit ranges, maintain `bm_set`, and mark pages either `NEED_WRITEOUT` when bits are set or `LAZY_WRITEOUT` when bits are cleared. `_drbd_bm_set_bits()` optimizes large set ranges by filling full words while still accounting for changed bits.

Find/count operations walk bitmap pages under `bm_lock` and use little-endian bit helpers. The bitmap is intentionally stored little endian in memory and on disk, which simplifies network transfer and cross-platform operation.

Bitmap I/O is centralized in `bm_rw()`. It creates a `drbd_bm_aio_ctx`, gets a local disk reference, records the context in `pending_bitmap_io`, submits one bio per selected bitmap page through `bm_page_io_async()`, waits for `in_flight` completion via `misc_wait`, handles I/O errors, recounts set bits after reads, and drops the context krefs.

`bm_page_io_async()` computes the metadata sector for the page, trims length for small external metadata areas, serializes per-page I/O with `BM_PAGE_IO_LOCK`, clears dirty/lazy state before submission so concurrent changes redirty the page, optionally copies the page for writeout that may race with ongoing bitmap mutation, builds a bio, and submits or fault-injects it. `drbd_bm_endio()` records errors, unlocks the page, frees copied pages, and completes the context.

Write variants select pages differently: normal write skips unchanged pages, write-all writes every page, lazy write uses copied pages and optionally stops at an upper page index, copy-pages writes changed pages via temporary pages, and hinted write writes only AL-marked pages that are still dirty.

## State and Persistence Behavior

The in-memory bitmap is authoritative while a local disk is attached. Dirty page-private flags track what must be written to metadata. The on-disk bitmap lives in the metadata area beginning at `md_offset + bm_offset` and ending before the AL or metadata end depending on internal/external layout.

`bm_set` caches the total number of out-of-sync bits. It is maintained incrementally on mutations and recounted after reads or shrink. Surplus bits outside device capacity are cleared for normal semantics; 32-bit padding alignment is explicitly handled for 32/64-bit interoperability.

Page I/O errors mark `BM_PAGE_IO_ERROR` and trigger DRBD metadata I/O error handling. Lazy writeout permits cleared bits to be deferred because remote bitmap exchange can reconstruct them if necessary; set bits are marked for stronger writeout.

## Dependencies and Integration Points

- DRBD core structs and metadata layout from `drbd_int.h`.
- Activity log integration in `drbd_actlog.c` through hinted bitmap writeout.
- Block layer bio APIs and the shared DRBD metadata bio set/page mempool.
- Linux bitmap, highmem, vmalloc/kvfree, waitqueue, spinlock, mutex, and kref APIs.
- DRBD fault injection for bitmap allocation and metadata read/write faults.
- Debugfs observes `pending_bitmap_io` via `drbd_debugfs.c`.

## Risks and Edge Cases

- Very large devices produce very large bitmaps; comments document limits, especially on 32-bit architectures.
- Bitmap resize must avoid deadlocks by using `GFP_NOIO` while DRBD I/O may be suspended.
- `bm_set` is protected by `bm_lock` but comments note inherent raciness for callers that do not hold broader synchronization.
- Page-private state combines index and flags; incorrect bit usage can corrupt both I/O state and page identity.
- `bm_rw()` relies on local disk references to keep bitmap and metadata devices stable during asynchronous I/O.
- Copy-pages writeout is necessary where bitmap changes may continue during writeback. Using normal writeback in those contexts can lose dirtying information.
- Metadata sector trimming for small external metadata devices must avoid reading/writing beyond valid bitmap space.

## Test Signals

- Resize tests for zero capacity, grow with new bits set/clear, shrink, metadata space too small, allocation failure injection, and 32-bit padding behavior.
- Bit operation tests for set, clear, large range set, count, find-next, extent weight, and surplus masking.
- Endian/interoperability tests for `drbd_bm_merge_lel()` and `drbd_bm_get_lel()`.
- Bitmap I/O tests for read, normal write, write-all, lazy write, copy-pages, hinted write, metadata I/O errors, and force-detach/timeouts.
- Stress tests with concurrent bit changes during copy-pages and normal I/O to confirm pages are redirtied or warnings trigger appropriately.
- Locking tests around `bm_change`, `bm_lock`, page I/O locks, and pending bitmap I/O list handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_buildtag.c -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_buildtag.c

## Purpose

`drbd_buildtag.c` provides the `drbd_buildtag()` helper used to report the provenance of the DRBD code. In in-tree builds it reports a built-in marker; in module builds it can expose the module `srcversion`.

## Important APIs and Data

- `const char *drbd_buildtag(void)` returns a static string.
- The static `buildtag[38]` is initialized so that built-in builds can become `"built-in"` by changing the first byte, while module builds format `"srcversion: <THIS_MODULE->srcversion>"`.
- Includes `linux/drbd_config.h` for DRBD version/config context and `linux/module.h` for module metadata.

## Control Flow

The first call initializes the static buffer if `buildtag[0] == 0`. With `MODULE` defined, it formats the module source version into the fixed-size buffer. Without `MODULE`, it sets the first character to `b`, making the initialized string read as built-in. Later calls return the already-initialized buffer.

## State and Persistence Behavior

State is a process-lifetime static buffer inside the kernel/module. It is not persistent across reboot or module reload. There is no locking; initialization is idempotent enough for the expected diagnostic use, though simultaneous first callers could race on identical data.

## Dependencies and Integration Points

- Used by debugfs version reporting in `drbd_debugfs.c`.
- Depends on module metadata when DRBD is built as a module.
- Complements DRBD version macros such as `REL_VERSION` reported elsewhere.

## Risks and Edge Cases

- The fixed buffer size assumes the formatted `srcversion` fits the padded width plus prefix.
- No locking around first initialization, but writes are deterministic and the function returns a static string.
- Built-in behavior relies on the unusual initial string `"\0uilt-in"` and setting byte 0 to `b`; maintainers may miss this idiom.

## Test Signals

- Build DRBD built-in and confirm version output contains `built-in`.
- Build DRBD as a module and confirm version output includes the module source version.
- Compile with warnings enabled to catch formatting or buffer-size regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_buildtag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_debugfs.c

## Purpose

`drbd_debugfs.c` implements DRBD's debugfs diagnostics. It creates a `/sys/kernel/debug/drbd` tree with version information, resource directories, connection diagnostics, volume diagnostics, minor symlinks, request summaries, metadata/bitmap I/O visibility, activity-log and resync cache dumps, generation IDs, and callback history.

The file is observational. It should not change DRBD replication state, but it must safely traverse live DRBD structures while resources, connections, devices, and peer devices may be removed.

## Important APIs, Types, and Data

- Global dentries: `drbd_debugfs_root`, `drbd_debugfs_version`, `drbd_debugfs_resources`, and `drbd_debugfs_minors`.
- Add/cleanup APIs: `drbd_debugfs_init()`, `drbd_debugfs_cleanup()`, `drbd_debugfs_resource_add/cleanup()`, `drbd_debugfs_connection_add/cleanup()`, `drbd_debugfs_device_add/cleanup()`, and `drbd_debugfs_peer_device_add/cleanup()`.
- `drbd_single_open()` wraps `single_open()` with dentry positivity and kref acquisition to prevent object teardown while a debugfs file is open.
- Show functions include `in_flight_summary_show()`, `callback_history_show()`, `connection_oldest_requests_show()`, device `oldest_requests`, `act_log_extents`, `resync_extents`, `data_gen_id`, `ed_gen_id`, and `drbd_version_show()`.
- Request printing helpers decode `enum drbd_req_state_bits` and peer request flags into tabular seq_file output.

## Control Flow

Module/debugfs setup calls `drbd_debugfs_init()`, which creates root `drbd`, `version`, `resources`, and `minors` entries. Cleanup removes these in reverse-ish dependency order through `drbd_debugfs_remove()`, which nulls dentry pointers after `debugfs_remove()`.

When a resource is added, `drbd_debugfs_resource_add()` creates `/resources/<resource>`, `volumes`, `connections`, and `in_flight_summary`. The summary file prints oldest bitmap I/O, metadata I/O, socket buffer stats, oldest peer requests, application requests waiting for the AL, and transfer-log summary.

Connection add creates a current `peer` directory under the resource connection directory, plus `callback_history` and `oldest_requests`. The callback file prints worker/receiver callback timing history; oldest requests prints the connection's selected request pointers under `req_lock`.

Device add creates a volume directory by vnr, a minor-number symlink under `/minors`, and diagnostic files for oldest requests, AL extents, resync extents, data generation IDs, and exposed data UUID. Device cleanup removes each dentry pointer.

Peer-device add currently creates a vnr directory below the connection directory; cleanup removes it.

Every state-reading file uses seq_file. Many show functions take snapshots under `req_lock`, RCU, or object-specific locks, then format ages relative to `jiffies`. Long transfer-log scans periodically drop and reacquire `req_lock` to avoid holding interrupts disabled for too long.

## State and Persistence Behavior

The debugfs hierarchy mirrors runtime DRBD object state and disappears at cleanup/unmount/module unload. It does not persist data. The diagnostic content is a point-in-time or best-effort snapshot and can be stale immediately after reading.

The file intentionally includes format version markers (`v: 0`) in several outputs. Comments instruct maintainers to bump versions if output format changes.

## Dependencies and Integration Points

- Requires `CONFIG_DEBUG_FS`; otherwise `drbd_debugfs.h` stubs these calls.
- Uses DRBD core resource, connection, device, peer-device, request, peer-request, bitmap I/O, activity-log, resync, UUID, and version structures.
- Uses `seq_file`, debugfs, kref, RCU, spinlocks, jiffies, TCP socket internals, and LRU cache dump helpers.
- Integrates with object lifecycle via krefs and cleanup hooks from DRBD resource/connection/device management.

## Risks and Edge Cases

- Debugfs files are read concurrently with object removal. `drbd_single_open()` mitigates this with parent inode locking, dentry positivity checks, and `kref_get_unless_zero()`.
- Some diagnostic reads are intentionally racy and copy fields without full locking, such as metadata I/O snapshots and callback timing details.
- `in_flight_summary_show()` assumes the first connection and uses TCP internals when a socket exists; future multi-peer behavior may require directory naming and iteration changes.
- Long transfer-log scans drop `req_lock` and use request krefs to avoid holding the lock too long; mistakes in list continuation can skip or duplicate entries under churn.
- Debugfs creation failures are mostly tolerated by storing dentries and continuing, but later code must handle null or error dentries.

## Test Signals

- Build with `CONFIG_DEBUG_FS=y` and confirm expected debugfs tree appears for resources, connections, devices, peer devices, and minors.
- Build with `CONFIG_DEBUG_FS=n` and confirm callers compile against stubs.
- Open debugfs files while concurrently deleting DRBD resources/devices to validate kref lifetime handling.
- Exercise active application I/O, peer I/O, bitmap I/O, metadata I/O, AL waits, and resync; confirm summaries expose plausible entries.
- Format-version regression tests for scripts that consume debugfs outputs.
- Lockdep/KASAN tests for request-list traversal and cleanup races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_debugfs.h

## Purpose

`drbd_debugfs.h` declares the DRBD debugfs lifecycle hooks and provides no-op inline stubs when debugfs is disabled. It lets the rest of the DRBD driver call debugfs integration points unconditionally without scattering `#ifdef CONFIG_DEBUG_FS` through core code.

## Important APIs

With `CONFIG_DEBUG_FS` enabled, the header declares:

- `drbd_debugfs_init()` and `drbd_debugfs_cleanup()`.
- `drbd_debugfs_resource_add()` / `drbd_debugfs_resource_cleanup()`.
- `drbd_debugfs_connection_add()` / `drbd_debugfs_connection_cleanup()`.
- `drbd_debugfs_device_add()` / `drbd_debugfs_device_cleanup()`.
- `drbd_debugfs_peer_device_add()` / `drbd_debugfs_peer_device_cleanup()`.

With debugfs disabled, it defines static inline no-op versions of the same functions.

## Control Flow

There is no independent runtime control flow in the header. It determines whether calls from DRBD initialization and object lifecycle code link to real debugfs implementation in `drbd_debugfs.c` or compile away to no-ops.

## State and Persistence Behavior

The header owns no state. In debugfs builds, state is maintained by `drbd_debugfs.c` and the dentry pointers embedded in DRBD objects. In non-debugfs builds, no debugfs state exists.

## Dependencies and Integration Points

- Includes kernel, module, and debugfs headers, plus `drbd_int.h` for DRBD object types.
- Must match the function definitions in `drbd_debugfs.c`.
- Integrated by DRBD resource, connection, device, and peer-device lifecycle paths.

## Risks and Edge Cases

- Prototype drift between this header and `drbd_debugfs.c` breaks debugfs builds or silently changes no-op behavior.
- The no-op stubs must preserve attributes such as `__init` where relevant so call sites compile in all configurations.
- Including `drbd_int.h` can increase dependency coupling; changes in core type declarations may affect debugfs consumers.

## Test Signals

- Compile DRBD with `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n`.
- Verify core DRBD code can call every debugfs lifecycle hook without local preprocessor guards.
- Check that module init/cleanup and object add/remove paths have no unresolved debugfs symbols in non-debugfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_debugfs.h -->
