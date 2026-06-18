# subset-b-004042 research

This grouped report covers the requested Linux MD RAID0 and RAID1 source files from the Ceph client source snapshot. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid0.c -->
# sources/distributed-fs/ceph-client/drivers/md/raid0.c

## Purpose
`raid0.c` implements the Linux MD RAID0 personality: a striped block device with no redundancy. It builds the run-time strip-zone map from component device sizes, maps each incoming bio to exactly one member device, handles discard fan-out across stripes, reports status, fails the whole array on member failure, and supports limited takeover from degraded RAID4/5, RAID10, and RAID1 layouts.

## Important APIs, Types, And Functions
The file registers `raid0_personality` with MD through `register_md_submodule()`. Its main personality callbacks are `raid0_run`, `raid0_make_request`, `raid0_status`, `raid0_size`, `raid0_takeover`, `raid0_quiesce`, `raid0_error`, and `raid0_free`. `create_strip_zones()` is the central setup routine; it allocates `struct r0conf`, `strip_zone[]`, and the flattened zone-by-disk `devlist`. `find_zone()` converts an array sector into a zone-relative sector. `map_sector()` maps a zone-relative sector to a component `md_rdev` and device-relative offset. `raid0_map_submit_bio()` remaps normal reads/writes/write-zeroes and submits the clone/current bio. `raid0_handle_discard()` translates a discard range into per-device discard bios. Takeover helpers adjust `mddev` geometry before creating the RAID0 config.

## Control Flow
Startup rejects missing chunk size and arrays with bitmaps, applies queue limits for non-DM MD devices, then creates strip zones unless takeover already supplied `mddev->private`. Zone creation rounds each rdev size down to a chunk multiple, counts unique device-size bands, verifies slot coverage, makes the first zone contain all disks, and creates later zones only from devices that extend beyond the previous smallest device. Multi-zone arrays must use either `RAID0_ORIG_LAYOUT` or `RAID0_ALT_MULTIZONE_LAYOUT`; if the superblock and `raid0.default_layout` do not specify one, assembly is refused because Linux 3.14 changed historical layout behavior.

The request path handles flush through `md_flush_request()`, dispatches discard to `raid0_handle_discard()`, splits normal bios at chunk boundaries, then remaps to the selected rdev. The original layout maps multizone sectors using the absolute bio sector for disk rotation compatibility; the alternate layout maps using the zone-relative sector. Broken member devices cause `bio_io_error()` and `md_error()`. Discards may be split at zone boundaries and then decomposed into per-disk ranges based on stripe index, disk index, `disk_shift`, and `dev_start`.

## State And Persistence
Persistent RAID0 state lives in MD metadata outside this file: level, layout, raid disks, chunk sectors, device offsets, and component sizes. In-memory state is `struct r0conf`, which stores zone boundaries, device-start offsets, layout choice, and the rdev lookup table. `create_strip_zones()` mutates `rdev->sectors` to a chunk-aligned value and takeover paths update `mddev->new_*`, `raid_disks`, `delta_disks`, `resync_offset`, and unsupported feature flags. RAID0 has no bitmap, journal, parity log, or recovery persistence because any member loss breaks the array.

## Dependencies And Integration Points
This file integrates with MD core (`md.h`), queue-limit stacking, integrity registration, bio splitting/submission, discard helpers, trace remap events, and RAID5 layout constants for takeover. It depends on `raid0.h` for `struct r0conf`, `struct strip_zone`, and layout enum definitions. It participates in module aliasing as MD personality 2 and exposes the `raid0.default_layout` module parameter.

## Risks
The highest-risk logic is multizone mapping compatibility: wrong layout selection or `disk_shift` math remaps sectors to different disks and can corrupt existing arrays. Zone construction assumes unique size bands and complete raid-disk slot coverage; takeover paths intentionally rewrite geometry and must only run under MD's reshape/takeover constraints. Discard range math differs from normal bio mapping and can silently discard wrong sectors if start/end disk-index calculations regress. RAID0 marks the array broken on member failure, so error handling is intentionally terminal rather than recoverable.

