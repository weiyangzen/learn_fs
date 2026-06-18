# Research: subset-b-004020

Grouped research for bcache setup/sysfs/writeback utility files and Device Mapper audit/bio-prison helpers. Each section is delimited for reconciliation into the required source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/super.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/super.c

## Purpose
`super.c` is the bcache registration, lifetime, and metadata I/O core. It recognizes cache and backing-device superblocks, registers `/sys/fs/bcache` control files, creates cache sets, attaches cached devices, exposes flash-only volumes, writes bcache superblocks, maintains UUID and priority metadata buckets, and tears everything down during unregister or reboot.

## Important APIs, Types, And Functions
Global state includes `bcache_kobj`, `bch_register_lock`, `bcache_is_reboot`, `bch_cache_sets`, `uncached_devices`, the block major, device IDA, unregister waitqueue, and bcache workqueues. `read_super()` and `read_super_common()` validate on-disk superblocks, feature bits, checksum, sizes, UUIDs, journal buckets, data offsets, and bucket layout. `__write_super()`, `bch_write_bdev_super()`, and `bcache_write_super()` persist updated backing/cache superblocks. UUID metadata is handled by `uuid_io()`, `uuid_read()`, `__uuid_write()`, and `bch_uuid_write()`. Priority/generation metadata is handled by `bch_prio_write()` and `prio_read()`. Device lifecycle runs through `bcache_device_init()`, `bcache_device_stop()`, attach/detach helpers, `bch_cached_dev_run()`, `bch_cached_dev_attach()`, `bch_cached_dev_detach()`, `register_bdev()`, `register_cache()`, and `register_cache_set()`. Module control flows enter through `register_bcache()`, `bch_pending_bdevs_cleanup()`, `bcache_reboot()`, `bcache_init()`, and `bcache_exit()`.

## Control Flow
User space writes a path to `/sys/fs/bcache/register` or `register_quiet`. `register_bcache()` opens the block device read-only, reads and validates the bcache superblock, allocates either `struct cached_dev` or `struct cache`, reopens the block device writable/exclusive with that holder, and either performs or queues registration. Backing devices become `cached_dev` instances and are placed on `uncached_devices` until a matching cache set is present. Cache devices allocate `struct cache`, create or join a `struct cache_set`, then `run_cache_set()` either recovers an existing set by replaying journal/priority/UUID metadata or initializes a fresh cache set, starts allocator and GC threads, attaches waiting backing devices, starts flash-only volumes, and marks the set running. Stop/unregister sets flags, queues closures, detaches or stops member devices, flushes btree/journal metadata when possible, releases kobjects, and wakes `unregister_wait`.

## State And Persistence
The file persists superblock sequence/state/feature/label fields, backing-device clean/dirty/stale state, UUID table entries, priority/generation buckets, journal-root references, and cache replacement mode. Runtime state spans closures, kobjects, block disks, biosets, workqueues, kthreads, bucket reservations, sysfs links, block holder links, and lists protected by `bch_register_lock`. The reboot notifier sets `bcache_is_reboot`, rejects new registration, stops cache sets and uncached devices, and waits up to roughly ten seconds for the global lists to drain.

## Dependencies And Integration Points
It integrates with bcache btree, journal, allocation, request, writeback, debug, feature, accounting, and sysfs code. Kernel dependencies include block-device open/holder APIs, `gendisk`, kobjects, sysfs, workqueues, kthreads, folio-backed superblock reads, bios, closures, debugfs, reboot notifiers, and module refcounting. `sysfs.c` calls many exported lifecycle routines, while `writeback.c` depends on `bch_write_bdev_super()` for dirty/clean state transitions.

## Risks
Registration and teardown are concurrency-heavy: `bch_register_lock`, closures, kobject references, block holders, async registration, and reboot paths must stay ordered or devices can leak, double-unlink, or disappear while I/O is active. Superblock validation must reject unsupported feature layouts and malformed bucket geometry before any write. `bch_prio_write()` temporarily drops `bucket_lock` while doing I/O, so bucket pin and old-priority cleanup ordering matters. Dirty cache-set failure policy can either stop or keep backing devices based on dirty state; mistakes risk data loss in writeback mode. Embedded `sb_bio` and `sb_disk` folio lifetimes are protected by the superblock write semaphore and must not be freed early.

## Test Signals
Useful signals include module init/exit, sysfs register/register_quiet with cache and backing devices, duplicate or busy device registration, async registration, unsupported feature bits, bad checksums and geometry, fresh cache initialization, journal recovery, UUID migration, flash-volume creation, attach/detach with dirty and clean devices, error-triggered cache-set unregister, reboot notifier waiting, pending backing-device cleanup, and fault injection for superblock, UUID, priority, kobject, workqueue, and allocator failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.c

## Purpose
`sysfs.c` implements the bcache object model visible under backing devices, flash volumes, cache sets, cache-set internals, and cache devices. It turns attribute reads into status/statistics output and attribute writes into configuration changes, metadata persistence, explicit attach/detach, garbage collection, writeback tuning, and stop/unregister actions.

