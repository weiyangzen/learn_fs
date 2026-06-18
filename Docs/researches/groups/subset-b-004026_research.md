# subset-b-004026 Research

Grouped research for device-mapper persistent cache, multipath path selectors, RAID targets, and region-hash code. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_segment.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_segment.c

## Purpose
Implements persistent-cache segment metadata management for `dm-pcache`. A cache segment wraps one physical cache-device segment, stores replicated segment-info records at the beginning of the segment, stores a replicated generation counter in the segment-control area, and exposes allocation/reference helpers used by cache writes, garbage collection, and key cleanup.

## Important APIs, Types, And Functions
The file operates on `struct pcache_cache_segment`, `struct pcache_segment_info`, `struct pcache_cache_seg_ctrl`, and `struct pcache_cache_seg_gen` from the pcache headers. `cache_seg_init()` initializes a segment either as new media or by loading existing metadata. `get_cache_segment()` finds and reserves a free cache segment in `cache->seg_map`. `cache_seg_get()` and `cache_seg_put()` maintain the segment reference count, and `cache_seg_set_next_seg()` persists segment chaining through `next_seg`.

Private helpers `cache_seg_info_write()` and `cache_seg_info_load()` maintain the metadata slot selected by `info_index`, increment the metadata sequence, calculate CRC with `pcache_meta_crc()`, and use `pcache_meta_find_latest()` on reload. `cache_seg_ctrl_write()`, `cache_seg_ctrl_load()`, and `cache_seg_gen_increase()` do the same for the segment generation record.

## Control Flow
Initialization calls `pcache_segment_init()` with data starting after the segment-info and control areas. For a newly formatted cache, `cache_seg_init()` zeroes the metadata/control ranges, writes an initial generation, writes segment info, and writes `pcache_empty_kset` at the data start to invalidate old key-set contents. For an existing cache, it loads the latest valid segment-info and generation entries before the segment can be used.

Allocation scans `cache->seg_map` from `cache->last_cache_seg`, wraps once, marks the found bit, and reports the cache as full if no zero bit exists. When the last reference is dropped, `cache_seg_put()` invalidates the segment by incrementing and persisting its generation, clears its bitmap bit, clears `cache_full`, wakes deferred requests, and queues `clean_work` so stale keys pointing at the old generation can be removed.

## State And Persistence
Persistent state is stored directly in pmem/DAX-mapped cache segments. The segment-info area uses `PCACHE_META_INDEX_MAX` alternating slots with CRC and sequence numbers; the control area persists the generation counter the same way. Writes use `memcpy_flushcache()` followed by `pmem_wmb()`, so crash recovery can select the latest complete record and ignore torn or corrupt metadata.

Volatile state includes the segment allocation bitmap, `last_cache_seg` search hint, `cache_full`, reference counters, `info_lock`, and `gen_lock`. The generation value is the core stale-reference guard: keys that name an old generation become invalid after the segment is recycled.

## Dependencies And Integration Points
This file depends on `cache_dev.h` for cache-device address layout and zeroing, `cache.h` for key-set metadata and work items, `segment.h` for generic segment initialization, and `dm_pcache.h` for logging and deferred-request wakeups. It integrates with the cache write path through segment allocation and references, with garbage collection through invalidation and `clean_work`, and with replay/recovery through persisted segment metadata.

## Risks
Metadata slot ordering and CRC logic are high-risk because a wrong `info_index` or generation slot can resurrect stale keys after crash recovery. `get_cache_segment()` assumes the segment bitmap is authoritative and protected by `seg_map_lock`; a missed bit clear can permanently reduce capacity, while a premature clear can allow overwrite of referenced data. `cache_seg_ctrl_write()` intentionally avoids locking based on single-threaded access assumptions, so future callers must not introduce concurrent generation writes without revisiting that contract.

## Test Signals
Useful signals include format and reload tests that verify segment info/generation survives remount, forced corruption of one metadata slot to confirm the alternate slot is chosen, write/read tests across segment reuse, cache-full/deferred-request recovery tests, and GC tests that confirm old-generation keys are removed after `cache_seg_put()`. Persistent-memory fault tests should exercise `copy_mc_to_kernel()` and CRC rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_segment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_writeback.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_writeback.c

## Purpose
Implements asynchronous writeback for dirty `dm-pcache` key sets. It walks the persisted dirty-tail stream, decodes each key set, issues writes from cache pmem into the backing device, and advances the persisted dirty tail only after all writes for that key set complete and the backing device is flushed.

## Important APIs, Types, And Functions
`cache_writeback_init()` initializes a one-subtree `writeback_key_tree`, clears the pending count, and queues `writeback_work`. `cache_writeback_exit()` cancels work, flushes the backing device, and destroys the tree. `cache_writeback_fn()` is the delayed-work state machine. `cache_key_writeback()` converts a dirty cache key into one or more `pcache_backing_dev_req` writes. `cache_wb_tree_writeback()` submits all decoded keys and tracks completion through `writeback_ctx`.

Helper `is_cache_clean()` reads the current dirty tail into `wb_kset_onmedia_buf`, checks `PCACHE_KSET_MAGIC` and CRC, and treats unreadable or invalid data as clean/no-work. `last_kset_writeback()` handles a terminal key set by moving `dirty_tail` to the next cache segment.

## Control Flow
The worker exits early if a previous writeback batch is still pending or the pcache target is stopping. Otherwise it snapshots `cache->dirty_tail`, reads a key set, and either backs off for `PCACHE_CACHE_WRITEBACK_INTERVAL` if the cache appears clean, advances to the next segment if the key set is marked `PCACHE_KSET_FLAGS_LAST`, or decodes all keys into the writeback RB tree.