## Test Signals
Useful signals are MD RAID0 creation and assembly tests with equal and unequal device sizes, explicit `raid0.default_layout=1/2`, fio/readback across chunk and zone boundaries, discard verification with devices that support and do not support discard, queue-limit checks, integrity registration, and takeover tests from the supported degraded RAID4/5/10/1 configurations. Regression tests should compare known data patterns before and after reload because the most serious bugs are deterministic remapping errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid0.h -->
# sources/distributed-fs/ceph-client/drivers/md/raid0.h

## Purpose
`raid0.h` defines the private in-memory layout structures used by the MD RAID0 personality. It captures how the array is divided into strip zones for uneven component sizes and records which historical multizone layout interpretation is active.

## Important APIs, Types, And Functions
`struct strip_zone` describes one contiguous array range: `zone_end` is the array-sector end boundary, `dev_start` is the starting offset on each participating real device, `nb_dev` is the number of devices in the zone, and `disk_shift` stores the first disk position for original-layout multizone rotation. `enum r0layout` defines `RAID0_ORIG_LAYOUT` and `RAID0_ALT_MULTIZONE_LAYOUT`. `struct r0conf` owns the `strip_zone` array, the flattened `md_rdev **devlist`, the number of zones, and the selected layout.

## Control Flow
The header contains no executable control flow. `raid0.c` fills `r0conf` during `create_strip_zones()`, consults it from `find_zone()`, `map_sector()`, normal request handling, discard handling, and frees it from `raid0_free()`.

## State And Persistence
These structures are in-memory only. They are reconstructed from MD metadata and member-device sizes at array run or takeover time. The layout enum reflects an on-disk/assembly compatibility decision, but this header itself does not persist data.

## Dependencies And Integration Points
The types rely on `sector_t` and `struct md_rdev` from MD/block-layer headers included before this private header. `raid0.c` is the direct consumer, and MD core indirectly depends on these definitions through `mddev->private` for RAID0 arrays.

## Risks
The header's fields encode the mapping contract. Changing field meaning, `RAID0_ORIG_LAYOUT`/`RAID0_ALT_MULTIZONE_LAYOUT` values, or the flattened `devlist` interpretation would break compatibility with existing arrays and the mapper in `raid0.c`. `disk_shift` only matters for original multizone layout, so code using it must preserve the "first zone layouts are identical" rule.

## Test Signals
Header coverage is indirect through RAID0 build, module load, assembly of equal-size and uneven-size arrays, and mapping/discard tests that exercise zone boundaries and both layout enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid1-10.c -->
# sources/distributed-fs/ceph-client/drivers/md/raid1-10.c

## Purpose
`raid1-10.c` is a shared implementation include used by RAID1 and RAID10 personalities for common mirrored-I/O helpers. In this subset it is included by `raid1.c` after defining `RAID_1_10_NAME` as `raid1`. It provides resync page management, write submission and plug batching, bitmap-unplug ordering, read-error thresholding, bad-block read-range selection, clustered resync read policy, and a common error-handling predicate.

## Important APIs, Types, And Functions
The file defines `RESYNC_BLOCK_SIZE`, `RESYNC_PAGES`, `IO_BLOCKED`, `IO_MADE_GOOD`, `BIO_SPECIAL()`, and `MAX_PLUG_BIO`. `struct resync_pages` ties a resync bio to its allocated page array and parent raid bio. `struct raid1_plug_cb` stores plugged pending write bios. Resync helpers include `resync_alloc_pages`, `resync_free_pages`, `resync_get_all_pages`, `resync_fetch_page`, `get_resync_pages`, and `md_bio_reset_resync_pages`. Write helpers include `raid1_submit_write`, `raid1_add_bio_to_plug`, and `raid1_prepare_flush_writes`. Error/read-selection helpers include `check_decay_read_errors`, `exceed_read_errors`, `raid1_check_read_range`, `raid1_should_read_first`, and `raid1_should_handle_error`.

## Control Flow
Resync buffer allocation allocates `RESYNC_PAGES` pages per `struct resync_pages`; additional bios can share the first page set by incrementing page refs. Bio reset rebuilds the bvec table after `bio_reset()` by re-adding each page. Normal mirrored writes either submit immediately when no bitmap is enabled or enter a block plug callback so bitmap I/O can be issued before data I/O without per-bio synchronous stalls. If a plug accumulates enough bios relative to copy count, it flushes early.