## Important APIs, Types, And Functions
Attribute declarations use macros from `sysfs.h` for write-only, read-only, and read/write files. String-list helpers expose cache modes, readahead policies, cache-set failure policies, replacement policies, and error actions. `__bch_cached_dev_show()` and `__cached_dev_store()` handle backing-device attributes including `cache_mode`, `writeback_*`, `io_disable`, `running`, `label`, `attach`, `detach`, and `stop`; `bch_cached_dev_store()` wraps this with global locking and schedules writeback-rate work when needed. `bch_flash_dev_show()` and `__bch_flash_dev_store()` expose flash volume `size`, `label`, and unregister. Cache-set helpers compute bset statistics, root usage, btree cache size, bucket hash chain length, used percentage, and average key size. `__bch_cache_set_show()`/`__bch_cache_set_store()` expose cache-set control, feature flags, GC, prune, error policy, congestion, and debug state. `__bch_cache_show()`/`__bch_cache_store()` expose per-cache stats and replacement policy.

## Control Flow
Sysfs dispatch enters generated `*_show` or `*_store` methods for the kobject type. Locked variants acquire `bch_register_lock` before touching global device/cache-set state. Reads compare `attr` against static `sysfs_*` attributes and return formatted output using `sysfs_emit()`, `bch_hprint()`, or string-list formatting. Writes first reject access during reboot via `bcache_is_reboot`, parse text using numeric or human-readable helpers, clamp values where required, then update in-memory fields and persist selected changes with `bch_write_bdev_super()`, `bcache_write_super()`, or `bch_uuid_write()`. Attach writes parse a UUID and try all cache sets. Writeback toggles wake the writeback thread and start delayed rate updates only when attached to a cache set.

## State And Persistence
Many attributes are purely runtime counters or tunables, but several persist: cached-device label, cache mode, backing-device superblock state, cache-set synchronous bit, replacement policy, flash volume UUID-table size/label, and UUID labels. Clear-stat actions reset atomics and accounting structures. `io_disable`, `CACHE_SET_IO_DISABLE`, debug booleans, congestion thresholds, and writeback controller parameters remain runtime state unless their backing metadata is explicitly written elsewhere.

## Dependencies And Integration Points
This file depends on `bcache.h`, btree traversal/stat APIs, request/debug/accounting helpers, `writeback.h`, feature rendering helpers, block-device naming, sorting, and scheduler clock utilities. It is tied to `super.c` through kobject types and lifecycle functions, to `writeback.c` through writeback parameter semantics and scheduling, and to GC/shrinker paths through `force_wake_up_gc()` and shrinker callbacks.

## Risks
The implementation is attribute-pointer dispatch, so adding an attribute without matching show/store behavior silently returns `0` or accepts no-op writes. Some writes persist immediately and asynchronously, so error handling around metadata writes matters. Global locking prevents many races but may interact with sysfs calls that themselves trigger detach/stop work. Label handling copies fixed-size arrays and emits uevents; bounds and newline trimming are important. Writeback parameter clamps depend on the ordering of low/mid/high fragment thresholds. Reboot rejection prevents late sysfs mutation during module/device shutdown.

## Test Signals
Exercise all visible attributes with valid and invalid input, including cache-mode strings, UUID attach parsing, writeback rate clamps, label sizes, flash volume resizing, GC trigger, prune count, error action switching, `io_disable` toggling, replacement-policy persistence, and access while `bcache_is_reboot` is set. Also check sysfs links and default group creation for `bch_cached_dev`, `bch_flash_dev`, `bch_cache_set`, `bch_cache_set_internal`, and `bch_cache`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.h

## Purpose
`sysfs.h` is the macro layer used by bcache sysfs implementations. It standardizes `kobj_type` construction, show/store function declarations, globally locked wrappers, attribute declarations, formatting helpers, numeric parsers, clamp helpers, and human-readable numeric parsing for sysfs writes.

## Important APIs, Types, And Functions
`KTYPE(type)` builds a `const struct kobj_type` with a release function, inline `sysfs_ops`, and default attribute groups. `SHOW()`, `STORE()`, `SHOW_LOCKED()`, and `STORE_LOCKED()` generate sysfs callbacks, with locked forms taking `bch_register_lock` and forwarding to `__name_show/store`. `write_attribute()`, `read_attribute()`, and `rw_attribute()` produce static `struct attribute` instances. Formatting helpers include `sysfs_printf()`, `sysfs_print()`, `sysfs_hprint()`, and `var_*` wrappers. Parsing helpers include `sysfs_strtoul()`, `sysfs_strtoul_bool()`, `sysfs_strtoul_clamp()`, `strtoul_or_return()`, `strtoi_h_or_return()`, and `sysfs_hatoi()`.

## Control Flow
Each show/store body in `sysfs.c` is a sequence of macro checks comparing the current `attr` pointer to a generated `sysfs_*` object. On match, the macro formats into `buf`, parses from `buf`, updates the target variable, and returns either byte count or parse error. Locked wrappers serialize the whole show/store body around the global registration lock.

## State And Persistence
The header owns no runtime state. It mutates state only through variables passed by the caller. Persistence is caller-defined: a macro may update an in-memory field, but the caller must explicitly invoke bcache metadata writes when the field is persistent.

