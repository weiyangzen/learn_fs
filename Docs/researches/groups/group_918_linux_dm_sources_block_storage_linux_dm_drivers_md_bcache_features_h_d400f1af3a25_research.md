# Group Research: group_918_linux_dm_sources_block_storage_linux_dm_drivers_md_bcache_features_h_d400f1af3a25

Scope: `Docs/research_subset_a.md`; source tree `sources/block-storage/linux-dm`.

This grouped report covers bcache feature flags, metadata I/O, journaling, request handling, moving garbage collection, writeback, sysfs exposure, module registration/lifecycle, utility primitives, tracing, and Device Mapper audit helpers. Each file listed in the work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/features.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/features.h

`features.h` defines the superblock feature-bit contract used by bcache cache devices. It separates feature classes into compatible, read-only compatible, and incompatible spaces, with helper masks for direct bit testing. In this snapshot the only supported feature bits are incompatible bucket-size layout flags: the obsolete 32-bit large bucket encoding and the newer logarithmic large-bucket-size encoding.

The core generated helpers come from `BCH_FEATURE_*_FUNCS()`, which emit `bch_has_feature_*()`, `bch_set_feature_*()`, and `bch_clear_feature_*()` routines against `struct cache_sb`. The generated `has` helpers explicitly return false for superblocks older than `BCACHE_SB_VERSION_CDEV_WITH_FEATURES`, so callers can use the same helpers on old and feature-bearing superblocks.

Unknown-feature detection is centralized in `bch_has_unknown_compat_features()`, `bch_has_unknown_ro_compat_features()`, and `bch_has_unknown_incompat_features()`. `super.c` uses these checks while reading feature-bearing cache superblocks, rejecting devices with unsupported bits before interpreting bucket geometry. The file also declares the feature-printing functions consumed by `sysfs.c` for `feature_compat`, `feature_ro_compat`, and `feature_incompat`.

Important dependencies are `bcache_ondisk.h` for `struct cache_sb` layout and superblock version constants, plus `features.c` for the declared printers. The main invariant is that feature bits are meaningful only on cache-device superblocks at or above the feature-version threshold.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/features.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/io.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/io.c

`io.c` provides low-level bcache bio helpers and error accounting. The `bbio` helpers allocate metadata bios from the cache-set mempool, initialize them with inline vectors sized for metadata buckets, copy a single pointer from a bkey when needed, set the target cache block device, record submission time, and submit through `closure_bio_submit()`.

The backing-device error path is handled by `bch_count_backing_io_errors()`. It intentionally ignores failed read-ahead bios because md raid recovery/degraded paths can fail speculative read-ahead without implying media failure. Non-read-ahead backing errors increment `cached_dev.io_errors` and call `bch_cached_dev_error()` after the configured device limit.

Cache-device errors are handled by `bch_count_io_errors()`. It implements decaying error accounting with `io_count`, `io_errors`, `error_decay`, and `error_limit`; when errors exceed the limit it escalates to `bch_cache_set_error()`. `bch_bbio_count_io_errors()` also maintains the cache-set congestion signal by comparing elapsed microseconds against read/write congestion thresholds and adjusting `c->congested`.

`bch_bbio_endio()` is the standard completion helper for `bbio` I/O: it updates congestion/error counters, drops the bio reference, and drops the closure. This file is depended on by journal, UUID/prio metadata I/O, request reads, moving GC, and writeback.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/io.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/journal.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/journal.c

`journal.c` implements bcache's btree-insertion journal. Journal replay is driven during cache-set startup: journal buckets are read, entries are validated by magic/checksum/size, valid `jset`s are ordered by sequence, obsolete entries are discarded using `last_seq`, keys are marked for GC/accounting, and then replayed into the btree in sequence order.

`journal_read_bucket()` scans a journal bucket without allowing a journal entry to span a bucket. It supports rereading a larger window when a valid entry is bigger than the current read, validates `jset_magic()` and `csum_set()`, inserts unique entries into an ordered replay list, and records the highest sequence seen per journal bucket. `bch_journal_read()` uses a golden-ratio probe followed by fallback linear search, binary search, and reverse wraparound reading to find the active circular journal region and initialize `cur_idx`, `last_idx`, `discard_idx`, and `c->journal.seq`.

