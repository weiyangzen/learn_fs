# subset-b-004027 Research

Grouped research for device-mapper request, snapshot, statistics, striped, switch, sysfs, table, and target registry sources. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-rq.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-rq.c

## Purpose
Implements request-based Device Mapper support on top of blk-mq. The file owns the per-request `dm_rq_target_io` state, maps an original request through a single request-capable target, prepares cloned requests, handles partial bio completion, requeue behavior, request statistics, and blk-mq queue setup for request-based mapped devices.

## Important APIs, Types, And Functions
`struct dm_rq_target_io` is allocated as request private data and carries the mapped device, selected target, original and cloned request pointers, `union map_info`, stats auxiliary data, partial completion accounting, and target-private per-IO storage when requested. Module parameters control reserved request-based IOs, blk-mq hardware queues, and queue depth through `dm_get_reserved_rq_based_ios()`, `dm_get_blk_mq_nr_hw_queues()`, and `dm_get_blk_mq_queue_depth()`.

The main blk-mq callbacks are `dm_mq_init_request()`, `dm_mq_queue_rq()`, and `dm_softirq_done()` through `dm_mq_ops`. `map_request()` delegates target mapping to `ti->type->clone_and_map_rq()` and interprets `DM_MAPIO_SUBMITTED`, `DM_MAPIO_REMAPPED`, `DM_MAPIO_REQUEUE`, `DM_MAPIO_DELAY_REQUEUE`, and `DM_MAPIO_KILL`. `setup_clone()` wraps `blk_rq_prep_clone()` and installs `end_clone_request()` plus per-clone bio constructors. `dm_done()`, `dm_end_request()`, `dm_requeue_original_request()`, and `dm_kill_unmapped_request()` translate target completion policy into blk-mq completion or requeue.

## Control Flow
Queueing starts in `dm_mq_queue_rq()`. It rejects requests while suspend blocks IO, resolves the immutable target or the first target from the live table, checks target `busy()`, starts the request, initializes `dm_rq_target_io`, and calls `map_request()`. Remapped requests are cloned, traced with `trace_block_rq_remap()`, and inserted using `blk_insert_cloned_request()`. Resource failures unwind clone preparation and return `BLK_STS_RESOURCE` so blk-mq requeues the original request.

Completion flows from the clone `end_io` to `dm_complete_request()` on the original request, then through blk-mq `.complete` into `dm_softirq_done()`. If there is no clone, the original request is completed directly. Otherwise `dm_done()` calls an optional target `rq_end_io()` and obeys its decision to complete, leave incomplete, requeue immediately, or requeue after delay. Clone bios use `end_clone_bio()` for partial completion so upper layers can observe completed bytes without ending the original request before the clone has fully finished.

## State And Persistence
All durable state is in the mapped device, blk-mq tag set, request queue, and target callbacks. The file maintains no persistent on-disk state. Runtime state includes module parameters, the per-request `dm_rq_target_io`, request clone lifetime, and an md reference held between `dm_start_request()` and `rq_completed()` to keep the mapped device alive during in-flight IO.

## Dependencies And Integration Points
Depends on `dm-core.h`, `dm-rq.h`, blk-mq, target-type request callbacks, DM table lookup, DM mempools, and DM statistics. It integrates with sysfs via the legacy `rq_based_seq_io_merge_deadline` show/store stubs and with request-based targets through `clone_and_map_rq`, `release_clone_rq`, `rq_end_io`, `busy`, `per_io_data_size`, and immutable table selection.

## Risks
Completion ordering is fragile: original requests must not be ended before clone bios and clone request cleanup are complete. Requeue paths must undo stats and md references exactly once. Request-based DM only supports single immutable targets at the table layer, so target mixing or request splitting assumptions can break. Incorrect handling of `BLK_STS_RESOURCE` or target-specific `rq_end_io()` return values risks IO loss, endless requeue, or double completion.

## Test Signals
Build with request-based DM targets such as multipath. Exercise suspend/resume while IO is queued, target `busy()` resource pressure, request requeue and delayed requeue, discard/write-zeroes target failure paths that disable unsupported limits, and DM statistics on request-based devices. KASAN/KCSAN and blk-mq debug signals should show no double free, leaked md references, or request completion imbalance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-rq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-rq.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-rq.h

## Purpose
Provides the internal request-based Device Mapper interface used by `dm-rq.c`, `dm-table.c`, and sysfs. It declares request-queue setup and cleanup hooks, queue control helpers, reserved IO accounting, and the front-padded clone-bio metadata used for request-based request cloning.

## Important APIs, Types, And Functions
`struct dm_rq_clone_bio_info` embeds a cloned `struct bio` after metadata that points to the original bio and the request's `dm_rq_target_io`. The structure is designed for bioset front-pad allocation so request clone bios can be recovered with `container_of()` in `end_clone_bio()`.