## Dependencies And Integration Points
It assumes `bch_register_lock`, `bch_hprint()`, `strtoi_h()`, and kernel sysfs/kobject types are in scope. It is tightly coupled to `sysfs.c` naming conventions: generated functions and attributes must match `type_release`, `type_groups`, `__type_show`, and `__type_store` symbols.

## Risks
These macros hide control flow and returns, so misuse can bypass cleanup or make an attribute silently shadow later logic. `sysfs_print()` chooses formats using `__builtin_types_compatible_p`; unsupported types fall back to integer formatting. Locked wrappers use one global mutex, which is simple but can serialize unrelated sysfs reads and writes. Parsing helpers return directly from the caller, so they should only be used in straightforward store functions.

## Test Signals
Build coverage is the main signal: every generated kobject type and attribute must compile. Runtime tests should cover show/store attributes using bool, bounded unsigned long, human-readable sizes, string-list parsing, unknown attributes returning `0`, and locked wrappers under concurrent attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/trace.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/trace.c

## Purpose
`trace.c` materializes and exports bcache tracepoints declared in `<trace/events/bcache.h>`. It is the compilation unit that defines `CREATE_TRACE_POINTS`, creating tracepoint storage and making selected bcache events visible to tracing users and GPL modules.

## Important APIs, Types, And Functions
There are no local functions. The file includes `bcache.h`, `btree.h`, `linux/blktrace_api.h`, and `linux/module.h`, defines `CREATE_TRACE_POINTS`, includes the bcache trace event header, then calls `EXPORT_TRACEPOINT_SYMBOL_GPL()` for request, bypass, read/write, cache insert, journal, btree, GC, invalidation, allocation, and writeback events.

## Control Flow
At build/load time, the trace event header expands into tracepoint definitions. Other bcache code calls `trace_bcache_*()` helpers generated from the trace event header. This file only provides the backing symbols and exports; it does not run per-I/O logic itself.

## State And Persistence
Tracepoint enablement and buffers are kernel tracing runtime state, not bcache persistent metadata. The file stores no bcache device state and writes nothing to disk.

## Dependencies And Integration Points
The exported tracepoints integrate with ftrace/perf/tracefs and with bcache call sites in request, journal, btree, GC, allocation, and writeback code. Inclusion of bcache and btree headers ensures event field helpers can see bcache types.

## Risks
The main risk is symbol/header drift: event names exported here must match tracepoint declarations in `<trace/events/bcache.h>` and call sites. Tracepoints must remain low overhead when disabled, and field definitions must not dereference unstable bcache objects after lifetime transitions.

## Test Signals
Build with tracing enabled, inspect `/sys/kernel/tracing/events/bcache`, enable representative events, run cached read/write/writeback/GC workloads, and verify events appear without warnings. Also check that modules depending on GPL-exported tracepoints resolve successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/util.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/util.c

## Purpose
`util.c` implements small bcache utility routines shared by sysfs, superblock parsing, metadata I/O, timing, rate limiting, UUID parsing, and bio setup.

## Important APIs, Types, And Functions
`STRTO_H()` generates `bch_strtoint_h()`, `bch_strtouint_h()`, `bch_strtoll_h()`, and `bch_strtoull_h()` for decimal values with binary suffixes `k` through `y`/`z`. `bch_hprint()` formats byte/sector counts into compact human-readable strings. `bch_is_zero()` tests zero-filled buffers and is used for UUID validation. `bch_parse_uuid()` parses hex UUID text while tolerating punctuation. `bch_time_stats_update()` records max duration and EWMA duration/frequency under a spinlock. `bch_next_delay()` advances a ratelimit schedule based on completed work and configured rate. `bch_bio_map()` maps a contiguous virtual/vmalloc buffer, or placeholder pages, into an already-sized bio. `bch_bio_alloc_pages()` allocates one page per bio vector and unwinds on allocation failure.

## Control Flow
Parsing functions scan input, validate suffix and overflow, then return `0` or `-EINVAL`. Time stats read `local_clock()`, compute duration and interval, update EWMA fields, and record `last`. Ratelimit uses `done / rate` to move `next`, bounds how far ahead/behind the stream can drift, and returns a jiffy delay. Bio helpers assume freshly initialized bios with vector storage already allocated, fill `bio_vec` entries, then leave submission to callers.

## State And Persistence
The file has no global persistent state. It mutates caller-owned `time_stats`, `bch_ratelimit`, UUID buffers, and bio vectors. No disk state is written directly, but these helpers support sysfs and metadata paths that do persist data.

## Dependencies And Integration Points
It uses kernel bio/block APIs, ctype, seq/debugfs includes, scheduler clocks, vmalloc helpers, pages, and `util.h` macros. Callers include sysfs human-readable parsing/printing, superblock UUID validation, priority checksum generation through `bch_crc64()` in the header, and writeback rate limiting.