For a normal key set, each non-clean key is written back in chunks no larger than `backing_dev_req_coalesced_max_len()`, which avoids crossing incompatible devmap pages in vmalloc-backed pmem mappings. `writeback_ctx.pending` starts at one sentinel reference, each backing request increments it, and each completion calls `writeback_ctx_end()`. The final completion flushes the backing device, advances and persists `dirty_tail`, and immediately requeues the worker.

## State And Persistence
Persistent state is the dirty-tail cache position encoded by `cache_encode_dirty_tail()` after successful writeback. Cached key sets and data remain in the pmem segment log until GC/segment reuse. Volatile state includes `writeback_ctx.pending`, `writeback_ctx.ret`, `writeback_ctx.advance`, `writeback_key_tree`, and the reusable key-set buffer.

Writeback is conservative: any request error is latched, dirty-tail advancement is skipped, and the worker retries later from the same persistent dirty tail. The backing device is flushed before the dirty tail is persisted, maintaining writeback ordering across crashes.

## Dependencies And Integration Points
The file depends on `cache.h` for key decoding, cache positions, CRC helpers, and workqueue access; `backing_dev.h` for request creation/submission and flush; `cache_dev.h` for pmem address helpers; and `dm_pcache.h` for stop-state/logging. It is paired with the dirty-key append path and cache GC: writeback makes key sets safe to clean, while GC can reclaim after dirty-tail progress.

## Risks
Treating unreadable or invalid key-set metadata as clean avoids an infinite loop but can hide metadata loss; with dirty data this can become data loss. Pending-count ordering is critical because dirty-tail advancement must happen exactly once and only after all writes finish. The code assumes a key fits within the remaining segment (`BUG_ON(seg_remain < key->len)`), so corrupt metadata can crash the kernel. Retry behavior can spin forever on persistent backing errors unless higher layers surface and manage the fault.

## Test Signals
Test writeback with multiple keys per key set, key sets spanning different pmem page mappings, backing write failures, backing flush failures, and target teardown while work is pending. Crash tests should verify that data written but not dirty-tail-advanced is replayed, and data whose dirty tail advanced is present on the backing device. Status output should show dirty-tail progress over sustained writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_writeback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/dm_pcache.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/dm_pcache.c

## Purpose
Defines the `pcache` device-mapper target. It parses the target table, opens cache and backing devices, starts the cache-device/backing-device/cache subsystems, maps bios into `pcache_request` objects, handles temporary `-EBUSY` deferral, exposes status and messages, and registers/unregisters the target module.

## Important APIs, Types, And Functions
The public target callbacks are `dm_pcache_ctr()`, `dm_pcache_dtr()`, `dm_pcache_map_bio()`, `dm_pcache_status()`, and `dm_pcache_message()` in `dm_pcache_target`. Module setup calls `pcache_backing_init()`, `pcache_cache_init()`, and `dm_register_target()`.

Request lifetime is managed by `pcache_req_get()` and `pcache_req_put()` around the per-bio `struct pcache_request`. Deferred work is handled by `defer_req()`, `pcache_defer_reqs_kick()`, `defered_req_fn()`, and `defer_req_stop()`. Argument parsing is split into `parse_cache_dev()`, `parse_backing_dev()`, and `parse_cache_opts()`.

## Control Flow
Construction rejects table loading for a live mapped device, allocates `struct dm_pcache`, creates a per-target workqueue, parses `<cache_dev> <backing_dev> [options]`, and starts `cache_dev`, `backing_dev`, then `pcache_cache` in dependency order. The target advertises one flush bio, flush support, and `per_io_data_size = sizeof(struct pcache_request)`.

Mapping initializes the per-bio request with byte offset and length, increments `inflight_reqs`, and calls `pcache_cache_handle_req()`. A normal return completes through `pcache_req_put()`. `-EBUSY` places the request on `defered_req_list`; deferred work retries until the cache can accept it or teardown forces `-EIO`. Destruction marks the target stopping, drains deferred requests, waits for all in-flight requests, stops subsystems in reverse order, releases devices, drains/destroys the workqueue, and frees the context.

## State And Persistence
This file owns target-level volatile state: target pointer, cache/backing/cache subobjects, options, deferred-request list, target workqueue, `state`, `inflight_reqs`, and waitqueue. Persistent cache metadata is managed by the cache-device and cache layers, not directly here. The `state` atomic gates deferred processing and writeback so teardown does not accept new background work.

Status reports cache-device flags, segment counts, used segment count, GC percent, cache flags, and key/dirty-tail positions for `STATUSTYPE_INFO`; `STATUSTYPE_TABLE` emits reconstructable table arguments with cache mode and CRC option. The `gc_percent` message updates runtime GC threshold through `pcache_cache_set_gc_percent()`.

## Dependencies And Integration Points
The target integrates with device-mapper core APIs, `dm_get_device()`/`dm_put_device()`, per-bio target data, target status/message hooks, and block flush support. It depends on pcache submodules `cache_dev`, `backing_dev`, and `cache`; the cache layer is the actual I/O policy engine. The singleton target feature means only one live table instance is supported.

## Risks
The constructor forbids live table reloads, so operational workflows depending on table replacement are unsupported. Request refcounting and `inflight_reqs` must stay balanced across direct completion, deferred retry, and teardown; otherwise teardown can hang or complete a bio twice. The deferred-list spelling is consistent but easy to misread. Only `cache_mode writeback` is accepted despite table/status vocabulary that hints at more modes.