`bch_journal_mark()` prepares replay by building the journal pin FIFO in reverse sequence order, attaching `journal_replay.pin` references where possible, pinning referenced buckets, and applying initial key marks. `bch_journal_replay()` verifies contiguous sequences except for discard-enabled gaps at the beginning, inserts each replay key with `bch_btree_insert()`, decrements replay pins, logs replay stats, and frees the replay list on exit.

The active journal write path stages keys in one of two `journal_write` buffers. `journal_wait_for_write()` waits until the current entry has room, forcing a write or journal reclaim when the current entry or journal device is full. `bch_journal()` appends keylist bytes into the current `jset`, bumps the current pin refcount, and either waits on a synchronous write or schedules delayed flush work. `bch_journal_meta()` creates an empty metadata journal update.

`journal_write_unlocked()` emits the current `jset`: it fills the btree root, UUID bucket, priority bucket, magic, version, `last_seq`, and checksum; writes with `REQ_SYNC|REQ_META|REQ_PREFLUSH|REQ_FUA`; advances journal pointer offsets; updates per-bucket sequence tracking; drops the initial current-entry pin; rotates to the next journal entry; and reclaims space. It treats a zero-pointer journal key as a bug because such a journal entry would be lost.

Journal reclaim is coordinated by the pin FIFO. `journal_reclaim()` pops fully unpinned entries, computes `last_seq`, advances `last_idx`, optionally issues discard bios for obsolete journal buckets, allocates the next bucket when the current one is exhausted, and wakes waiters once the journal is no longer full. If the journal is full because btree nodes still pin old entries, `btree_flush_write()` scans cached dirty btree nodes referencing the oldest journal entry and writes up to `BTREE_FLUSH_NR` of them to unblock reclaim.

Initialization and teardown are in `bch_journal_alloc()` and `bch_journal_free()`, which set locks/work, default journal delay, allocate the pin FIFO, and allocate two page-backed `jset` buffers. The file interacts heavily with `btree.c`, `super.c`, `io.c`, `util.h` FIFO helpers, and tracepoints.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/journal.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/journal.h

`journal.h` documents and declares bcache's journal model. The comments explain the circular bucket journal, ordered-key replay, open journal entry tracking via a refcount FIFO, and reclaim policy based on the oldest still-pinned journal entry. It also records a known fragility: `BTREE_REPLACE` operations are not journaled, so writeback and moving GC rely on flushing btree state around related metadata updates.

The replay data structure is `struct journal_replay`, a list node plus optional pin pointer and an inline variable-sized `jset`. The write-side staging unit is `struct journal_write`, which owns a `jset` buffer, waitlist, dirty flag, and need-write flag.

`struct journal` is embedded in `struct cache_set`; it contains the spinlocks, full-journal waitlist, I/O closure, delayed flush work, free block count, sequence counter, pin FIFO, current journal key, and two alternating `journal_write` buffers. `struct journal_device` is embedded in each `struct cache`; it records sequence numbers per journal bucket, current/last/discard bucket indexes, discard state, discard work/bio, and a reusable bio for journal I/O.

Important constants include `JSET_BITS` for journal buffer order, `BTREE_FLUSH_NR` for bounded old-entry flush work, `JOURNAL_PIN` for pin FIFO capacity, and `journal_full()` for the write path's full condition. Public functions cover journaling keys, advancing entries, marking/replaying journal lists, metadata journaling, reading replay lists, allocation, and free.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/movinggc.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/movinggc.c

`movinggc.c` implements copy/moving garbage collection for cache buckets that are partly used and worth compacting. The selection predicate `moving_pred()` matches bkeys with available pointers into buckets marked `GC_MOVE`.

`bch_moving_gc()` is the main entry point. It exits if copy GC is disabled, then scans buckets under `bucket_lock`, ignoring metadata, empty, full, and pinned buckets. It maintains a heap ordered by sectors used, accumulates the selected live-sector cost, trims selection to the moving-GC reserve capacity, marks selected buckets with `GC_MOVE`, resets the keybuf scan position, and starts the I/O loop.

The I/O loop in `read_moving()` refills `moving_gc_keys`, skips stale keys, allocates a `moving_io` large enough for inline bio vectors, initializes a read bio at idle priority, allocates pages, traces the copy, limits concurrency with `moving_in_flight`, and starts asynchronous read/write closures. Read completion checks for I/O failure and stale clean pointers; write submission uses `bch_data_insert()` with `replace=true`, preserves dirty/csum state, and sets writeback mode when the original key is dirty.