## Risks
`bch_bio_map()` directly manipulates bio internals and assumes an empty vector table with enough entries. Human-readable parsers use legacy `simple_strto*` helpers and must defend against overflow; suffix handling intentionally treats suffixes as powers of 1024. `bch_next_delay()` divides by the atomic rate, so callers must ensure the rate is nonzero. `bch_bio_alloc_pages()` allocates per-vector pages and must be paired with proper page freeing on all I/O completion paths.

## Test Signals
Unit-level tests should cover suffix parsing, overflow rejection, UUID text variants, zero-buffer detection, human-readable formatting for negative and large values, EWMA updates across first and later samples, ratelimit bounds, `bch_bio_map()` for direct and vmalloc buffers, and page-allocation unwind fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/util.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/util.h

## Purpose
`util.h` is bcache's shared utility header. It provides debug assertions, heap/FIFO/array allocator macros, safe parsing helpers, time-stat sysfs helpers, a ratelimit type, arithmetic helpers, rbtree search/insert macros, CRC64, a pseudo-exponential helper, and declarations for utility functions implemented in `util.c`.

## Important APIs, Types, And Functions
Debug behavior is controlled by `CONFIG_BCACHE_DEBUG` through `EBUG_ON()`, `atomic_dec_bug()`, and `atomic_inc_bug()`. Data-structure macros include `DECLARE_HEAP`, `init_heap`, `heap_add`, `heap_pop`, `DECLARE_FIFO`, `init_fifo`, `fifo_push/pop`, `fifo_move`, and `DECLARE_ARRAY_ALLOCATOR`. Numeric helpers include `ANYSINT_MAX`, `strtoi_h()`, `strtoul_safe()`, and `strtoul_safe_clamp()`. `struct time_stats` plus `sysfs_print_time_stats()` and attribute-list macros integrate timing stats with sysfs. `struct bch_ratelimit` stores `next` and atomic `rate`. `RB_INSERT`, `RB_SEARCH`, and `RB_GREATER` wrap common rbtree patterns. `bch_crc64()` computes the bcache metadata checksum flavor, and `fract_exp_two()` supports congestion scaling.

## Control Flow
Most helpers are statement-expression macros that allocate, mutate, or return from caller context. FIFO and heap macros expect the caller to provide storage structs generated by the declaration macros. Rbtree macros walk trees using caller-provided comparison functions and either link, search, or find the next greater node. Sysfs time macros compare `attr` against generated attribute names and emit scaled timing values.

## State And Persistence
The header owns no independent state, but many macros mutate caller-owned queues, heaps, rbtrees, atomics, and statistic structs. `bch_crc64()` is part of persistent metadata validation for bcache structures written by other files.

## Dependencies And Integration Points
It includes block, closure, errno, kernel, scheduler clock, llist, ratelimit, vmalloc, workqueue, and crc64 headers. It is a common dependency across bcache allocation, btree, sysfs, superblock, request, and writeback code.

## Risks
The macros are powerful and type-sensitive; side effects in arguments can be evaluated unexpectedly, and return-from-caller parsing macros must be used carefully. `fifo_pop_back()` relies on caller macro syntax and is easy to misuse. The rbtree macros depend entirely on correct comparison functions. Debug and non-debug builds have different assertion strength, so bugs may only crash with `CONFIG_BCACHE_DEBUG`.

## Test Signals
Build both debug and non-debug configurations. Exercise heap ordering, FIFO wraparound and exact sizing, array allocator exhaustion/reuse, rbtree insert/search/greater behavior, time-stat sysfs output, CRC64 compatibility with on-disk metadata, and `fract_exp_two()` bounds for congestion inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.c

## Purpose
`writeback.c` implements background writeback for dirty bcache data. It computes per-backed-device target dirty data, adjusts writeback rate, scans btrees for dirty keys, reads dirty extents from cache, writes them to backing devices in order, clears dirty bits in the btree, tracks dirty sectors by stripe, initializes dirty accounting after attach/recovery, and starts/stops writeback threads.

## Important APIs, Types, And Functions
Rate control is handled by `__calc_target_rate()`, `__update_writeback_rate()`, `idle_counter_exceeded()`, `set_at_max_writeback_rate()`, `update_writeback_rate()`, and `writeback_delay()`. I/O state is `struct dirty_io`, with callbacks `dirty_io_destructor()`, `write_dirty_finish()`, `dirty_endio()`, `write_dirty()`, `read_dirty_endio()`, and `read_dirty_submit()`. Dirty scanning uses `read_dirty()`, `dirty_pred()`, `refill_full_stripes()`, and `refill_dirty()`. Dirty accounting is exported through `bcache_dev_sectors_dirty_add()` and initialized through `bch_sectors_dirty_init()`, `bch_dirty_init_thread()`, and `bch_root_node_dirty_init()`. Public setup functions are `bch_cached_dev_writeback_init()` and `bch_cached_dev_writeback_start()`.

## Control Flow
When writeback starts, a workqueue and kthread are created, delayed rate updates are scheduled, and the thread is woken. The thread sleeps unless dirty data exists, writeback is enabled, or detach requires draining. It fills a key buffer with dirty btree keys, preferring full stripes when partial stripes are expensive. `read_dirty()` batches up to `MAX_WRITEBACKS_IN_PASS` contiguous keys and submits cache reads; each completion transitions to ordered backing writes using sequence numbers and a closure waitlist so writes reach the backing device in key order. `write_dirty_finish()` frees pages, clears dirty state by inserting clean keys into the btree, updates success/failure counters, deletes the keybuf entry, and releases in-flight capacity. When a full scan finds no dirty keys, the thread marks the backing device clean and writes its superblock; during detach it clears `set_uuid`, marks state `none`, writes synchronously, and exits.