## Test Signals
Exercise valid/invalid table arguments, cache/backing device open failures, subsystem start failure unwinds, normal reads/writes/flushes, cache-full `-EBUSY` deferral and later wakeup, target removal under load, and `gc_percent` messages. `dmsetup status` should show coherent segment/key-tail fields and `dmsetup table` should round-trip the configured devices and CRC option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/dm_pcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/dm_pcache.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/dm_pcache.h

## Purpose
Declares the top-level `dm-pcache` target context and per-bio request object shared between the target front end and cache/backing/cache-device layers. It also centralizes container conversions, target state constants, request reference APIs, deferred-request wakeup, and target-scoped logging macros.

## Important APIs, Types, And Functions
`struct dm_pcache` embeds `pcache_cache_dev`, `pcache_backing_dev`, `pcache_cache`, and `pcache_cache_options`, plus the device-mapper target pointer, deferred-request list/work item, workqueue, state, in-flight request counter, and waitqueue. `struct pcache_request` stores the originating `bio`, byte offset, data length, request refcount, latched return code, and list node for deferral.

Macros `CACHE_DEV_TO_PCACHE`, `BACKING_DEV_TO_PCACHE`, and `CACHE_TO_PCACHE` provide ownership lookup. `PCACHE_STATE_RUNNING` and `PCACHE_STATE_STOPPING` define target lifecycle states, while `pcache_is_stopping()` is used by background workers to stop safely. `pcache_req_get()`, `pcache_req_put()`, and `pcache_defer_reqs_kick()` are implemented in `dm_pcache.c`.

## Control Flow
The header is included by pcache submodules that need to reach the containing target for logging, stop-state checks, or request completion. A bio becomes a `pcache_request` in the target map callback, is passed to cache handling, may be queued on the deferred list, and finally completes through `pcache_req_put()`.

## State And Persistence
All declarations here describe volatile in-memory state. Persistent state is held by the embedded cache device mapping and cache metadata structures declared elsewhere. The request `ret` field latches the first nonzero error so asynchronous pieces can report a single final bio status.

## Dependencies And Integration Points
The header depends on the device-mapper public API and `dm-core.h`. It is the glue between the DM target, cache-device code, backing-device request code, and cache policy/data code. Logging macros prefix messages with the mapped device name through `pcache->ti->table->md->name`.

## Risks
Because `struct dm_pcache` embeds major subsystem objects directly, include ordering and forward declarations must stay consistent with the actual complete type definitions. Request refcount misuse in any submodule can break target teardown because `dm_pcache.c` waits on `inflight_reqs`. The state check is a simple atomic equality test, so callers must still coordinate their own queues and work cancellation.

## Test Signals
Build coverage is the main signal for this header. Runtime signals include clean target teardown with no in-flight hang, correct logging prefixes from all submodules, and correct bio completion after asynchronous cache/backing activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/dm_pcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/pcache_internal.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/pcache_internal.h

## Purpose
Provides shared low-level helpers for `dm-pcache`: logging macros, size constants, metadata header layout, CRC calculation, sequence comparison, and mirrored metadata-slot selection. It is the common persistence integrity layer used by superblock/cache-info/segment metadata code.

## Important APIs, Types, And Functions
`struct pcache_meta_header` stores a CRC, 8-bit sequence number, version byte, and reserved field at the start of pcache metadata records. `pcache_meta_crc()` computes CRC32C over a metadata object excluding the CRC field. `pcache_meta_seq_after()` compares 8-bit sequence numbers using signed wraparound arithmetic. `pcache_meta_find_latest()` scans `PCACHE_META_INDEX_MAX` copies, rejects CRC failures, selects the latest valid sequence, and copies the winning record into a caller buffer.

The file defines `PCACHE_KB`, `PCACHE_MB`, `PCACHE_META_INDEX_MAX`, and `PCACHE_CRC_SEED`, plus `pcache_err/info/debug` macros that include function and line.

## Control Flow
Callers pass the address of the first metadata header, the actual metadata size, the slot stride, and a destination buffer to `pcache_meta_find_latest()`. The helper uses `copy_mc_to_kernel()` for each slot so pmem machine-check faults are converted to `-EIO`. After choosing the newest valid slot it copies that slot into the destination and returns the source address; callers derive the active slot index from that address.

## State And Persistence
This header defines the persistent metadata envelope but stores no state itself. Its design assumes two alternating metadata slots, each independently checksummed and sequenced. Crash recovery can tolerate one torn slot if the other slot remains valid.

## Dependencies And Integration Points
It depends on Linux delay and CRC32C helpers and on pmem-safe copying through `copy_mc_to_kernel()`. Segment metadata, cache-device superblocks/cache-info, cache-tail positions, and segment generation records all use this contract. The logging macros are reused across the pcache implementation.

## Risks
The sequence comparison works only within half the 8-bit sequence space; if metadata updates wrap far enough between reads, latest-slot selection can become ambiguous. `pcache_meta_crc()` assumes the CRC field is the first four bytes and the caller supplies the exact object size. Any new metadata record that does not embed `pcache_meta_header` first will silently compute the wrong checksum.

## Test Signals
Unit-style tests should cover CRC rejection, single-slot corruption, sequence wraparound near 255-to-0, machine-check copy failure handling, and records where slot stride is larger than record size. Integration tests should verify that pcache reload chooses the latest metadata copy after simulated torn writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/pcache_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/segment.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/segment.c