Completion frees bio pages, traces replace collisions, removes the keybuf entry, releases the moving-GC semaphore, and frees the `moving_io`. `bch_moving_init_cache_set()` initializes the cache-set keybuf and a 64-entry semaphore. This file depends on the request insertion path, keybuf infrastructure, btree replacement semantics, and cache bucket GC marks.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/movinggc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/request.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/request.c

`request.c` is the main bcache block I/O path. It handles cached backing-device requests, flash-only volume requests, cache lookup, cache insertion, miss handling, bypass decisions, writeback-mode decisions, detached-device forwarding, error recovery, and request accounting.

The cache insertion path centers on `struct data_insert_op` and `bch_data_insert()`. Data is split into cache-sized keys, sectors are allocated with `bch_alloc_sectors()`, optional checksums are computed with `bio_csum()`, writes are submitted to cache via `bch_submit_bbio()`, then generated keys are journaled and inserted into the btree. If allocation fails for non-writeback writes, writethrough writes invalidate the remaining range while cache-miss fills can insert already-written fragments or bail out. If a non-replace cache write fails, `bch_data_insert_error()` strips pointers from generated keys to invalidate the affected cache ranges instead of pointing at unwritten data.

`check_should_bypass()` decides whether a cached-device bio should skip cache. It bypasses on detach, high cache occupancy, discards, cache mode `none`, writearound writes, selected read-ahead/background I/O depending on policy, unaligned I/O, torture testing, sequential I/O beyond threshold, or congestion. It updates sequential I/O tracking with a recent-I/O hash/LRU and records bypassed sectors in stats.

Reads use a `struct search` closure. `cache_lookup_fn()` walks matching btree keys, calls the device-specific miss handler for holes, chooses a cache pointer, splits the request, copies/cuts a bkey into the child `bbio`, and submits cache reads. Clean cache reads are rechecked for stale pointers at completion; stale clean reads are treated as recoverable cache-read races. `cache_lookup()` maps keys through the btree and marks dirty-cache read errors as unrecoverable from backing storage.

Cached-device miss handling is in `cached_dev_cache_miss()`. It may allocate a bounce bio for the miss range, read from backing storage, then `cached_dev_read_done()` copies fetched data to the original bio and optionally inserts it into cache using replace semantics. If cache read recovery is permitted, `cached_dev_read_error()` retries failed clean cache reads from the backing device.

Writes use `cached_dev_write()`. It checks overlap with moving GC and active writeback keys, forces writeback for overlapping dirty writeback ranges, bypasses discards, consults `should_writeback()`, and either sends I/O to the backing device, writes only to cache in writeback mode, or clones the bio for writethrough. Flushes in writeback mode also submit a backing-device flush. All write paths call `bch_data_insert()` to update or invalidate cache metadata.

`cached_dev_submit_bio()` is the block-layer entry point for cached backing devices. It rejects I/O when the cache set or backing device is disabled, resets idle/max-writeback-rate state on new I/O, remaps to the backing device and data offset, allocates a search if the cached device is active, and dispatches empty flushes, reads, or writes. If the cache device is detached, it forwards directly through `detached_dev_do_request()` while preserving accounting and error handling.

Flash-only devices use `flash_dev_submit_bio()`. Reads map cache keys and zero-fill misses; writes are always cache writeback/insertion operations, with discards represented as bypass invalidations. The file initializes per-device request callbacks and owns the `bch_search_cache` slab via `bch_request_init()`/`bch_request_exit()`.

Major cross-file dependencies include `journal.c` for key persistence, `btree.c` for lookup/insert, `writeback.h` for writeback decisions, `io.c` for bbio submission/error handling, `stats.c` for accounting, and `super.c` for device registration callbacks.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/request.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/request.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/request.h

`request.h` exposes the request-layer API and defines `struct data_insert_op`, the closure state used by cache insertion, writeback, flash-volume writes, and moving GC. The structure carries the cache set, bio, workqueue, inode/device id, write point/priority, block status, flags, generated insert keylist, and optional replacement key.