## State And Persistence
Runtime state includes writeback rate controller fields, dirty keybuf, in-flight semaphore, ordering waitlist, delayed work flags, writeback kthread/workqueue, per-stripe dirty counters, full-stripe bitmap, `has_dirty`, and cache-set idle/max-rate flags. Persistent state changes occur when dirty data first appears (`BDEV_STATE_DIRTY`), when all dirty data is cleaned (`BDEV_STATE_CLEAN`), and when detach finishes (`BDEV_STATE_NONE` and zero set UUID). Clean-key insertion into the btree persists removal of dirty bits through normal journal/btree metadata.

## Dependencies And Integration Points
The file integrates bcache btree mapping/insertion, keybuf refill, cache and backing bio submission, closure scheduling, writeback sysfs tunables, cache-set GC, tracepoints, and superblock writes from `super.c`. It depends on `writeback.h` constants and helpers, `util.c` ratelimiting and bio allocation/mapping helpers, kernel kthreads, workqueues, semaphores, rwsems, and block bio APIs.

## Risks
Writeback is data-integrity critical. Cache read errors clear the key's dirty bit locally to avoid backing writes and count cache errors; backing write errors also alter key state and may leave data dirty or failed. Ordered writeback uses sequence counters and closure waits; ordering bugs could reorder overlapping writes. Dirty-sector accounting must stay balanced for negative and positive updates or writeback decisions and detach behavior become unsafe. The delayed rate work uses `BCACHE_DEV_RATE_DW_RUNNING` barriers to coordinate cancellation. Multi-threaded dirty initialization walks btree roots while managing cannibalize wait state; missed cleanup can corrupt wait lists.

## Test Signals
Run writeback-mode workloads with sequential, random, fragmented, and partial-stripe-expensive patterns. Verify dirty state transitions in backing superblocks, clean shutdown after detach, ordered overlapping writes, cache read failures, backing write failures, high cache utilization cutoff behavior, idle max-rate behavior, GC-after-writeback wakeups, dirty accounting after recovery, rate tunable changes from sysfs, delayed-work cancellation, and kthread/workqueue teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.h

## Purpose
`writeback.h` defines bcache writeback policy constants, dirty-initialization coordination structs, dirty-sector query helpers, writeback admission logic, queue helpers, dirty-state transition helpers, and exported function prototypes.

## Important APIs, Types, And Functions
Constants include default and maximum dirty cutoff thresholds, per-pass writeback limits, rate update limits, auto-GC threshold, fragmentation thresholds, maximum dirty-init threads, and `WRITEBACK_SHARE_SHIFT`. `struct bch_dirty_init_state` and `struct dirty_init_thrd_info` coordinate parallel dirty-sector initialization. `bcache_dev_sectors_dirty()` totals per-stripe dirty sectors. `offset_to_stripe()` maps a sector offset to a stripe and validates bounds. `bcache_dev_stripe_dirty()` checks whether a range intersects dirty stripes. `should_writeback()` decides whether a write should be cached dirty based on cache mode, detach state, cache utilization, discard operations, partial-stripe behavior, skip decisions, sync/meta/priority flags, and cutoff thresholds. `bch_writeback_queue()` wakes the writeback thread, and `bch_writeback_add()` marks a backing device dirty and persists that state.

## Control Flow
Request code can call `should_writeback()` during write handling. When dirty data is inserted, `bch_writeback_add()` atomically sets `has_dirty`, transitions the backing superblock to dirty if needed, writes that superblock, and wakes background writeback. Dirty accounting updates and initialization are implemented in `writeback.c`, while this header supplies inline fast paths used by request and writeback code.

## State And Persistence
The header mutates caller-owned `bcache_device` stripe counters and `cached_dev` dirty flags. `bch_writeback_add()` persists dirty state through `bch_write_bdev_super()`. Cutoff thresholds are external module parameters owned by `super.c`.

## Dependencies And Integration Points
It depends on bcache core types, bio operation flags, stripe arrays allocated in `super.c`, writeback thread fields initialized in `writeback.c`, and request-path cache-mode decisions. It also integrates with sysfs through the cutoff and rate constants exposed in `sysfs.c`.

## Risks
`offset_to_stripe()` reports invalid ranges and returns `-EINVAL`; callers must handle negative results. `bcache_dev_stripe_dirty()` walks stripes without separately checking the final stripe bound after increment, relying on valid request ranges. `should_writeback()` is central to writeback-mode safety; cutoff or detach mistakes can write dirty data when the cache should be bypassed or can bypass when writeback is expected. `bch_writeback_add()` writes the superblock asynchronously in a comment-marked weak spot.