## Purpose
Implements generic data movement between a pcache segment's pmem data area and block-layer bios, plus segment object initialization. It is the low-level copy layer beneath cache hits, cache fills, and writes into the persistent cache.

## Important APIs, Types, And Functions
`segment_copy_to_bio()` copies from `segment->data + data_off` into a bio iterator using `_copy_mc_to_iter()` so pmem read faults can be detected. `segment_copy_from_bio()` copies from a bio iterator into the segment using `_copy_from_iter_flushcache()` and persists with `pmem_wmb()`. `pcache_segment_init()` sets segment info type, owning cache device, physical segment id, data size, and data pointer according to `struct pcache_segment_init_options`.

## Control Flow
Both copy functions build an `iov_iter` from the current bio vector state and advance it by `bio_off` when requested. They require the low-level copy to transfer exactly `data_len`; otherwise they return `-EIO`. Initialization computes the usable data region as `PCACHE_SEG_SIZE - data_off`, allowing cache-specific segment headers/control areas to live before user data.

## State And Persistence
The copy-to-bio path reads persistent memory but does not mutate state. The copy-from-bio path writes into the DAX/pmem mapping with cache-line flushes and a write memory barrier, making data durable before upper metadata points to it. The segment object itself is volatile and points into the cache-device mapping.

## Dependencies And Integration Points
The file depends on Linux DAX/iov iterator helpers, `pcache_internal.h`, `cache_dev.h`, and `segment.h`. Higher cache request code uses these functions to serve reads from cache and populate cache data from writes or backing reads. Segment type metadata is defined in `segment.h` and later persisted by cache-segment code.

## Risks
The functions trust callers to pass valid offsets and lengths within the segment data area. Bio iterator setup depends on the current `bi_iter` fields, so incorrect `bio_off` can copy the wrong range. Partial copies are reported as `-EIO`, but already-written bytes may remain in pmem; callers must publish metadata only after successful full writes.

## Test Signals
Exercise copies with multi-segment bios, nonzero `bio_off`, boundary-length requests, pmem copy faults, and writes followed by reload/readback. Tests should verify that metadata is not committed when `segment_copy_from_bio()` returns an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/segment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/segment.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/segment.h

## Purpose
Declares the generic pcache segment metadata and in-memory segment view. It provides flag/type helpers, segment-position arithmetic, copy APIs, and initialization options shared by the cache segment and request code.

## Important APIs, Types, And Functions
`struct pcache_segment_info` is the persistent segment header containing `pcache_meta_header`, flags, and `next_seg`. `PCACHE_SEG_INFO_FLAGS_HAS_NEXT` records segment chaining, and `PCACHE_SEG_INFO_FLAGS_TYPE_MASK` stores the segment type, currently `PCACHE_SEGMENT_TYPE_CACHE_DATA`. `struct pcache_segment` holds the cache device, data pointer, data size, segment id, and pointer to the associated segment info.

Inline helpers include `segment_info_has_next()`, `segment_info_set_type()`, `segment_info_get_type()`, and `segment_pos_advance()`. The header declares `segment_copy_to_bio()`, `segment_copy_from_bio()`, and `pcache_segment_init()`.

## Control Flow
Cache code creates a `pcache_segment_init_options` object with a physical segment id, type, data offset, and segment-info pointer, then calls `pcache_segment_init()` to derive the usable data window. Segment positions advance monotonically within `segment->data_size` and fail fast via `BUG_ON()` if callers overrun.

## State And Persistence
`pcache_segment_info` is persistent when written by cache-segment code; `pcache_segment` and `pcache_segment_pos` are volatile views. The `next_seg` field links cache segments in on-media order, which is used during replay/writeback/GC to walk the cache log.

## Dependencies And Integration Points
The header depends on block bio types, bitfield helpers, and `pcache_internal.h`. It is included by segment copy code, cache segment metadata code, and cache key/data paths that need to move positions or inspect segment types.

## Risks
Segment type and `has_next` share the same flags word, so future flags must avoid overlapping `PCACHE_SEG_INFO_FLAGS_TYPE_MASK`. `segment_pos_advance()` uses `BUG_ON()` instead of returning an error, making metadata corruption or caller arithmetic bugs fatal. There is no bounds checking in the copy API declarations; callers must enforce it.

## Test Signals
Build tests should catch type/flag helper changes. Runtime tests should cover segment chaining, end-of-segment advancement, replay of `next_seg`, and copy operations at exact segment-data boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-pcache/segment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-historical-service-time.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-ps-historical-service-time.c

## Purpose
Implements the `historical-service-time` multipath path selector. It estimates future path latency from an exponentially weighted moving average of completed service time plus outstanding I/O count, and includes staleness probing logic so paths that have not completed I/O recently are not permanently ignored.

## Important APIs, Types, And Functions
The selector registers a `struct path_selector_type` named `historical-service-time` with `DM_PS_USE_HR_TIMER`. `struct selector` tracks valid/failed path lists, valid count, precomputed EMA weights, and a threshold multiplier. `struct path_info` stores a path pointer, repeat count, per-path lock, fixed-point historical service time, stale deadline, last finish time, and outstanding request count.

Important helpers are `fixed_power()`, `fixed_ema()`, `hst_set_weights()`, `hst_compare()`, `hst_select_path()`, `hst_start_io()`, and `hst_end_io()`. Creation accepts optional `base_weight` and `threshold_multiplier`; path addition accepts optional `repeat_count`.