The flag union names the insertion modes: bypass invalidation, writeback/dirty insertion, journal flushing, checksum generation, replacement insertion, replacement collision reporting, and insert completion. This common structure is the bridge between request handling, moving GC, and writeback.

The header declares congestion probing, data insertion, cached-device and flash-device request initialization, block-layer submit functions, and the `bch_search_cache` slab. It assumes the broader bcache type definitions from `bcache.h`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/request.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/stats.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/stats.c

`stats.c` implements bcache cache-hit and bypass accounting exposed through sysfs. It tracks absolute totals and three rolling windows: five minutes, one hour, and one day. Atomic collectors accumulate hot-path counters, and a timer periodically transfers collector values into shifted counters and rescales EWMAs.

Sysfs attributes include hits, misses, bypass hits, bypass misses, hit ratio, miss collisions, and bypassed bytes. `bch_stats_show()` converts internal fixed-point counters by shifting down 16 bits and computes hit ratio with `DIV_SAFE()`.

`bch_cache_accounting_add_kobjs()` installs `stats_total`, `stats_five_minute`, `stats_hour`, and `stats_day` kobjects under a parent. `bch_cache_accounting_init()` initializes kobjects, closure, timer, and starts periodic accounting. `bch_cache_accounting_destroy()` puts kobjects, marks closing, and coordinates timer completion with the closure.

Hot-path marking helpers update per-device and cache-set collectors: `bch_mark_cache_accounting()` for hit/miss and bypass dimensions, `bch_mark_cache_miss_collision()` for replacement collisions, and `bch_mark_sectors_bypassed()` for bypassed sector totals. `bch_cache_accounting_clear()` resets only total counters; rolling windows are independently decayed by the timer.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/stats.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/stats.h

`stats.h` declares the accounting structures used by cached devices and cache sets. `struct cache_stat_collector` contains atomic hot-path counters for cache hits, misses, bypass hits/misses, miss collisions, and bypassed sectors.

`struct cache_stats` is a sysfs-visible fixed-point snapshot with a kobject, absolute or decayed counters, and a rescale counter. `struct cache_accounting` ties the collector, timer, closure, close flag, and four stats windows together.

The public API covers initialization, sysfs kobject creation, clearing, destruction, and hot-path marking. The header declares `bch_mark_cache_readahead()` even though this grouped source set does not include an implementation in `stats.c`, which is a notable declaration/API mismatch to resolve by checking the wider bcache tree if needed.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/super.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/super.c

`super.c` owns bcache module setup/teardown, superblock parsing/writing, UUID and priority metadata I/O, bcache block-device creation, cached-device/cache-device registration, cache-set startup/recovery, detach/unregister behavior, reboot shutdown, and global sysfs registration entry points.

Superblock reading starts with `read_super()`, which reads the on-disk superblock page, validates offset, magic, checksum, UUID, block size, and version. Cache-device superblocks pass through `read_super_common()`, which validates bucket/journal geometry, set membership, device size, and sequential journal bucket layout. Feature-bearing cache superblocks first convert feature bitfields and reject unknown compatible, read-only compatible, or incompatible bits before bucket-size interpretation via `get_bucket_size()`.

Superblock writing uses `__write_super()` for both backing and cache devices, filling endian-converted disk fields, feature fields for feature-bearing versions, checksums, and a synchronous metadata write bio. `bch_write_bdev_super()` serializes backing-super writes with `sb_write_mutex`; `bcache_write_super()` updates cache-set sequence/version and writes the cache-device superblock.

UUID metadata I/O is handled by `uuid_io()`, `uuid_read()`, `__uuid_write()`, and `bch_uuid_write()`. UUID entries live in a metadata bucket referenced from the journal; old UUID formats are converted in place after read. UUID writes allocate a metadata bucket, write the UUID page through cache bbios, update `c->uuid_bucket`, free the bkey reference, and journal a metadata update.

Priority metadata stores bucket generation and priority data in linked metadata buckets. `bch_prio_write()` serializes current bucket state into packed `prio_set` pages, allocates priority-reserve buckets, writes them, journals the new metadata pointer, and only then frees old priority buckets. `prio_read()` follows the priority bucket chain, validates magic/checksum, and restores bucket `prio`, `gen`, and `last_gc`.