## Test Signals
Test writeback admission for all cache modes, discard, sync/meta/priority writes, detaching devices, dirty full stripes, `would_skip`, and cache utilization across cutoff and sync cutoff thresholds. Verify dirty-state persistence when first dirty data is added and no wakeup occurs when the writeback thread is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/writeback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-audit.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-audit.c

## Purpose
`dm-audit.c` creates Linux audit records for Device Mapper control operations and I/O-related target events. It centralizes audit formatting for mapped-device targets.

## Important APIs, Types, And Functions
`dm_audit_log_start()` checks `audit_enabled`, opens an audit buffer with `audit_log_start()`, and writes the `module` and `op` fields. `dm_audit_log_ti()` logs target-instance events for `AUDIT_DM_CTRL` and `AUDIT_DM_EVENT`, deriving mapped-device major/minor numbers through `dm_table_get_md()` and `dm_disk()`. `dm_audit_log_bio()` logs bio-level events using the bio block device major/minor, sector, and result. Both public functions are GPL-exported.

## Control Flow
Callers pass an audit type, DM message prefix, operation string, target or bio, and result. If auditing is disabled or allocation fails, logging is skipped. Control events include task info and a success/error message from `ti->error`; event logs include device and sector fields. Each successful path appends `res=` and ends the audit record.

## State And Persistence
The file does not persist DM metadata and owns no long-lived state. Audit records are emitted to the kernel audit subsystem, which is external runtime/logging state.

## Dependencies And Integration Points
It depends on Linux audit APIs, Device Mapper core types, `dm-core.h`, block/bio helpers, and audit type constants such as `AUDIT_DM_CTRL` and `AUDIT_DM_EVENT`. The matching header provides no-op stubs when `CONFIG_DM_AUDIT` is disabled.

## Risks
Logging must not assume an audit buffer is available. `dm_audit_log_ti()` treats unexpected audit types as no-op, so misuse can silently omit records. The `error_msg` formatting uses `ti->error` when `result` is zero and `"success"` otherwise, so callers must pass result consistently with local conventions. Bio logging derives the device from `bio->bi_bdev`; remapped bios must pass the intended sector explicitly.

## Test Signals
Build with and without `CONFIG_DM_AUDIT`. Exercise DM target constructor/destructor and event wrappers with audit enabled/disabled, allocation failure injection, success and error results, and bio events on remapped devices. Validate audit log fields `module`, `op`, `dev`, `sector`, `error_msg`, and `res`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-audit.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-audit.h

## Purpose
`dm-audit.h` is the public Device Mapper audit interface. It exposes audit helpers when `CONFIG_DM_AUDIT` is enabled and compiles callers to empty inline stubs when disabled.

## Important APIs, Types, And Functions
When enabled, it declares `dm_audit_log_bio()` and `dm_audit_log_ti()`, and defines wrappers `dm_audit_log_ctr()`, `dm_audit_log_dtr()`, and `dm_audit_log_target()` for constructor, destructor, and target event logging. When disabled, all wrapper functions are inline no-ops with matching signatures.

## Control Flow
Target code calls the wrapper matching its operation. Enabled builds forward to `dm_audit_log_ti()` with `AUDIT_DM_CTRL` or `AUDIT_DM_EVENT`; disabled builds return immediately. The header intentionally discourages direct module use of `dm_audit_log_ti()` outside wrapper functions.

## State And Persistence
The header stores no state. It gates whether runtime audit records can be emitted by callers.

## Dependencies And Integration Points
It includes `linux/device-mapper.h` and `linux/audit.h` for target and audit type declarations. It is consumed by DM targets that need audit records without open-coding audit conditionals.

## Risks
Because disabled builds compile to no-ops, tests that only inspect functional DM behavior will not notice missing audit coverage. Wrappers rely on callers passing meaningful module prefixes, operation names, and result conventions. Signature drift with `dm-audit.c` would break enabled builds.

## Test Signals
Compile both enabled and disabled configurations. Verify wrapper calls from DM targets generate symbols only when enabled and impose no runtime side effects when disabled. Check static analysis for direct `dm_audit_log_ti()` use outside the intended wrapper layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v1.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v1.c

## Purpose
`dm-bio-prison-v1.c` implements the original Device Mapper bio prison: a range-keyed detention structure that serializes conflicting bios for thin-provisioning style targets. It also implements deferred sets used to delay work until prior shared-block reads complete, and it initializes both v1 and v2 prison slab caches from one module.

## Important APIs, Types, And Functions
`struct prison_region` contains a spinlock and rbtree; `struct dm_bio_prison` contains a mempool and hash-lock regions. `dm_bio_prison_create()`, destroy, alloc, and free manage the prison and cell pool. `cmp_keys()` compares virtual/physical range keys and treats overlapping ranges as equal. `dm_cell_key_has_valid_range()` enforces `BIO_PRISON_MAX_RANGE` and boundary rules. `dm_bio_detain()` inserts a new holder cell or appends an inmate bio to an existing overlapping cell. Release functions include `dm_cell_release()`, `dm_cell_release_no_holder()`, `dm_cell_error()`, and `dm_cell_visit_release()`. Deferred set APIs are `dm_deferred_set_create()`, `dm_deferred_entry_inc()`, `dm_deferred_entry_dec()`, and `dm_deferred_set_add_work()`.