## Control Flow
On selection, the selector locks the valid list, compares every valid path against the current best using current time, historical service time, outstanding count, and stale deadline, then moves the selected path to the tail for tie fairness. `start_io` increments the path outstanding count. `end_io` computes elapsed service time from the supplied high-resolution start timestamp, serializes overlapping completions using `last_finish`, updates the fixed-point EMA using the precomputed weight bucket, decrements outstanding, and refreshes the stale deadline.

Failed and reinstated paths are moved between valid and failed lists under selector lock. Status reports global table args and per-path historical service time/outstanding/stale state.

## State And Persistence
All state is in memory and reset when the table is loaded or the module is reloaded. The selector maintains no on-disk persistence. The EMA uses 10-bit fixed-point arithmetic and time buckets of about 16 ms to avoid expensive exponentiation on every completion.

## Dependencies And Integration Points
It integrates with the DM multipath path-selector API from `dm-path-selector.h`; the multipath core calls `select_path`, `start_io`, and `end_io` around each mapped I/O. It uses `ktime_get_ns()` and the high-resolution timing feature flag so `start_time` passed to `end_io` is meaningful.

## Risks
Arithmetic overflow is mitigated but still a key risk in the outstanding-count and fixed-point service-time calculations. The threshold multiplier can make latency differences disappear if configured too high. Stale-path handling intentionally probes unused paths, which can send I/O to a degraded path. Correctness also depends on balanced `start_io`/`end_io` calls; an underflow in `outstanding` would distort all future choices.

## Test Signals
Test with paths of different latency, intermittent idleness, failures/reinstatements, and high queue depth. Status should show historical service time changing after completions and stale deadlines refreshing. Module load should log version `0.1.1`, and table parsing should reject invalid fixed-point weights or extra arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-historical-service-time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-io-affinity.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-ps-io-affinity.c

## Purpose
Implements the `io-affinity` multipath path selector. It maps CPUs to paths using user-supplied cpumasks so I/O issued on a CPU prefers the path associated with that CPU, falling back to NUMA-local and then any available mapped path when necessary.

## Important APIs, Types, And Functions
`struct selector` contains a per-CPU `path_map`, a `path_mask` of CPUs with mappings, and a `map_misses` counter. `struct path_info` contains the `dm_path`, parsed cpumask, refcount, and failed flag. The selector callbacks are `ioa_create()`, `ioa_destroy()`, `ioa_add_path()`, `ioa_fail_path()`, `ioa_reinstate_path()`, `ioa_select_path()`, and `ioa_status()`.

## Control Flow
Creation allocates the selector, an array sized to `nr_cpu_ids`, and a mask of mapped CPUs. Each path must provide one cpumask argument; for each CPU in the mask, the selector installs the path if no mapping already exists and increments the path context refcount. Selection pins the current CPU with `get_cpu()`, checks the direct CPU mapping, then scans CPUs on the same NUMA node, then all mapped CPUs. Failed paths are skipped. Missing direct mappings increment `map_misses`.

Destroy iterates mapped CPUs and drops path references through `ioa_free_path()`, freeing a path context only when the last CPU mapping for it is removed.

## State And Persistence
State is entirely volatile: CPU-to-path mappings, path masks, per-path failed flags, and the map-miss counter. There is no service-time or queue-depth history and no persistent metadata.

## Dependencies And Integration Points
The selector integrates with DM multipath through `dm-path-selector.h` and with kernel CPU topology through cpumasks, `cpu_to_node()`, and `cpumask_of_node()`. Userspace must supply cpumask strings in the table path arguments, and status emits the table cpumask via `%*pb`.

## Risks
There is no explicit lock around `path_map` lookup or `failed` flag updates, relying on multipath path-selector call context and simple boolean updates. CPU hotplug/topology changes after table load can make mappings suboptimal. Duplicate CPU mappings are ignored with a warning, so table order silently decides ownership. A path with an empty or out-of-range mask fails to add.

## Test Signals
Test cpumask parsing, duplicate mappings, missing CPU mappings, failed-path fallback, reinstate behavior, and NUMA-local fallback. `map_misses` should increase only when the current CPU has no direct mapping. Table status should reproduce the cpumask for each path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-io-affinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-queue-length.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-ps-queue-length.c

## Purpose
Implements the `queue-length` multipath path selector. It chooses the valid path with the fewest in-flight I/Os and uses list rotation to spread ties across paths.

## Important APIs, Types, And Functions
`struct selector` holds valid and failed path lists protected by a spinlock. `struct path_info` stores the `dm_path`, repeat count, and atomic in-flight I/O count `qlen`. The registered selector callbacks are `ql_create()`, `ql_destroy()`, `ql_add_path()`, `ql_fail_path()`, `ql_reinstate_path()`, `ql_select_path()`, `ql_start_io()`, `ql_end_io()`, and `ql_status()`.

## Control Flow
Path addition parses an optional repeat count, deprecates values above one by forcing them to one, allocates path context, and appends the path to the valid list. Selection scans valid paths under lock, stops early when it finds a zero-queue path, moves the selected path to the tail, and returns the associated `dm_path`. `start_io` increments `qlen`; `end_io` decrements it. Failure and reinstate move path contexts between lists under lock.

## State And Persistence
The only dynamic metric is the atomic in-flight request count per path. Lists and counts are reset on table reload. There is no persistent state and no history of latency or throughput.

## Dependencies And Integration Points
The file integrates with DM multipath through the path-selector registration API. The multipath core is responsible for calling start/end hooks around I/O so `qlen` remains accurate. Status exposes the current `qlen` in `STATUSTYPE_INFO` and repeat count in `STATUSTYPE_TABLE`.