Read-error handling decays per-rdev read error counters based on elapsed hours, increments the counter on new errors, and calls `md_error()` when the threshold is exceeded. Bad-block range selection returns the length of the first readable sector range, updates the requested length when the good range starts after an initial bad range, and lets RAID1 split/retry reads around bad blocks. `raid1_should_read_first()` avoids balanced reads while a resync or clustered resync window covers the request. `raid1_should_handle_error()` suppresses repair/retry side effects for readahead, nowait, and invalid-user-request failures.

## State And Persistence
The helpers manipulate in-memory bio, page, rdev, and bitmap state. Bad-block decisions integrate with each `md_rdev`'s bad-block log, which may be metadata-backed elsewhere in MD. Read-error counters and timestamps are in-memory device health state. `IO_BLOCKED` and `IO_MADE_GOOD` are sentinel bio pointer values stored in RAID1/10 per-request arrays, so callers must always guard with `BIO_SPECIAL()` or equivalent before treating a slot as a real bio.

## Dependencies And Integration Points
This file is not a standalone translation unit. It depends on the including RAID personality to define `RAID_1_10_NAME` and to provide MD, bio, bitmap, and rdev context. In `raid1.c`, its helpers feed `r1buf_pool` allocation/freeing, write request submission, pending-bio flushing, read balancing, read-error repair, sync write completion, and retry handling.

## Risks
Because it is included C rather than a normal module, symbol names and macros share the including file's namespace. The `IO_BLOCKED`/`IO_MADE_GOOD` sentinel values are intentionally invalid low pointers; any code path that forgets to treat them specially can dereference garbage. Plug/bitmap ordering avoids deadlock around `current->bio_list`, so changes to `raid1_prepare_flush_writes()` or direct submission rules can reintroduce submit recursion stalls. Resync page reference sharing is subtle: allocation, reset, and freeing must stay symmetric across all bios.

## Test Signals
Useful coverage comes from RAID1 and RAID10 resync/recovery tests, bitmap-enabled write workloads, write-mostly/write-behind tests, bad-block injection, read error threshold tests, readahead and nowait read failures, discard to devices without discard support, and lockdep/KASAN runs during resync buffer allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid1-10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid1.c -->
# sources/distributed-fs/ceph-client/drivers/md/raid1.c

## Purpose
`raid1.c` implements the Linux MD RAID1 personality: mirrored reads and writes, mirror selection, write-behind for write-mostly devices, bad-block repair, resync/recovery/check/repair, hot add/remove, resize/reshape, takeover from two-disk RAID5, and module registration. It converts one upper bio into one selected mirror read or multiple mirror writes while preserving MD metadata, bitmap, barrier, and device-failure semantics.

## Important APIs, Types, And Functions
The personality is `raid1_personality`, with callbacks for `make_request`, `run`, `free`, `status`, `error_handler`, hot add/remove, spare activation, sync requests, resize, size, reshape checking, quiesce, and takeover. The primary request entry point is `raid1_make_request()`, which dispatches to `raid1_read_request()` or `raid1_write_request()` after flush handling and barrier-unit splitting. Completion handlers are `raid1_end_read_request()`, `raid1_end_write_request()`, `end_sync_read()`, and `end_sync_write()`. The background thread `raid1d()` drains `retry_list` and `bio_end_io_list` for read repair, write-error narrowing, and sync write completion.

Key setup and management functions are `setup_conf()`, `raid1_run()`, `raid1_free()`, `raid1_add_disk()`, `raid1_remove_disk()`, `raid1_spare_active()`, `raid1_resize()`, `raid1_reshape()`, `raid1_quiesce()`, and `raid1_takeover()`. Important internal helpers include interval-tree write serialization (`check_and_add_serial`, `wait_for_serialization`, `remove_serial`), barrier controls (`raise_barrier`, `lower_barrier`, `_wait_barrier`, `wait_read_barrier`, `freeze_array`, `unfreeze_array`), mirror choice (`read_balance` and its chooser helpers), write-behind allocation (`alloc_behind_master_bio`, `raid1_start_write_behind`), and recovery (`raid1_sync_request`, `sync_request_write`, `fix_sync_read_error`, `process_checks`, `fix_read_error`, `narrow_write_error`).