## Control Flow
Callers preallocate a cell, build a `dm_cell_key`, and call `dm_bio_detain()`. The key hashes to a region lock, the rbtree is searched for an overlapping key, and either the caller becomes the holder or its bio is appended to the existing cell. When the holder completes, release removes the cell from the rbtree and returns the holder plus queued inmates, or only inmates for the no-holder variant. `dm_cell_error()` releases all detained bios with an error status. Deferred sets maintain a ring of entries; work is either run immediately when no entries are pending or linked to the current entry and swept when counts fall to zero.

## State And Persistence
All state is in-memory: rbtrees of detained cells, bio lists, mempool elements, spinlocks, and deferred work lists/counts. There is no disk persistence. Correctness is based on callers releasing cells and freeing preallocated cells according to whether insertion used them.

## Dependencies And Integration Points
The file integrates with DM core hash-lock sizing, DM thin metadata key types, block `bio_list`, mempool/slab allocation, spinlocks, rbtrees, and the v2 bio-prison implementation. It exports symbols for DM thin/cache targets and related modules.

## Risks
Range comparison treats overlap as equality, so callers must validate range size and boundary constraints or unrelated ranges can contend incorrectly. Release must use the same hashed region as insertion. The holder/inmate distinction is subtle and release variants differ. Deferred-set ring logic can delay work indefinitely if counts are leaked. Module init must unwind v1/v2 cache setup in reverse order on partial failure.

## Test Signals
Test non-overlapping, overlapping, boundary-crossing, and oversized keys; holder vs inmate returns; release with and without holder; error completion of queued bios; visit-and-release atomicity; mempool exhaustion behavior; hash-lock distribution; deferred set immediate/deferred/sweep behavior; and module init failure unwinding across v1 and v2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v1.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v1.h

## Purpose
`dm-bio-prison-v1.h` declares the v1 bio-prison API and deferred-set API for Device Mapper targets that must hold bios on conflicting virtual or physical block ranges.

## Important APIs, Types, And Functions
`struct dm_cell_key` identifies a virtual/physical range with `virtual`, `dev`, `block_begin`, and `block_end`. `BIO_PRISON_MAX_RANGE` and `BIO_PRISON_MAX_RANGE_SHIFT` define range limits. `struct dm_bio_prison_cell` is exposed so clients can preallocate/manage cell memory; it contains a client `user_list`, rbtree node, key, holder bio, and detained bio list. The header declares prison create/destroy, cell alloc/free, range validation, `dm_bio_detain()`, release/error/visit helpers, and deferred set create/destroy/inc/dec/add-work functions.

## Control Flow
Clients validate keys, allocate or provide a cell, call `dm_bio_detain()`, process the bio immediately if it became the holder, or wait for the holder to release the cell. Later they call a release helper to obtain bios that should be remapped or completed. Deferred-set clients increment an entry for reads they are waiting on and add work that should run only after relevant entries drain.

## State And Persistence
The header defines opaque prison state and caller-visible cell/deferred handles only. All state is runtime memory, and no DM metadata is persisted by this layer.

## Dependencies And Integration Points
It includes persistent-data block manager and thin metadata headers for `dm_block_t` and `dm_thin_id`, plus bio and rbtree headers. It is implemented by `dm-bio-prison-v1.c` and used by DM thin/cache code.

## Risks
The cell struct is not fully opaque because callers manage allocation, so layout changes can affect external users. Callers must obey range constraints and must compare return values to know whether they own the holder path. Deferred entries require balanced inc/dec. Misuse can leak bios, complete bios twice, or serialize too broad a range.

## Test Signals
Compile all DM clients against the header, check oversized range validation, verify caller-managed cell allocation/free rules, and test deferred set balancing under concurrent reads and deferred writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.c

## Purpose
`dm-bio-prison-v2.c` implements the newer Device Mapper bio prison with shared and exclusive lock levels. It allows bios to take shared locks unless blocked by an exclusive lock at an equal or higher level, supports quiescing before exclusive work, and returns detained bios when exclusive locks unlock.

## Important APIs, Types, And Functions
`struct dm_bio_prison_v2` holds a workqueue pointer, global spinlock, rbtree of cells, and cell mempool. Create/destroy and cell alloc/free wrap allocation. `cmp_keys()` treats overlapping ranges as equal. `__find_or_insert()` finds an overlapping cell or inserts a preallocated one. `dm_cell_get_v2()` grants or detains shared bio access. `dm_cell_put_v2()` drops shared counts and may erase/free a cell or queue a quiesce continuation. `dm_cell_lock_v2()` obtains an exclusive lock and reports whether existing shared holders must quiesce. `dm_cell_quiesce_v2()` queues or stores a continuation. `dm_cell_lock_promote_v2()` changes the exclusive level. `dm_cell_unlock_v2()` releases exclusive ownership, merges detained bios, and may return cell ownership to the caller.