## Risks
If the multipath core or an error path misses `end_io`, a path can be permanently penalized. The metric counts requests, not bytes, so large and small bios are weighted equally. Atomic reads during selection can race completions but are acceptable for heuristic load balancing. Repeat-count compatibility remains in the table grammar but no longer changes behavior above one.

## Test Signals
Test balanced selection at equal queue depth, preference for lower queue depth, fail/reinstate list movement, and start/end balancing under errors. Status should show `qlen` rising under outstanding I/O and returning to zero after completion. Module load should register version `0.2.0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-queue-length.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-round-robin.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-ps-round-robin.c

## Purpose
Implements the classic `round-robin` multipath path selector. It cycles through currently valid paths in list order, moving the selected path to the tail after each selection.

## Important APIs, Types, And Functions
`struct selector` contains valid and invalid path lists protected by a spinlock. `struct path_info` stores the `dm_path` and repeat count. The selector callbacks are `rr_create()`, `rr_destroy()`, `rr_add_path()`, `rr_fail_path()`, `rr_reinstate_path()`, `rr_select_path()`, and `rr_status()`. The module registers `rr_ps` as `round-robin`, version `1.2.0`.

## Control Flow
Path addition accepts at most one repeat-count argument, warns that values above one are deprecated, and appends the path to the valid list. Selection takes the first valid path, moves it to the end of the valid list, and returns it. Failure moves a path to the invalid list; reinstatement moves it back to the valid list.

## State And Persistence
State is limited to volatile path lists and configured repeat counts. There are no in-flight counters, timing metrics, or persistent records.

## Dependencies And Integration Points
The file depends on the DM path-selector API and Linux module infrastructure. It is loaded by DM multipath when a table references `round-robin`; the multipath core owns path-group policy, I/O submission, and failure notification.

## Risks
Round-robin ignores path speed, queue depth, CPU locality, and request size, so it can perform poorly on asymmetric hardware. The deprecated repeat-count field remains visible in status but is clamped to one for values above one. List operations require correct failure/reinstate sequencing from multipath core.

## Test Signals
Test path cycling order, empty-valid-list behavior, fail/reinstate transitions, argument parsing, and table status round-trip. Under equal healthy paths, selected path sequence should rotate deterministically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-round-robin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-service-time.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-ps-service-time.c

## Purpose
Implements the `service-time` multipath path selector. It estimates service time as current in-flight byte load plus incoming request size divided by a user-configured relative throughput value, then selects the path with the lowest estimate.

## Important APIs, Types, And Functions
`struct selector` holds valid and failed path lists protected by a spinlock. `struct path_info` contains the `dm_path`, repeat count, relative throughput, and atomic in-flight byte count. Key functions are `st_add_path()`, `st_compare_load()`, `st_select_path()`, `st_start_io()`, `st_end_io()`, and `st_status()`. The selector table accepts optional per-path `repeat_count` and `relative_throughput` in the range 0 to 100.

## Control Flow
Selection scans valid paths and compares each candidate with the current best. If throughputs match, it chooses lower in-flight bytes; if load is equal or one path has throughput zero, it chooses higher throughput; otherwise it avoids division by comparing cross-multiplied service-time estimates and shifts down very large values to avoid overflow. The selected path is moved to the tail for tie fairness. `start_io` adds `nr_bytes` to `in_flight_size`, and `end_io` subtracts it.

## State And Persistence
All state is volatile and rebuilt on table load. The selector maintains a byte-weighted current load per path but no historical latency and no persistent state. A relative throughput of zero keeps a path from being selected while positive-throughput alternatives are available.

## Dependencies And Integration Points
It integrates with DM multipath path-selector hooks and relies on the multipath core to pass request byte size to select/start/end callbacks. Status exposes current in-flight bytes and relative throughput for monitoring and table reconstruction.

## Risks
The in-flight byte counter is an `atomic_t`, so very large or many concurrent requests can overflow on platforms where `int` is narrower than `size_t`. Incorrect start/end balancing permanently skews load. The throughput value is manually configured and can misrepresent actual path performance. Overflow mitigation in comparison preserves heuristic behavior but reduces precision at extreme loads.

## Test Signals
Test asymmetric throughput choices, zero-throughput paths, equal-load tie rotation, fail/reinstate, and high in-flight byte values near overflow thresholds. Status should show in-flight bytes changing with outstanding bios and table output should preserve configured throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ps-service-time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-raid.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-raid.c

## Purpose
Implements the modern `raid` device-mapper target backed by the MD RAID personalities. It supports raid0, raid1, raid10, raid4/5/6 variants, optional raid4/5/6 journal devices, rebuilds, resync controls, bitmap region sizing, grow/shrink, reshape, and level takeover while exposing a DM table/status/message interface.

## Important APIs, Types, And Functions
`struct raid_set` is the target context and embeds an `mddev`, selected `raid_type`, runtime/constructor flags, rebuild bitmap, requested layout parameters, optional journal device, and flexible array of `struct raid_dev` members. `struct raid_dev` pairs a metadata device, data device, and `md_rdev`. `struct dm_raid_superblock` is the dm-raid on-disk metadata format, including v1.9 reshape extensions.

Major functions include `raid_ctr()`/`raid_dtr()`, `raid_map()`, `raid_status()`, `raid_message()`, `raid_preresume()`, `raid_resume()`, and suspend hooks. Parsing and validation are split across `parse_raid_params()`, `parse_dev_params()`, `validate_region_size()`, `validate_raid_redundancy()`, `rs_check_takeover()`, and `rs_check_reshape()`. Superblock handling is implemented by `super_load()`, `super_validate()`, `super_init_validation()`, `super_sync()`, and `analyse_superblocks()`. Reshape/takeover flow uses `rs_prepare_reshape()`, `rs_setup_reshape()`, `rs_start_reshape()`, `rs_setup_takeover()`, and size/offset helpers.

## Control Flow
Construction parses `<raid_type> <#raid_params> ... <#raid_devs> <meta data>...`, allocates `raid_set`, parses target options, opens all component devices, computes requested array/device sizes, analyzes superblocks to recover current state, decides whether the table represents a new set, recovery, reshape continuation, takeover, reshape request, grow/shrink, or unchanged set, then initializes and starts the embedded MD array suspended/frozen. RAID I/O is mapped by handing bios to `md_handle_request()`, with requeue for addresses past current MD array size during forward grow reshape.