The header declares `dm_mq_init_request_queue()` and `dm_mq_cleanup_mapped_device()` for tag-set lifecycle, `dm_start_queue()` and `dm_stop_queue()` for blk-mq quiesce control, `dm_mq_kick_requeue_list()` for requeue wakeups, `dm_get_reserved_rq_based_ios()` for mempool sizing, and the compatibility sysfs handlers for `rq_based_seq_io_merge_deadline`.

## Control Flow
The header itself has no executable flow, but it defines the contracts used when a mapped device is completed as request-based. `dm_table_alloc_md_mempools()` uses `dm_get_reserved_rq_based_ios()` and the clone-bio front-pad layout. `dm_mq_init_request_queue()` installs blk-mq ops on the mapped device queue, and suspend/resume or queue management paths call `dm_stop_queue()`, `dm_start_queue()`, and `dm_mq_kick_requeue_list()`.

## State And Persistence
No state is stored in this header. It exposes state-bearing types allocated per cloned bio and per mapped device by implementation files. There is no on-disk persistence.

## Dependencies And Integration Points
Includes Linux bio and kthread headers, `dm-stats.h`, and a forward declaration for `struct mapped_device`. It is consumed by request-based DM core code, table mempool sizing, and sysfs attribute glue.

## Risks
The placement of `struct bio clone` at the end of `dm_rq_clone_bio_info` is part of the bioset allocation contract; changing it without updating front-pad calculations would corrupt clone metadata. The header also exposes compatibility sysfs symbols that userspace may still read even though the merge-deadline heuristic is deprecated.

## Test Signals
Compile all request-based DM code with `CONFIG_BLK_DEV_DM` and request-based targets enabled. Runtime coverage should include cloned requests with multiple bios, sysfs reads and writes of `rq_based_seq_io_merge_deadline`, queue quiesce/unquiesce, and mempool allocation under request-based table load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-rq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-snap-persistent.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-snap-persistent.c

## Purpose
Implements the persistent snapshot exception store for Device Mapper snapshots. It records copy-on-write exceptions on the COW device so a snapshot can survive reboot, supports snapshot merge metadata removal, tracks COW allocation usage, and registers both the long name `persistent` and compatibility name `P`.

## Important APIs, Types, And Functions
On-disk metadata uses `struct disk_header` with magic `SNAP_MAGIC`, validity, version, and chunk size, followed by `struct disk_exception` entries storing old and new chunks in little-endian format. In-memory `struct pstore` tracks the exception store, version, valid flag, metadata area buffers, current metadata area, `next_free`, current committed entry, pending commit count, callback array, a `dm_io_client`, and `metadata_wq`.

Key operations are exposed through `struct dm_exception_store_type`: `persistent_ctr()`, `persistent_dtr()`, `persistent_read_metadata()`, `persistent_prepare_exception()`, `persistent_commit_exception()`, `persistent_prepare_merge()`, `persistent_commit_merge()`, `persistent_drop_snapshot()`, `persistent_usage()`, and `persistent_status()`. Helpers include `read_header()`, `write_header()`, `read_exceptions()`, `insert_exceptions()`, `area_io()`, and `zero_disk_area()`.

## Control Flow
Construction allocates a `pstore`, initializes validity and the first free chunk after the header and first metadata area, creates a metadata workqueue, and optionally accepts the `O` overflow-support option. `persistent_read_metadata()` reads the header, chooses or corrects chunk size, allocates metadata buffers, writes a header for a new snapshot, or loads existing exception areas with dm-bufio prefetch until an entry with `new_chunk == 0` terminates the list.

During copy-on-write, `persistent_prepare_exception()` checks COW capacity, assigns `e->new_chunk` from `next_free`, skips metadata chunks, and increments `pending_count`. `persistent_commit_exception()` writes the exception into the in-memory metadata area, records the completion callback, waits until either pending exceptions drain or the area fills, clears the next area if needed, writes the current metadata area with preflush/FUA/sync, advances to the next area, and invokes all batched callbacks with the final valid state.

Merge flows backwards. `persistent_prepare_merge()` returns the last committed old/new chunk and a run length of consecutive chunks in reverse order. `persistent_commit_merge()` clears those exception entries, writes metadata with preflush/FUA, decrements `current_committed`, and updates `next_free` for status reporting.

## State And Persistence
This file is explicitly persistent. The COW device stores a header at chunk 0 and metadata areas separated by data chunks. All metadata is little-endian and versioned with no compatibility support beyond version 1. The `valid` flag is written to disk by `persistent_drop_snapshot()` and is also cleared when metadata IO fails during commit, making invalid snapshots unrecoverable by design.