## Control Flow
Shared callers pass a bio, lock level, key, and preallocated cell to `dm_cell_get_v2()`. If an exclusive lock blocks that level, the bio is added to the cell's detained list and the call returns false; otherwise the shared count is incremented. Exclusive callers call `dm_cell_lock_v2()`, which either inserts an exclusive cell, fails on an existing exclusive lock, or marks an existing shared cell exclusive and requests quiescing. When shared holders call `dm_cell_put_v2()`, the last one queues the stored continuation if an exclusive lock is waiting. Exclusive unlock merges detained bios to the caller and erases the cell if no shared users remain.

## State And Persistence
All state is runtime: rbtree cells, shared counts, exclusive flags/levels, detained bios, optional quiesce work, mempool elements, and a caller-supplied workqueue. There is no disk persistence.

## Dependencies And Integration Points
It depends on DM block/thin key types, bio lists, rbtrees, mempool/slab allocation, spinlocks, workqueues, and the v1 module init wrapper. It exports GPL symbols for DM targets requiring more nuanced lock semantics than v1.

## Risks
Comments note starvation and imperfect level tracking: shared locks granted above an exclusive level can starve exclusive work, and the code quiesces all shared locks because it does not know their levels. Callers must free cells only when return values transfer ownership. `quiesce_continuation` is a single pointer, so callers must not install conflicting continuations. The global lock is simpler than v1 region locks but can be hotter under contention.

## Test Signals
Test shared grants, shared denial under exclusive locks, exclusive lock insertion, `-EBUSY` on double-exclusive lock, quiesce continuation queuing after last shared put, promotion with and without shared holders, detained bio merge on unlock, cell ownership/free return values, overlapping and non-overlapping ranges, and mempool failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.h

## Purpose
`dm-bio-prison-v2.h` declares the v2 shared/exclusive bio-prison interface for Device Mapper targets. It exposes key and cell structures needed by callers that preallocate cells and coordinate lock state.

## Important APIs, Types, And Functions
`struct dm_cell_key_v2` identifies a virtual/physical block range. `struct dm_bio_prison_cell_v2` contains exclusive lock state, exclusive level, shared reference count, optional quiesce continuation, rbtree node, key, and detained bio list. The header declares v2 module init/exit helpers, prison create/destroy, cell alloc/free, shared `dm_cell_get_v2()`/`dm_cell_put_v2()`, exclusive `dm_cell_lock_v2()`, `dm_cell_quiesce_v2()`, `dm_cell_lock_promote_v2()`, and `dm_cell_unlock_v2()`.

## Control Flow
Callers create a prison with a workqueue, preallocate cells, take shared locks for normal bios, and take exclusive locks for operations that must block conflicting bios. Return values tell callers whether access was granted, whether quiescing is required, and whether cell ownership has returned and should be freed.

## State And Persistence
The header defines runtime synchronization state only. It does not persist DM metadata and does not own the workqueue passed at create time.

## Dependencies And Integration Points
It includes DM persistent-data/thin metadata types, bio, rbtree, and workqueue headers. The implementation is initialized from the v1 module and is used by DM components that need lock-level behavior.

## Risks
The exposed cell layout includes FIXME comments about packing and semantics; callers may accidentally rely on layout details. Lock-level behavior is subtle: shared locks above an exclusive level may still be granted, and unlock can occur while shared locks remain. Caller ownership of preallocated cells is determined by comparisons and boolean returns, so misuse can leak or double-free cells.

## Test Signals
Compile DM clients, run lock-level matrix tests, verify workqueue continuations fire exactly once, check ownership/free rules for every return path, and stress overlapping range operations under concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-prison-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-record.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bio-record.h

## Purpose
`dm-bio-record.h` provides tiny helpers for Device Mapper targets that need to resubmit a bio after lower block layers mutate it. It records and restores the mutable fields needed to retry a bio in its original state.

## Important APIs, Types, And Functions
`struct dm_bio_details` stores `bi_bdev`, `__bi_remaining`, `bi_flags`, `bi_iter`, `bi_end_io`, and optionally the block-integrity payload pointer. `dm_bio_record()` copies those fields from a bio into the details struct. `dm_bio_restore()` writes them back and resets the atomic remaining count.

## Control Flow
Before submitting a bio down a path that may fail and require retry, a target calls `dm_bio_record()`. If retry is needed, it calls `dm_bio_restore()` before resubmitting through another path. The helpers are inline and have no allocation or error return.

## State And Persistence
Only caller-owned stack or heap state is used. Nothing is persisted, and no global state exists. The restored fields affect subsequent block-layer processing of the same bio.

## Dependencies And Integration Points
It depends on `linux/bio.h` and optional `linux/blk-integrity.h`. It is used by DM targets such as multipath-style retry paths that must preserve the original iterator and completion callback.

## Risks
The helper records only selected mutable fields. If newer block-layer fields become relevant to resubmission, this header must be updated or retries may inherit mutated state. Restoring `__bi_remaining` and integrity payloads must match block-layer expectations. It should not be used after the bio lifetime has ended.

## Test Signals
Exercise DM retry paths with split/advanced bios, changed target block devices, altered end I/O callbacks, integrity-enabled bios, and multiple retry attempts. Verify the restored iterator covers the original range and completion happens once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bio-record.h -->