Resume-time work is important: `raid_preresume()` updates superblocks when needed, loads/resizes the MD bitmap, applies grow capacity, sets recovery windows, and starts requested reshape. `raid_resume()` unfreezes MD recovery and writes, and on secondary resume attempts to restore previously faulty devices. Suspend freezes sync changes, prepares interrupted raid456 reshape if needed, stops writes, suspends MD, and marks the array read-only.

## State And Persistence
Persistent state lives in dm-raid superblocks on metadata devices. The superblock stores magic, compatible feature flags, device count/position, event counter, failed-device bitmap, per-disk recovery offset, array resync offset, level/layout/chunk, reshape flags and position, new layout/chunk/delta, array sectors, data offsets, rdev sectors, and extended failed-device bits. `super_sync()` writes little-endian metadata from current `mddev`/`md_rdev` state.

Volatile state includes constructor flags, runtime flags such as prereresumed/resumed/bitmap-loaded/update-superblocks/reshape/grow/frozen, MD recovery flags, bitmap state, journal mode, and target capacity. The target carefully separates constructor-requested new layout from superblock-current layout until it can decide whether a conversion is legal.

## Dependencies And Integration Points
The target integrates deeply with MD core (`mddev`, `md_rdev`, personalities, bitmaps, recovery thread, reshape APIs), RAID personalities (`raid1`, `raid5`, `raid10`), DM target registration through `module_dm(raid)`, DM table events/status/messages, and block queue limits. Userspace integration is through documented target table parameters and messages such as `frozen`, `idle`, `resync`, `recover`, `check`, and `repair`.

## Risks
This is a high-risk control-plane file: wrong parsing or flag validation can permit unsafe RAID layouts; wrong superblock selection can assemble stale or incompatible arrays; and reshape/grow data-offset mistakes can overwrite live data. The code explicitly disables some operations for degraded, recovering, reshaping, or journaled sets, and those checks must remain conservative. Discard support for raid456 is disabled unless the module parameter asserts safe zeroing semantics. Status and table output must remain userspace-compatible because tools reconstruct arrays from it.

## Test Signals
Coverage should include each RAID level/layout, metadata and metadata-less tables, invalid flag combinations, rebuild paths, failed-device re-add, bitmap loading/resizing, suspend/resume, status/table round-trip, messages for sync actions, raid456 journal modes, grow/shrink, reshape with data offsets, and takeover validation. Fault injection should cover superblock read errors, stale events, failed devices, degraded arrays, interrupted reshape, and discard behavior with `devices_handle_discard_safely` both false and true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-raid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-raid1.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-raid1.c

## Purpose
Implements the legacy `mirror` device-mapper target. It mirrors writes to multiple devices, chooses readable mirrors for reads, tracks dirty/no-sync regions through a dirty log and region hash, performs background recovery with kcopyd, and supports user-visible error handling features.

## Important APIs, Types, And Functions
`struct mirror_set` is the target context with bio queues, region hash, kcopyd and dm-io clients, recovery state, error flags, workqueue/timer, and mirror array. `struct mirror` stores device, offset, error count/type, and parent pointer. The target callbacks are `mirror_ctr()`, `mirror_dtr()`, `mirror_map()`, `mirror_end_io()`, suspend/resume hooks, `mirror_status()`, and `mirror_iterate_devices()`.

Core helpers include `fail_mirror()`, `mirror_flush()`, `recover()`, `do_recovery()`, `choose_mirror()`, `do_reads()`, `do_writes()`, `do_failures()`, and the worker `do_mirror()`. `create_dirty_log()` constructs a core or disk dirty log, and `parse_features()` handles `handle_errors` and `keep_log`.

## Control Flow
Writes are queued to the mirror worker. The worker updates region states, starts recovery work, dispatches reads, classifies writes by region state, flushes the dirty log, writes clean/dirty regions to all mirrors through dm-io, delays writes to recovering regions, and writes no-sync regions only to the default mirror when allowed. `mirror_end_io()` decrements pending region counts for writes.

Reads to in-sync regions can be remapped directly to a selected mirror; reads to not-yet-synced regions are queued. Failed reads restore the original bio and retry another mirror if possible. Recovery asks the region hash for quiesced regions, copies from the default mirror to all other mirrors with kcopyd, and marks regions recovered or failed. Error handling can hold bios and trigger DM table events so userspace can reconfigure.

## State And Persistence
Persistent synchronization state is owned by the dirty log implementation passed in the table; `dm-region-hash` caches dirty/no-sync/recovering regions in memory and writes state through the log. Volatile state includes queued bios, current default mirror, per-mirror error bits, in-sync/log-failure/leg-failure flags, suspend flag, timer state, and recovery-in-flight.