## Control Flow
Normal reads first wait for the array-frozen read barrier, allocate or reuse an `r1bio`, choose a readable mirror, optionally split around bad blocks or barrier-unit limits, clone the bio to the selected rdev, and submit it. Read balancing prefers a first usable device during resync/cluster resync windows, otherwise prefers sequential continuity, low pending count on nonrotational arrays, closest head position on rotational arrays, then devices with partial bad-block-free ranges, and only finally write-mostly devices. Failed reads are either completed upward if they should not be repaired, retried on another mirror through `raid1d`, or repaired synchronously while the array is frozen.

Normal writes wait for cluster resync conflicts, wait for the write barrier, and wait for blocked rdev bad-block acknowledgement. They select every non-faulty mirror or replacement that can accept the range, split before bad blocks, mark MD write start, clone the bio per target, optionally copy data into a behind bio for bitmap-backed write-mostly devices, serialize overlapping writes when `MD_SERIALIZE_POLICY` or collision checking is active, and submit through bitmap-aware plug batching. A write completes successfully to the upper layer once at least one in-sync non-faulty target has succeeded; write-behind can acknowledge after non-write-mostly mirrors complete while background write-mostly writes continue. Write errors set `WriteErrorSeen`, request replacement, may fail fast, and are processed later to record precise bad blocks or complete the upper bio after metadata changes are safe.

The barrier state machine divides the address space into hashed 64 MiB units. Normal I/O increments `nr_pending`, waits when `barrier` or `array_frozen` blocks it, and later calls `allow_barrier`. Resync raises a barrier only when no pending normal I/O exists in that bucket, respects `RESYNC_DEPTH`, and lowers it when the resync buffer is released. `freeze_array()` globally stops normal and sync I/O for reshape, quiesce, removal, and repair by waiting until only allowed queued operations remain.

Resync/recovery starts from `raid1_sync_request()`. It initializes the resync mempool lazily, skips clean bitmap chunks unless full sync or user-requested check/repair requires work, raises the barrier, assigns read and write targets based on `In_sync`, `Faulty`, bad-block, write-mostly, and recovery flags, builds page-backed bios up to `RESYNC_BLOCK_SIZE`, updates clustered resync windows, and submits one or all reads depending on whether this is normal recovery or user-requested check/repair. Completion either writes good data to stale mirrors, compares all readable mirrors for check/repair, fixes sync read errors by trying alternate mirrors, records bad blocks, updates mismatch counters, and calls `md_done_sync()`.

## State And Persistence
The central in-memory state is `struct r1conf` from `raid1.h`: mirror slots, replacement slots, retry queues, pending writes, barrier arrays, mempools, split bioset, temporary page, resync thread, cluster resync window, and fullsync flag. Per-I/O state is `struct r1bio`, which tracks the master bio, target bios/sentinels, read disk, sector range, completion counters, and state bits such as `R1BIO_Uptodate`, `R1BIO_IsSync`, `R1BIO_BehindIO`, `R1BIO_ReadError`, `R1BIO_Returned`, `R1BIO_MadeGood`, `R1BIO_WriteError`, and `R1BIO_FailFast`.

Persistent state is managed through MD core and rdev metadata: `In_sync`, `Faulty`, `WriteErrorSeen`, `WantReplacement`, `Replacement`, bad-block logs, bitmap dirty/sync state, `mddev->degraded`, `recovery` bits, superblock change flags, array size, device size, and clustered resync messages. This file sets those flags and calls MD helpers that persist or advertise them. It does not define an independent on-disk format.

## Dependencies And Integration Points
`raid1.c` integrates deeply with MD core (`md.h`), bitmap operations (`md-bitmap.h`), cluster operations (`md-cluster.h`), block-layer bio allocation/submission/splitting, queue-limit stacking, integrity registration, interval trees for write serialization, sysfs rdev links, module registration, and trace events. It includes `raid1-10.c` for shared mirrored I/O helpers and `raid1.h` for private structures. The MD management layer invokes hotplug, reshape, recovery, and status callbacks; the block layer invokes `make_request` for all upper I/O.