The bcache device layer builds gendisks with `bcache_device_init()`, assigning the bcache major, 128 minors per device, queue limits, discard support, write-cache flags, dirty stripe arrays, a bioset, and an ida index. `open_dev()`, `release_dev()`, and `ioctl_dev()` provide common block operations. Device attach/link/unlink/detach maintain cache-set device arrays, sysfs links, holder links, UUID invalidation on detach, and cache-set closure references.

Cached backing-device lifecycle includes `cached_dev_init()`, `register_bdev()`, `bch_cached_dev_attach()`, `bch_cached_dev_run()`, `bch_cached_dev_detach()`, and free/flush callbacks. Attach validates set UUID, duplicate UUIDs, block-size compatibility, UUID table state, starts writeback infrastructure while initially blocked by `writeback_lock`, initializes dirty-sector accounting, runs the bcache disk, links sysfs, and marks obsolete large-bucket cache sets read-only. A status kthread watches for a dying backing queue and disables I/O after a timeout.

Flash-only volume lifecycle is implemented by `bch_flash_dev_create()`, `flash_dev_run()`, `flash_devs_run()`, and flash free/flush callbacks. Flash volumes allocate UUID entries marked `UUID_FLASH_ONLY`, create bcache gendisks backed by the cache set, initialize dirty-sector state, attach request handlers, and expose them as `volume<N>` links.

Cache-set lifecycle starts with `bch_cache_set_alloc()`, which initializes closures, kobjects, accounting, locks, waits, moving GC, lists, mempools, biosets, UUID storage, workqueues, journal, btree cache, open buckets, sort state, congestion defaults, and error limits. `run_cache_set()` either recovers a synchronized cache by reading journal, priorities, btree root, UUIDs, btree checks, GC marks, allocator startup, UUID upgrade, and journal replay, or initializes a new invalidated cache by creating journal buckets, priorities, UUID bucket, root btree node, sync flag, and initial journal metadata. It then starts GC, writes the superblock, attaches pending backing devices, runs flash volumes, and marks the set running.

Error and unregister behavior is coordinated by `bch_cache_set_error()`, `bch_cache_set_unregister()`, `__cache_set_unregister()`, `cache_set_flush()`, and `cache_set_free()`. Cache-set failures set `CACHE_SET_IO_DISABLE`, optionally panic, stop/detach devices, preserve clean backing devices when `stop_when_cache_set_failed=auto`, flush dirty btree nodes unless I/O is disabled, stop allocator/GC, flush pending journal work, and release resources.

Global registration is exposed by `/sys/fs/bcache/register`, `register_quiet`, and `pendings_cleanup`. `register_bcache()` opens a path exclusively, sets block size, reads the superblock, rejects duplicate/busy devices with bcache-aware checks, and registers a backing or cache device either synchronously or via delayed work under `CONFIG_BCACHE_ASYNC_REGISTRATION`. Reboot handling blocks new registrations, stops all cache sets and uncached devices, and waits up to about ten seconds for lists to drain.

Module initialization validates writeback cutoff parameters, initializes global locks/waits, registers the block major, initializes btree/request/debug/closure subsystems, creates workqueues and `/sys/fs/bcache`, and installs global sysfs files. Module exit tears those resources down in reverse. This file is the central integration point for almost every other bcache file in this group.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/super.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/sysfs.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/sysfs.c

`sysfs.c` defines the user-facing and internal sysfs control surface for cached devices, flash volumes, cache sets, and cache devices. It uses macro helpers from `sysfs.h` to declare attributes and kobject types, with locked show/store wrappers where global registration state must be serialized by `bch_register_lock`.

Cached-device attributes expose cache mode, readahead cache policy, stop-on-cache-failure behavior, writeback controls, I/O error state, dirty data, stripe geometry, sequential cutoff, running/state/label, backing device name/UUID, and debug-only verification/torture controls. Stores can clear stats, run a stale/no-cache device, change cache mode and persist it to the backing superblock, attach to a cache set by UUID, detach, stop, update labels with uevents and UUID-table writes, tune writeback rate controller parameters, and toggle `io_disable`.

The cached-device store wrapper performs post-processing for `writeback_running` and `writeback_percent`: it wakes the writeback thread when the running flag changes and starts delayed writeback-rate updates once a device is attached and writeback percentage is set. All user stores reject writes while `bcache_is_reboot` is true.