`keep_log` changes persistence/error semantics: with handled errors and kept logs, failed writes may be failed rather than allowing log state to be cleared. Without handled errors, some failures can be reported as success after marking regions no-sync, relying on later recovery.

## Dependencies And Integration Points
The target depends on dm-io for replicated I/O, dm-kcopyd for recovery copies, dm-dirty-log for persistent sync state, dm-region-hash for region state and delayed bios, dm-bio-record for read retry, and device-mapper target APIs. It registers as target `mirror` with atomic-write support and uses a global `dm_raid1_wq` for table-event work plus per-target `kmirrord` workqueues.

## Risks
The mirror target has intricate concurrency around worker queues, pending region counts, suspend, and recovery stopping. Misordered region-hash updates can mark data clean before all mirror writes are durable. Using `bio->bi_next` to stash a mirror pointer is delicate and valid only before lower-layer submission. Error handling semantics are subtle: the wrong combination of `handle_errors`, `keep_log`, and log failure can either hang bios awaiting userspace or acknowledge data that is not replicated.

## Test Signals
Test normal mirrored reads/writes, read retry after one leg fails, write failure with and without `handle_errors`, `keep_log` behavior, dirty-log flush failures, recovery after out-of-sync regions, suspend/resume during recovery, noflush suspend requeue, discard handling, and status characters `A/F/D/S/R`. Persistent tests should reload with disk logs and confirm dirty regions recover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-raid1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-region-hash.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-region-hash.c

## Purpose
Provides the shared region-state engine used by the mirror target. It maps sectors/bios to dirty-log regions, caches nontrivial region states in a hash table, tracks pending writes, coordinates recovery quiescing, delays bios that conflict with recovery, and updates the persistent dirty log.

## Important APIs, Types, And Functions
`struct dm_region_hash` holds region size/shift, dirty log, hash buckets, locks, flush-failure flag, recovery semaphore/count, clean/quiesced/recovered/failed lists, mempool, callbacks, and target begin sector. `struct dm_region` stores key, state, hash/list nodes, pending count, and delayed bios.

Exported APIs include `dm_region_hash_create()`, `dm_region_hash_destroy()`, `dm_rh_dirty_log()`, `dm_rh_bio_to_region()`, `dm_rh_region_to_sector()`, `dm_rh_get_state()`, `dm_rh_inc_pending()`, `dm_rh_dec()`, `dm_rh_mark_nosync()`, `dm_rh_update_states()`, `dm_rh_recovery_prepare()`, `dm_rh_recovery_start()`, `dm_rh_recovery_end()`, `dm_rh_recovery_in_flight()`, `dm_rh_flush()`, `dm_rh_delay()`, `dm_rh_stop_recovery()`, and `dm_rh_start_recovery()`.

## Control Flow
Writes call `dm_rh_inc_pending()` to allocate/find each region, transition clean regions to dirty, and mark them in the dirty log. Completion calls `dm_rh_dec()`, which moves zero-pending dirty regions to the clean list, recovering regions to the quiesced list, or leaves no-sync regions resident. The mirror worker periodically calls `dm_rh_update_states()` to remove clean/recovered regions from the hash, clear or update log state, dispatch delayed bios, release recovery slots, and flush the dirty log.

Recovery starts with `dm_rh_start_recovery()` seeding the recovery semaphore. `dm_rh_recovery_prepare()` asks the dirty log for resync work, marks selected regions recovering, and either waits for pending writes to drain or places already-quiesced regions on the quiesced list. The caller starts I/O for regions returned by `dm_rh_recovery_start()` and later calls `dm_rh_recovery_end()` with success/failure, which queues the region for state update and wakes workers.

## State And Persistence
The hash is an in-memory cache of regions that are dirty, no-sync, recovering, recently clean, or awaiting recovered processing. Persistent state is delegated to `struct dm_dirty_log` operations: `mark_region`, `clear_region`, `set_region_sync`, `get_resync_work`, `flush`, and `in_sync`. A flush failure sets `flush_failure`, preventing later write completions from being marked clean because durability is uncertain.

Locking is split between `hash_lock` for bucket membership and `region_lock` for state/list/delayed-bio fields. A recovery semaphore limits parallel recovery to `max_recovery`, and `recovery_in_flight` lets suspend wait until recovery callbacks have fully dispatched delayed bios.

## Dependencies And Integration Points
This module exports GPL symbols used by `dm-raid1.c` and any other DM target using dirty-log region recovery. It depends on `dm-dirty-log.h`, `dm-region-hash.h`, bio lists, vmalloc buckets, mempools, spin/rw locks, semaphores, and caller-provided callbacks to dispatch delayed bios and wake workers/waiters.

## Risks
The state machine is concurrency-sensitive: regions move among hash buckets and clean/quiesced/recovered lists under different locks, and callers must pair pending increments/decrements exactly. `dm_rh_delay()` appends to a region's delayed list under only the hash read lock, relying on region lifetime and caller sequencing. Flush failure handling is intentionally pessimistic; clearing it incorrectly could lose mirrored consistency. Destroy asserts no quiesced regions and no pending writes, so teardown ordering must be correct.

## Test Signals
Test region-size mapping, dirty-to-clean transitions, no-sync marking on write/flush failure, delayed bios during recovery, recovery success and failure paths, max-recovery throttling, stop/start recovery during suspend/resume, dirty-log operation failures, and hash races under concurrent writes to the same region. Mirror-target recovery tests are the main integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-region-hash.c -->