## Dependencies And Integration Points
Depends on `dm-exception-store.h`, DM snapshot accessors `dm_snap_cow()`, dm-io for synchronous block IO, dm-bufio for metadata read-ahead, vmalloc/kvcalloc allocation helpers, and the snapshot target's exception-store registration framework. It is consumed by `dm-snap.c` through the exception store method table.

## Risks
Metadata ordering and validity are critical. A failed zero of the next metadata area or failed FUA metadata write invalidates the snapshot. Out-of-order COW commits can leave holes, so `next_free` is conservative and status-only in merge mode. Header chunk-size overrides must reallocate buffers correctly. The callback array is sized to one metadata area and assumes commits are serialized through snapshot metadata paths.

## Test Signals
Exercise creation with explicit and default chunk sizes, reboot or reload of a persistent snapshot, COW exhaustion with and without userspace overflow support, metadata read corruption, FUA write failures, and snapshot-merge completion. Verify `dmsetup status` sectors allocated, metadata sectors, invalid/overflow states, and compatibility table output for both `P` and `PO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-snap-persistent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-snap-transient.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-snap-transient.c

## Purpose
Implements the non-persistent Device Mapper snapshot exception store. It allocates COW chunks linearly in memory-only state, performs no metadata IO, and registers both `transient` and compatibility name `N`.

## Important APIs, Types, And Functions
`struct transient_c` contains only `next_free`, the next free COW sector. The store method table supplies `transient_ctr()`, `transient_dtr()`, `transient_read_metadata()`, `transient_prepare_exception()`, `transient_commit_exception()`, `transient_usage()`, and `transient_status()`. There are no merge methods, so this store cannot back snapshot-merge.

## Control Flow
Construction allocates `transient_c`, initializes `next_free` to zero, and stores it in `store->context`. Metadata read returns success without loading any exceptions. Preparing an exception checks that the COW device has at least one chunk available, converts `next_free` to a chunk number for `e->new_chunk`, and advances `next_free` by `store->chunk_size`. Commit immediately invokes the supplied callback with the provided validity result.

## State And Persistence
All state is volatile. Exceptions disappear when the target is destroyed or the system reboots. `transient_usage()` reports allocated sectors from `next_free`, total sectors from the COW device, and zero metadata sectors. There is no on-disk valid bit and no recovery path.

## Dependencies And Integration Points
Depends on `dm-exception-store.h`, `dm_snap_cow()`, and the snapshot exception store registry. It integrates with `dm-snap.c` exactly like the persistent store for normal copy-on-write allocation, but omits merge and disk metadata hooks.

## Risks
Because `transient_prepare_exception()` returns `-1` on COW exhaustion rather than a conventional errno, callers must treat any nonzero return as allocation failure. The store cannot support crash recovery or snapshot-merge. Capacity accounting is sector-based and assumes chunk-size increments remain aligned with the snapshot store setup.

## Test Signals
Create `snapshot` targets with `N` and `transient`, perform writes through the snapshot and origin, verify status reports allocated COW sectors and zero metadata sectors, and confirm reload after teardown does not preserve exceptions. Attempt snapshot-merge with a transient store should be rejected by `dm-snap.c` because merge methods are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-snap-transient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-snap.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-snap.c

## Purpose
Implements the Device Mapper snapshot, snapshot-origin, and snapshot-merge targets. It maintains exception tables that map origin chunks to COW chunks, coordinates copy-on-write through dm-kcopyd, tracks origin writes across all snapshots sharing an origin, handles snapshot metadata handover during table reload, and performs online merging of COW data back to the origin.

## Important APIs, Types, And Functions
`struct dm_snapshot` is the central state object. It holds origin and COW devices, target pointer, validity and overflow flags, active state, pending exception counts and sequencing, completed and pending exception hash tables, per-snapshot locks, tracked read chunks, exception store pointer, kcopyd client, merge state, and bios queued during merge. `struct dm_snap_pending_exception` represents an in-flight COW exception with waiting origin and snapshot bios, sequencing, copy error state, optional full-bio shortcut, and RB-tree linkage for out-of-order kcopyd completions.

The file registers three targets: `snapshot`, `snapshot-origin`, and `snapshot-merge`. Important functions include `snapshot_ctr()`, `snapshot_dtr()`, `snapshot_map()`, `snapshot_merge_map()`, `snapshot_resume()`, `snapshot_merge_resume()`, `snapshot_status()`, `origin_ctr()`, `origin_map()`, `origin_resume()`, `origin_postsuspend()`, `do_origin()`, `__origin_write()`, `pending_complete()`, `start_copy()`, `copy_callback()`, `start_merge()`, and `snapshot_merge_next_chunks()`.

## Control Flow
Snapshot construction opens origin and COW devices, creates the configured exception store, initializes exception hash tables, kcopyd client, pending exception mempool, tracked chunk hash, and registers the snapshot under its origin. If this target is a handover destination, metadata loading is deferred; otherwise the store reads metadata and calls `dm_add_exception()` for each completed exception.

Normal snapshot mapping first handles flushes to the COW device. Reads without exceptions map to origin and are tracked so merge and pending completion do not overwrite chunks being read. Reads or writes with completed exceptions remap to the COW chunk. Writes to unallocated chunks allocate or find a pending exception, remap to its new COW chunk, queue the bio behind the exception, and start either a full-bio shortcut or a kcopyd copy from origin to COW. Completion commits metadata through the store, installs the completed exception, releases queued snapshot bios, retries origin bios, and frees pending state.

Origin writes enter `origin_map()` and `do_origin()`. They are split to the minimum snapshot chunk size and `__origin_write()` walks all active non-merging snapshots on that origin. For each snapshot, it creates pending exceptions for chunks not already copied and queues the origin write until necessary COW copies finish.

Snapshot merge uses snapshot mapping plus origin behavior. `snapshot_merge_next_chunks()` asks the persistent store for the next reverse run of exceptions, ensures overlapping chunks are reallocated into other snapshots, waits for pending exceptions and conflicting IO, copies COW data back to origin, flushes, commits metadata removal, removes in-memory exceptions, and repeats until complete or failed.

## State And Persistence
In-memory state includes origin hash tables, DM-origin registrations, exception caches, pending exception mempools, completed and pending exception tables, sequence counters, and merge flags. Persistent state is delegated to the selected exception store. Persistent snapshots survive reload through disk metadata; transient snapshots do not. Handover swaps exception tables and stores between old and new targets sharing the same COW device so metadata is not loaded concurrently.

## Dependencies And Integration Points
Depends on DM target registration, `dm-exception-store`, dm-kcopyd, block bio splitting and remapping, DM table events, target suspend/resume callbacks, module parameters for COW threshold and kcopyd throttling, and per-bio data. It exports `dm_snap_origin()` and `dm_snap_cow()` for exception stores. It integrates with `dm-snap-persistent.c` and `dm-snap-transient.c` through the exception-store API.

## Risks
The highest risks are concurrency and ordering. Pending exceptions must complete in allocation order for metadata consistency even if kcopyd finishes out of order. Tracked reads must drain before a completed exception or merge overwrites data visibility. Origin writes must create exceptions in every active snapshot before the origin write is released. Handover requires the old snapshot to be suspended. Merge failure handling must stop safely and resume normal IO without corrupting origin or COW metadata.

## Test Signals
Run snapshot create/read/write/origin-write tests with persistent and transient stores, COW overflow tests, discard feature tests for `discard_zeroes_cow` and `discard_passdown_origin`, suspend/resume handover reloads, concurrent origin and snapshot IO under kcopyd load, and snapshot-merge with multiple snapshots on the same origin. Status should report valid, invalid, overflow, and merge failed states correctly, and debug builds should not leave tracked chunks or pending exceptions on destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-snap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-stats.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-stats.c

## Purpose
Implements Device Mapper statistics regions and message commands. It lets userspace create sector ranges divided into entries, account read/write IO counts, sectors, merges, service time, in-flight time, queue time, optional precise nanosecond timestamps, and optional latency histograms.

## Important APIs, Types, And Functions
`struct dm_stat` describes one statistics region: id, range, step, flags, histogram boundaries, program and auxiliary strings, allocation sizes, per-CPU counters, and one shared entry per region bucket. `struct dm_stat_percpu` contains counters for sectors, ios, merges, ticks, io_ticks, time in queue, and histogram buckets. `struct dm_stat_shared` contains in-flight atomics and temporary totals used for print and clear.

External entry points are `dm_stats_init()`, `dm_stats_cleanup()`, `dm_stats_account_io()`, `dm_stats_message()`, `dm_statistics_init()`, and `dm_statistics_exit()`. Message handlers implement `@stats_create`, `@stats_delete`, `@stats_clear`, `@stats_list`, `@stats_print`, `@stats_print_clear`, and `@stats_set_aux`.

## Control Flow
`dm_stats_init()` initializes the mutex, list, precise timestamp flag, and per-CPU last-position tracking. `message_stats_create()` parses a range, fixed step or divisor, optional feature arguments, program id, and aux data. `dm_stats_create()` validates overflow and memory limits, allocates shared and per-CPU arrays, optionally allocates histogram arrays, suspends and resumes the mapped device around insertion so the new region starts exact, assigns the first available id, and enables the global stats static key.

IO accounting enters `dm_stats_account_io()` at start and end of IO. Start updates per-CPU merge detection and, if needed, stores precise start time in `dm_stats_aux`. Both start and end walk active regions under RCU and call `__dm_stat_bio()`, which splits the IO across region entries and updates each entry through `dm_stat_for_entry()`. End accounting decrements in-flight counters, increments IO and sector totals, records merges, accumulates duration, and places duration into the histogram bucket using binary search.

Print and clear paths aggregate per-CPU counters into each shared temporary entry with `__dm_stat_init_temporary_percpu_totals()`. `dm_stats_print()` emits one line per requested entry and optionally subtracts the temporary totals from current per-CPU counters to implement clear-after-print.

## State And Persistence
Statistics are volatile kernel state tied to `struct dm_stats` in the mapped device. Region definitions, counters, histograms, program ids, and aux data disappear when deleted or when the mapped device is destroyed. The file maintains global memory accounting in `shared_memory_amount` and limits stats allocations to fractions of RAM and vmalloc space. Deletes use RCU, with synchronous freeing for vmalloc-backed allocations and `rcu_barrier()` at module exit if needed.

## Dependencies And Integration Points
Depends on DM core message dispatch, internal suspend/resume callbacks, RCU lists, per-CPU memory, static keys, jiffies and ktime, NUMA-aware allocation, and block read/write direction constants. `dm-rq.c` and bio-based DM core call `dm_stats_account_io()`, while `dm-stats.h` exposes the API and inline start timestamp helper.

## Risks
Memory use can be very large for many entries and histograms, so overflow checks and shared memory accounting are important. Counter updates are intentionally racy on 64-bit and lock-protected on 32-bit; changing locking could hurt performance or correctness. Precise timestamp mode changes global per-device accounting behavior. Deletion must honor RCU readers and vmalloc restrictions. Message parsing accepts complex optional forms, making boundary, histogram monotonicity, and buffer overflow tests important.

## Test Signals
Use `dmsetup message` to create, list, print, clear, print-clear, delete, set aux data, and filter by program id. Exercise whole-device ranges, divided ranges, precise timestamps, histograms, invalid parameters, very large allocation rejection, concurrent IO during stats accounting, and deletion while IO is active. Verify `stats_current_allocated_bytes` returns to zero after cleanup and that in-flight leak warnings do not appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-stats.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-stats.h

## Purpose
Defines the internal Device Mapper statistics API and lightweight state embedded in mapped devices and per-IO contexts. It is the shared contract between DM core/request paths and `dm-stats.c`.

## Important APIs, Types, And Functions
`struct dm_stats` owns the stats mutex, RCU-protected region list, per-CPU last-position array for merge detection, and the `precise_timestamps` flag. `struct dm_stats_aux` is per-IO auxiliary state containing the detected merge flag and nanosecond duration field used when precise timestamps are enabled.

The header declares lifecycle functions `dm_statistics_init()`, `dm_statistics_exit()`, `dm_stats_init()`, and `dm_stats_cleanup()`, message dispatch through `dm_stats_message()`, and IO accounting through `dm_stats_account_io()`. Inline helpers `dm_stats_used()` and `dm_stats_record_start()` let hot IO paths cheaply test whether stats exist and record precise start timestamps only when needed.

## Control Flow
DM core initializes `struct dm_stats` when a mapped device is created, calls `dm_stats_record_start()` for precise timestamp capable IO setup, accounts start and end events through `dm_stats_account_io()`, and routes `@stats_*` target messages to `dm_stats_message()`.

## State And Persistence
The header defines volatile in-kernel structures only. No counters or region definitions persist beyond mapped-device lifetime.

## Dependencies And Integration Points
Depends on Linux types, mutexes, lists, and a forward declaration of `struct mapped_device`. It is included by `dm-core` users and `dm-rq.h` so both bio-based and request-based IO can share statistics accounting.

## Risks
`dm_stats_used()` is a lockless list-empty test for hot paths; callers rely on the RCU/list discipline in `dm-stats.c`. `dm_stats_record_start()` writes `duration_ns` only when precise timestamps are active, so callers must pass the same aux object to IO completion accounting.

## Test Signals
Compile coverage should include both request-based and bio-based DM. Runtime stats tests should confirm IO paths call start and end accounting with the same `dm_stats_aux`, especially when precise timestamps are toggled by adding and removing stats regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-stripe.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-stripe.c

## Purpose
Implements the `striped` Device Mapper target. It maps logical sectors across multiple underlying devices in fixed-size chunks, supports flush/discard/secure-erase/write-zeroes fan-out, reports per-stripe error state, and exposes DAX operations when enabled.

## Important APIs, Types, And Functions
`struct stripe` stores one device, physical start sector, and an atomic error count. `struct stripe_c` stores stripe count, power-of-two shift optimizations, per-stripe width, chunk size, target pointer, event work, and the flexible stripe array.

Important functions include `stripe_ctr()`, `stripe_dtr()`, `stripe_map()`, `stripe_map_sector()`, `stripe_map_range()`, `stripe_status()`, `stripe_end_io()`, `stripe_iterate_devices()`, `stripe_io_hints()`, and optional DAX methods `stripe_dax_direct_access()`, `stripe_dax_zero_page_range()`, and `stripe_dax_recovery_write()`.

## Control Flow
Construction parses `<number of stripes> <chunk size> [<dev_path> <offset>]+`, validates divisibility of target length by stripe count and chunk size, opens each device, sets `max_io_len` to chunk size, configures the number of flush/discard/secure-erase/write-zeroes bios to the stripe count, and records whether stripe and chunk counts are powers of two for faster mapping.

Normal mapping computes the logical target offset, chunk offset, stripe number, and per-device sector. Flush bios are dispatched by target bio number to each stripe. Discard, secure erase, and write zeroes use `stripe_map_range()` to emit only the part of the request range that belongs to the selected stripe. End-IO increments per-device error counters and queues a table event until `DM_IO_ERROR_THRESHOLD` is reached.

## State And Persistence
State is in-memory target configuration and error counters. There is no on-disk metadata. Error counters affect status output and event generation but do not remove devices or remap around failures.

## Dependencies And Integration Points
Depends on DM target APIs, block bio remapping, DAX, queue-limit hints, workqueues, and target registration through `dm_stripe_init()` and `dm_stripe_exit()`. It integrates with table queue-limit stacking through `iterate_devices()` and `io_hints()`.

## Risks
Mapping arithmetic must be correct for both power-of-two and non-power-of-two chunk and stripe counts. Range operations for discard/write-zeroes must not submit sectors that belong to another stripe. Error event work must be flushed on destruction. DAX mapping assumes the selected underlying device has a usable `dax_dev`.

## Test Signals
Create striped devices with power-of-two and non-power-of-two stripe counts and chunk sizes, run read/write verification across stripe boundaries, issue flush/discard/secure-erase/write-zeroes, inspect status error flags after injected IO errors, and test DAX paths when configured. Queue-limit checks should show expected `io_min`, `io_opt`, `chunk_sectors`, and discard bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-stripe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-switch.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-switch.c

## Purpose
Implements the `switch` Device Mapper target for efficiently mapping many fixed-size logical regions to one of many paths when the mapping has no compact linear or striped pattern. It supports runtime region remapping through target messages.

## Important APIs, Types, And Functions
`struct switch_path` stores an underlying `dm_dev` and start sector. `struct switch_ctx` stores target pointer, number of paths, region size, number of regions, bit-shift optimizations, packed region-table geometry, the vmalloc-backed region table, and a flexible path array.

Key functions are `switch_ctr()`, `switch_dtr()`, `switch_map()`, `process_set_region_mappings()`, `switch_message()`, `switch_status()`, `switch_prepare_ioctl()`, and `switch_iterate_devices()`. Region table helpers pack and unpack path numbers into `region_table_slot_t` slots.

## Control Flow
Construction parses `<num_paths> <region_size> <num_optional_args> [dev offset]+`, currently requires zero optional args, opens each path, sets target max IO length to the region size, allocates a packed region table sized to the target length, initializes mappings round-robin, and declares a single discard bio because any path is sufficient for UNMAP.

Mapping computes the target offset, divides by region size to find a region, reads the packed path number, falls back to path 0 if a torn non-atomic read yields an invalid value, and remaps the bio to `path.start + offset`. Runtime messages are serialized by a static mutex. The only supported message, `set_region_mappings`, parses compact hexadecimal assignments and repeat commands (`R<cycle>,<count>`) to update region table entries.

## State And Persistence
All mapping state is volatile in the vmalloc-backed region table. There is no on-disk metadata and no automatic persistence of runtime remapping messages. Region table writes update memory in place and readers use `READ_ONCE()`, but there is no full transactional update across multiple region changes.

## Dependencies And Integration Points
Depends on DM target APIs, message dispatch, vmalloc, packed bit manipulation, and device iteration. It registers through `module_dm(switch)`. `prepare_ioctl()` forwards ioctls to the path used for sector 0 only when that underlying device size exactly matches the mapped range.

## Risks
Packed region-table updates can be observed concurrently by IO mapping, so invalid path fallback exists for architectures without atomic slot stores. Message parsing is performance-oriented and strict; malformed hex or repeat syntax must fail without partial invalid writes beyond already-applied earlier entries. The region table can be large, so overflow checks around regions, slots, and allocation size are important.

## Test Signals
Create switch targets with multiple paths and region sizes, verify initial round-robin mapping, apply `set_region_mappings` messages with explicit and repeat syntax, test invalid message rejection, and run concurrent IO while mappings change. Validate discard behavior, ioctl forwarding for full-device mappings, and table/status output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-sysfs.c

## Purpose
Provides the sysfs kobject and attributes under each mapped device's disk device. It exposes mapped-device name, UUID, suspended state, blk-mq compatibility state, and the deprecated request-based merge deadline attribute.

## Important APIs, Types, And Functions
`struct dm_sysfs_attr` wraps a sysfs `attribute` with show and store callbacks that receive `struct mapped_device *`. Macros `DM_ATTR_RO` and `DM_ATTR_RW` define attributes. Concrete attributes are `name`, `uuid`, `suspended`, `use_blk_mq`, and `rq_based_seq_io_merge_deadline`.

The public functions are `dm_sysfs_init()` and `dm_sysfs_exit()`. Internal dispatchers `dm_attr_show()` and `dm_attr_store()` recover the mapped device with `dm_get_from_kobject()`, call the attribute callback, and drop the reference.

## Control Flow
Mapped-device setup calls `dm_sysfs_init()`, which initializes and adds the `dm` kobject as a child of the disk device kobject with `dm_ktype`. Sysfs reads and writes are routed through `dm_sysfs_ops`; missing methods return `-EIO`. Teardown calls `dm_sysfs_exit()`, drops the kobject reference, and waits for the mapped-device kobject completion to ensure release has finished.

## State And Persistence
The file stores no persistent state. It exposes live mapped-device state copied through DM core helpers. `use_blk_mq` always reports true for userspace compatibility, and `rq_based_seq_io_merge_deadline` delegates to stubs in `dm-rq.c`.

## Dependencies And Integration Points
Depends on Linux sysfs, DM ioctl naming, `dm-core.h`, and `dm-rq.h`. It integrates with mapped-device reference counting through `dm_get_from_kobject()`, `dm_put()`, `dm_kobject_release()`, and completion signaling.

## Risks
Kobject lifetime and mapped-device references must be balanced to avoid use-after-free during sysfs access or teardown. Name and UUID copying can fail and must return `-EIO`. Compatibility attributes should not be removed casually because old userspace may still probe them.

## Test Signals
Create and remove mapped devices while reading sysfs attributes in parallel. Verify `/sys/block/dm-X/dm/name`, `uuid`, `suspended`, `use_blk_mq`, and `rq_based_seq_io_merge_deadline` outputs. Exercise suspend/resume and teardown races under KASAN or refcount debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-table.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-table.c

## Purpose
Implements Device Mapper table construction, target parsing, table indexing, underlying device reference management, table type selection, mempool allocation, queue-limit calculation, inline encryption capability aggregation, target suspend/resume callbacks, and target lookup by sector.

## Important APIs, Types, And Functions
Table creation and destruction are handled by `dm_table_create()` and `dm_table_destroy()`. Target loading flows through `dm_table_add_target()`, `dm_split_args()`, `dm_read_arg()`, `dm_read_arg_group()`, `dm_shift_arg()`, and `dm_consume_args()`. Device references are managed by `dm_get_device()`, `dm_put_device()`, `dm_devt_from_path()`, and helpers that share or upgrade table device opens.

Lookup uses a compact btree over target high sectors built by `dm_table_build_index()`, `setup_indexes()`, and `setup_btree_index()`, then searched by `dm_table_find_target()`. Queue mode and resources are decided by `dm_table_determine_type()`, `dm_table_alloc_md_mempools()`, and `dm_table_complete()`. Queue limits and feature restrictions are handled by `dm_calculate_queue_limits()` and `dm_table_set_restrictions()`.

When inline encryption is enabled, `dm_table_construct_crypto_profile()` intersects child crypto capabilities, installs key eviction and wrapped-key forwarding operations, prevents loading tables with fewer capabilities than the live queue, and later transfers capabilities with `dm_update_crypto_profile()`.

## Control Flow
A control-plane table load creates an empty table, adds contiguous nonzero targets one by one, resolves target modules, splits constructor arguments, calls each target `ctr`, records target high sectors, and rejects singleton, immutable, writeability, gap, and target-mixing violations. Completion determines bio-based, DAX bio-based, or request-based mode, builds the btree index, constructs a crypto profile, and allocates mapped-device mempools sized for the table type and target requirements.

When a table becomes live, `dm_calculate_queue_limits()` stacks limits from each target's devices, applies target IO hints, validates mapped device areas, checks zoned-device consistency, and validates logical block alignment across target boundaries. `dm_table_set_restrictions()` disables unsupported nowait, poll, discard, write-zeroes, secure-erase, DAX, zoned, and atomic-write features, commits queue limits, revalidates zones, updates DAX flags, and installs crypto capabilities.

Runtime lookup calls `dm_table_find_target()` to walk the btree from root to leaf and return the target covering a sector. Suspend and resume paths call `dm_table_presuspend_targets()`, `dm_table_presuspend_undo_targets()`, `dm_table_postsuspend_targets()`, and `dm_table_resume_targets()` to invoke target lifecycle hooks under the mapped-device suspend lock.

## State And Persistence
Tables are in-memory control-plane objects. They own target arrays, high-sector arrays, btree index nodes, a list of underlying devices with refcounts, mempools, event callbacks, queue-mode type, integrity support flag, and transient crypto profile. They do not persist on disk; userspace reloads tables as needed.

## Dependencies And Integration Points
Depends on DM core, request-based DM, target registry, blkdev queue limits, blk-integrity, zoned block support, DAX, blk-mq, block crypto, path lookup, and mapped-device table-device helpers. Every DM target integrates here through `target_type` callbacks such as `ctr`, `dtr`, `iterate_devices`, `io_hints`, `preresume`, `resume`, `presuspend`, and `postsuspend`.

## Risks
This file sits on many cross-subsystem contracts. Incorrect table type selection can allow unsupported request-based target mixes or reject valid hybrid tables. Queue-limit stacking must preserve block alignment, zoned constraints, integrity, atomic writes, and discard/write-zeroes semantics. Device reference upgrades must not race with existing users. Inline encryption capability shrinkage is explicitly rejected because the block layer cannot safely remove capabilities from an existing queue.

## Test Signals
Load tables with contiguous and gapped targets, singleton and immutable targets, request-based and bio-based targets, partitions and non-mq devices, DAX-capable and non-DAX devices, zoned devices, integrity-enabled devices, and inline encryption profiles. Verify table lookup across target boundaries, queue limits after reload, suspend/resume target callback ordering, mempool sizing, and cleanup warnings for missing `dm_put_device()` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-target.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-target.c

## Purpose
Implements the Device Mapper target type registry and the built-in `error` target. The registry lets target modules register by name, be autoloaded through `request_module("dm-%s")`, and be looked up by table construction code with module references held.

## Important APIs, Types, And Functions
The global registry is `_targets`, protected by `_lock`. Public registry functions are `dm_get_target_type()`, `dm_put_target_type()`, `dm_target_iterate()`, `dm_register_target()`, and `dm_unregister_target()`. `get_target_type()` does lookup and `try_module_get()`, while `load_module()` requests a missing target module.

The built-in error target uses `struct io_err_c` when optional backing-device arguments are supplied. It provides `io_err_ctr()`, `io_err_dtr()`, `io_err_map()`, `io_err_clone_and_map_rq()`, `io_err_iterate_devices()`, `io_err_io_hints()`, optional zoned `io_err_report_zones()`, and DAX `io_err_dax_direct_access()`.

## Control Flow
Table loading calls `dm_get_target_type()`. If no registered target matches, the registry attempts module autoload and looks up again. Successful lookup returns a target type with its module reference held until `dm_put_target_type()`. Target modules call `dm_register_target()` and `dm_unregister_target()` under the write lock.

The error target constructor accepts zero arguments or a backing `<dev> <sector>` pair. It always maps bios and request clones to `DM_MAPIO_KILL`, advertises discard support so discards fail as IO errors rather than unsupported operations, and can report zones or iterate the backing device when one was supplied.

## State And Persistence
The target registry is in-memory global kernel state. Registered target types persist until their modules unregister. The error target has per-target optional backing-device state only. There is no on-disk persistence.

## Dependencies And Integration Points
Depends on module reference APIs, kmod autoloading, DM core, block bio/request mapping, DAX, and optional zoned block reporting. `dm-table.c` uses the registry for every target load. Built-in error target registration occurs through `dm_target_init()` and `dm_target_exit()`.

## Risks
Registry locking and module references must prevent target code from unloading while table construction or live targets use it. Duplicate registration returns `-EBUSY`; unregistering an unknown target is a fatal bug. The error target's optional backing-device mode must keep queue-limit, zoned, and DAX behavior consistent even though all IO fails.

## Test Signals
Register and unregister loadable DM targets, load tables that trigger module autoload, and attempt duplicate registration in negative tests. For the error target, verify bio-based and request-based IO fail, discards fail as IO errors, optional backing-device arguments affect queue limits and zoned reporting, and DAX direct access returns `-EIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-target.c -->