Flash-volume attributes expose size, label, unregister, and disabled data checksum plumbing. Stores can resize the gendisk by updating UUID-entry sectors, relabel the UUID entry, or unregister by setting detach and stopping the bcache device.

Cache-set attributes expose synchronous mode, journal delay, flash volume creation, geometry, root/btree usage, btree cache metrics, average key size, error policy, I/O error tuning, congestion settings, and clear stats. Internal cache-set attributes add active journal entries, timing stats, btree node stats, bset tree stats, cache read races, journal reclaim counters, writeback key counters, GC/prune triggers, debug flags, copy GC, idle max writeback, auto-GC-after-writeback, I/O disable, writeback cutoff module parameters, and feature bit printers.

The cache-set show path computes live values by locking the root btree for root usage, summing cached btree memory under `bucket_lock`, scanning bucket hash chains, and using GC stats for btree utilization. The store path can unregister/stop the set, toggle sync and write the cache superblock, create flash volumes, clear counters, trigger GC, prune through the shrinker, change error action, tune error/congestion behavior, toggle cache-set I/O disable, and set debug/GC controls.

Cache-device attributes expose bucket/block geometry, bucket count, discard policy, written byte counters, I/O errors, replacement policy, priority stats, and stat clearing. Priority stats allocate a temporary priority array, count unused/clean/dirty/metadata buckets under the bucket lock, sort priorities, filter metadata/zero priorities, and print quantiles.

The file depends on `features.h` printers, `writeback.h` tunables, `request.h` congestion helper, `stats.c` accounting, `super.c` lifecycle functions, and btree/key statistics. Its major invariant is that sysfs state changes which affect global registration, attachment, or cache-set operation run under `bch_register_lock`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/sysfs.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/sysfs.h

`sysfs.h` is a macro utility header for bcache sysfs files. It defines `KTYPE()` to build `struct kobj_type` instances with local show/store functions and default attribute arrays. `SHOW()`, `STORE()`, `SHOW_LOCKED()`, and `STORE_LOCKED()` standardize sysfs handler definitions, with locked variants wrapping calls in `bch_register_lock`.

Attribute declaration helpers create write-only, read-only, and read-write `struct attribute`s. Print helpers select formatting based on C type, append newlines, or use `bch_hprint()` for human-readable byte values. `var_print`/`var_printf`/`var_hprint` pair those helpers with a local `var()` macro pattern used heavily in `sysfs.c`.

Store helpers parse decimal integers, booleans, clamped unsigned longs, and human-readable sizes. The `strtoul_or_return()` and `strtoi_h_or_return()` macros deliberately return parse errors directly from the surrounding sysfs store function. This header therefore assumes use inside sysfs show/store functions with `attr`, `buf`, and `size` variables in scope.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/trace.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/trace.c

`trace.c` instantiates bcache tracepoints by defining `CREATE_TRACE_POINTS` before including `<trace/events/bcache.h>`. It then exports the tracepoint symbols GPL-only so other bcache compilation units and modules can use them.

Exported tracepoints cover request start/end, bypass decisions, reads/writes/retries, cache insertion, journal replay/write/full events, btree cache pressure, btree reads/writes, node allocation/free, GC start/end/copy/collision, btree key insertion and structural changes, invalidation, allocation failure, and writeback/collision events.

The file has no runtime logic beyond tracepoint creation/export, but it is the central build unit that makes all `trace_bcache_*()` calls in the other bcache files link correctly.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/util.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/util.c

`util.c` implements bcache utility functions declared in `util.h`. The generated `bch_strto*_h()` parsers accept decimal numbers with binary size suffixes from `k` through `y`/`z`, reject malformed trailing characters, and check overflow for signed and unsigned targets while multiplying by 1024.

`bch_hprint()` formats signed 64-bit values into compact binary-suffix strings for sysfs, always scaling at least once so byte-like values print with a suffix. `bch_is_zero()` tests a memory range for all-zero bytes. `bch_parse_uuid()` parses up to 32 UUID hex nybbles while tolerating separators from a restricted character set.

`bch_time_stats_update()` updates max duration plus EWMA duration/frequency under a spinlock using `local_clock()`. `bch_next_delay()` implements rate-limit scheduling by advancing the next desired work time based on work done and an atomic rate, bounding both backlog and future sleep to keep writeback responsive.