## Risks
The main risks are concurrency and ordering. Barrier counters, `nr_pending`/`nr_waiting`/`nr_queued`, retry queues, `array_frozen`, and memory barriers must remain paired or resync can race normal writes. RCU-style `mirror.rdev` access is documented in the header but many paths rely on stronger contexts such as recovery or frozen arrays; changing removal paths can introduce use-after-free or NULL dereferences. Write-behind acknowledges upper bios before all physical writes complete, so bitmap ordering and collision serialization are correctness-critical. Bad-block repair and write-error narrowing intentionally do synchronous I/O while frozen; mistakes can lose the only good copy or fail the wrong rdev. Reshape reallocates mempools and repacks mirror slots under freeze, making it sensitive to pending references and sysfs link updates.

## Test Signals
Strong signals include MD selftests or blktests for RAID1 create/assemble, degraded operation, hot add/remove/replacement, bitmap resync skip, write-mostly and write-behind, forced read and write errors, bad-block injection and clearing, check/repair mismatch accounting, clustered resync windows, NOWAIT/readahead failure behavior, failfast, discard and atomic write paths, resize, raid-disk reshape, two-disk RAID5 takeover, lockdep, KASAN/KCSAN, and fault-injection for bio/mempool/page allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid1.h -->
# sources/distributed-fs/ceph-client/drivers/md/raid1.h

## Purpose
`raid1.h` defines the private data structures and constants for the MD RAID1 personality. It documents the safe access rules for mirror rdev pointers, declares barrier-bucket sizing, and defines the per-array and per-I/O state that `raid1.c` uses for mirrored I/O, recovery, write-behind, and hotplug.

## Important APIs, Types, And Functions
`BARRIER_UNIT_SECTOR_BITS` and `BARRIER_UNIT_SECTOR_SIZE` define 64 MiB barrier units. `BARRIER_BUCKETS_NR_BITS` and `BARRIER_BUCKETS_NR` size the per-bucket atomic arrays to one page. `struct raid1_info` stores one mirror or replacement `md_rdev`, current head position, and sequential-read tracking fields. `struct r1conf` is the per-array configuration: MD device pointer, mirror array sized at `raid_disks * 2`, disk counts, locks, retry lists, pending write list, barrier waitqueue and counters, fullsync flag, r1bio/resync mempools, split bioset, temporary repair page, private thread pointer, and cluster sync window. `struct r1bio` is the variable-sized per-request object with completion counters, sector range, state bits, master bio, selected read disk, retry linkage, optional behind bio, and flexible array of target bios. `enum r1bio_state` names the per-I/O state bits. `sector_to_idx()` hashes a sector's barrier unit to a barrier bucket.

## Control Flow
The header itself only defines structures and the inline `sector_to_idx()`. Its comments define the concurrency contract for `raid1_info.rdev`: safe access requires `mddev->reconfig_mutex`, known recovery/resync context, or RCU plus an `nr_pending` reference. `raid1.c` follows this contract in setup, removal, request submission, recovery, and frozen-array sections.

## State And Persistence
All types are in-memory. They mirror persistent MD concepts such as degraded count, replacement devices, bad blocks, bitmap-backed write-behind, recovery windows, and in-sync/faulty rdev flags, but the actual persistence is owned by MD metadata and bitmap code. The flexible `r1bio->bios[]` array is allocated with room for originals plus replacements and can contain real bios or sentinel values from the shared RAID1/10 helper include.

## Dependencies And Integration Points
The header depends on MD/block-layer types such as `struct mddev`, `struct md_rdev`, `mempool_t`, `struct bio_set`, `struct bio`, `sector_t`, atomic counters, locks, lists, pages, wait queues, and `hash_long()`. It is directly included by `raid1.c`; MD core indirectly interacts with `r1conf` through `mddev->private`.

## Risks
The "do not put fields after bios[]" rule on `struct r1bio` is critical because the flexible array is allocated contiguously with the object. Barrier bucket sizing assumes `atomic_t` width and page size; changing these constants affects memory use and lock granularity. Misusing `sector_to_idx()` or the rdev pointer access rules can create barrier collisions, missed wakeups, or lifetime bugs. The mirror array stores replacements after the primary `raid_disks` slots, so index math must consistently use `raid_disks * 2`.

## Test Signals
Header behavior is covered indirectly by RAID1 build and all normal I/O, resync, hotplug, replacement, reshape, and quiesce tests. Debug builds with lockdep/KCSAN/KASAN are especially useful for validating the documented rdev access and flexible-array lifetime assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid1.h -->