`bch_bio_map()` initializes a fresh bio's bvec table to cover either a linear memory buffer or unbacked pages, directly filling `bi_io_vec`/`bi_vcnt` because callers use newly initialized bios. `bch_bio_alloc_pages()` allocates a page for each bvec and frees already allocated pages on failure. These helpers are used by cache insert, moving GC, writeback, journal/UUID/prio I/O, and sysfs formatting.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/util.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/util.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/util.h

`util.h` provides shared bcache helper macros, data structures, and inline routines. Debug builds turn `EBUG_ON()` and atomic inc/dec checks into `BUG_ON()` assertions; non-debug builds reduce them to no-op-ish or plain atomic operations.

The heap macros implement an array-backed binary heap with caller-provided comparison, allocation via `kvmalloc()`, and add/pop/peek/full helpers. Moving GC uses this heap to choose partially used buckets. The FIFO macros implement a power-of-two ring buffer used heavily by journal pin tracking and cache bucket reserve lists; variants support exact or rounded sizing, push/pop at both ends, swapping, and moving between FIFOs.

The array allocator macros provide a fixed-size stack freelist over an embedded data array, used by keybuf-style structures where bounded allocation without runtime failure is useful. Red-black tree macros provide generic insert/search/greater/first/last/next/prev wrappers using local comparison callbacks and `container_of_or_null()`.

Parsing and formatting declarations include human-readable integer parsers, safe `kstrtoul()` wrappers, clamped parsing, `bch_hprint()`, zero test, and UUID parsing. Time helpers define `struct time_stats`, `local_clock_us()`, sysfs time-stat print/attribute macros, and `ewma_add()`.

Rate limiting is represented by `struct bch_ratelimit` with nanosecond `next` time and atomic rate; `bch_ratelimit_reset()` and `bch_next_delay()` support writeback throttling. `DIV_SAFE()` avoids divide-by-zero, `bch_crc64()` wraps big-endian CRC64 with init/final xor, and `fract_exp_two()` is a stepwise pseudo-exponential used for congestion bypass thresholds.

The header also declares `bch_bio_map()` and `bch_bio_alloc_pages()`. Because many macros evaluate caller expressions and assume specific in-scope names, this file is powerful but requires careful use at call sites.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/util.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/writeback.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/writeback.c

`writeback.c` implements background writeback of dirty cache data to backing devices, dirty-sector accounting, writeback rate control, dirty-key scanning, and startup initialization for cached devices.

The rate controller computes a dirty-sector target from cache capacity excluding flash-only dirty sectors, configured `writeback_percent`, and each backing device's proportional size share. `__update_writeback_rate()` is a PI controller using proportional and integral terms, with an optional fragmentation-aware override when cache usage and dirty bucket fragmentation are high. `set_at_max_writeback_rate()` detects an idle cache set after several update rounds and raises the rate to `INT_MAX` if enabled; incoming foreground I/O in `request.c` resets that state.

`update_writeback_rate()` is delayed work. It marks itself running with `BCACHE_DEV_RATE_DW_RUNNING`, exits if writeback is stopped or cache-set I/O is disabled, updates the rate under `writeback_lock` when dirty data exists and writeback percentage is nonzero, optionally triggers auto-GC-after-writeback state, reschedules itself, and clears the running flag.

The dirty I/O path uses `struct dirty_io`. `read_dirty()` gathers up to `MAX_WRITEBACKS_IN_PASS` contiguous dirty keys and up to `MAX_WRITESIZE_IN_PASS` sectors, allocates a per-key bio, reads dirty data from the cache, and chains to ordered backing writes. `write_dirty()` enforces write ordering using `writeback_sequence_next` and a closure waitlist, then writes to the backing device if the dirty bit survived the cache read. `write_dirty_finish()` clears the dirty bit in the btree via replacement insert, traces collisions, updates done/failed counters, removes the keybuf entry, and releases concurrency.

Dirty-sector accounting is maintained by `bcache_dev_sectors_dirty_add()`, which maps offsets to stripes, updates per-stripe atomic dirty sector counts, manages the full-dirty-stripe bitmap, and separately accounts flash-only dirty sectors. `dirty_pred()` selects dirty bkeys for the writeback keybuf. `refill_full_stripes()` prioritizes full dirty stripes for devices where partial stripes are expensive, while `refill_dirty()` scans the btree keyspace with wraparound and reports whether the full disk was scanned.

`bch_writeback_thread()` is the long-running per-cached-device thread. It sleeps when writeback has no work or is disabled, scans dirty data under `writeback_lock`, marks devices clean and updates the backing superblock after a full clean scan, handles detach completion by clearing UUID/set state, triggers moving GC after high-dirty writeback if configured, runs `read_dirty()`, applies a post-full-scan delay, and exits on stop or cache-set I/O disable. It flushes/destroys the writeback workqueue and drops its cached-device reference on exit.

Dirty-sector initialization at attach time is handled by `bch_sectors_dirty_init()`. For a leaf root it scans root keys directly; otherwise it starts up to half the online CPU count, capped at `BCH_DIRTY_INIT_THRD_MAX`, with each thread walking root keys and recursively scanning leaf subtrees. The initialization backs off when foreground searches are inflight.

`bch_cached_dev_writeback_init()` sets defaults for semaphores, locks, keybuf, writeback policy, PI terms, fragmentation terms, minimum rate, delayed work, and flags. `bch_cached_dev_writeback_start()` allocates a writeback workqueue, creates the thread, marks writeback running, schedules rate updates, and wakes the thread.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/writeback.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/writeback.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/bcache/writeback.h

`writeback.h` defines writeback thresholds, rate-update bounds, fragmentation thresholds, dirty-initialization thread limits, and shared writeback helpers. The default writeback cutoff is 40 percent cache use, sync cutoff is 70 percent, with module-parameter maxima of 70 and 90 respectively.

`struct bch_dirty_init_state` and `struct dirty_init_thrd_info` coordinate multi-threaded dirty-sector initialization during attach. The state tracks the cache set, device, total threads, shared root-key index, lock, started/enough atomics, waitqueue, and per-thread metadata.

Inline helpers sum dirty sectors across stripes, map offsets to stripe indexes with range checking, test whether any stripe covered by a request is dirty, determine whether an incoming write should be handled in writeback mode, wake the writeback thread, and mark a cached device as having dirty data. `should_writeback()` blocks writeback outside writeback cache mode, during detach, above the sync cutoff, and for discards; it forces writeback for expensive partial-stripe overlaps and otherwise considers sync/meta/priority writes or low cache usage.

The header exports writeback cutoff module parameters and declares dirty-sector accounting, dirty initialization, cached-device writeback initialization, and writeback startup functions.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/bcache/writeback.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-audit.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-audit.c

`dm-audit.c` implements audit logging helpers for Device Mapper targets when `CONFIG_DM_AUDIT` is enabled. `dm_audit_log_start()` skips work when auditing is off, starts an audit buffer with the given audit type, and writes the common `module=<prefix> op=<op>` fields.

`dm_audit_log_ti()` logs target-level control or event records from a `struct dm_target`. For `AUDIT_DM_CTRL`, it adds task info, mapped-device major/minor, and either the target error string or success. For `AUDIT_DM_EVENT`, it logs device major/minor and an unknown sector placeholder. Unsupported audit types are ignored. The function appends `res=<result>` and exports the symbol GPL-only.

`dm_audit_log_bio()` logs a bio-level DM event with the underlying bio block-device major/minor, sector, and result, then ends the audit buffer. It is also exported GPL-only. This file depends on Linux audit APIs, DM core helpers, mapped-device disk lookup, and bio/block-device metadata.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-audit.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-audit.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-audit.h

`dm-audit.h` declares the Device Mapper audit helper interface. With `CONFIG_DM_AUDIT`, it exposes bio-level logging and the lower-level target logger, plus inline wrappers for target constructor (`ctr`), destructor (`dtr`), and generic target event operations.

The header explicitly documents that DM modules should use wrappers rather than calling `dm_audit_log_ti()` directly. Without `CONFIG_DM_AUDIT`, all helper functions compile to empty inline stubs, preserving call sites without runtime or link cost.

The public API depends on `struct dm_target`, `struct bio`, Linux audit type constants such as `AUDIT_DM_CTRL` and `AUDIT_DM_EVENT`, and operation/result strings supplied by DM targets.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-audit.h -->