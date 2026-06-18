# Chunk Research: sources/cow-pools/openzfs/module/zfs/arc.c lines 1-8086

## Scope

This chunk covers the opening and core implementation of OpenZFS ARC (`module/zfs/arc.c`) in learn_fs subset A. It includes the ARC design notes, lock model, global tunables/statistics, buffer hash table, L1ARC buffer/header lifecycle, compressed/encrypted buffer transforms, state transitions, eviction/reclaim machinery, ARC read/write entry points, dirty-data throttling, kstat update logic, ARC state initialization/finalization helpers, and the beginning of `arc_init()`.

The chunk ends inside `arc_init()` immediately after computing `arc_dnode_limit`. Initialization continues after line 8086; this report does not cover the rest of module startup, final teardown, or most later L2ARC feed/rebuild/write code.

## APIs And Entry Points

- Buffer inspection and transform APIs: `arc_buf_size()`, `arc_buf_lsize()`, `arc_is_encrypted()`, `arc_is_unauthenticated()`, `arc_get_raw_params()`, `arc_get_compression()`, `arc_get_complevel()`, `arc_is_metadata()`, `arc_buf_thaw()`, `arc_buf_freeze()`, and `arc_untransform()`.
- Allocation and loan APIs: `arc_alloc_buf()`, `arc_alloc_compressed_buf()`, `arc_alloc_raw_buf()`, `arc_loan_buf()`, `arc_loan_compressed_buf()`, `arc_loan_raw_buf()`, `arc_return_buf()`, and `arc_loan_inuse_buf()`.
- Lifetime and mutation APIs: `arc_buf_destroy()`, `arc_release()`, `arc_released()`, `arc_freed()`, and debug-only `arc_referenced()`.
- I/O APIs: `arc_cached()`, `arc_read()`, `arc_getbuf_func()`, `arc_write()`, `arc_tempreserve_space()`, and `arc_tempreserve_clear()`.
- Cache management APIs: `arc_flush()`, `arc_flush_async()`, `arc_async_flush_guid_inuse()`, `arc_reduce_target_size()`, `arc_reclaim_needed()`, `arc_kmem_reap_soon()`, `arc_wait_for_eviction()`, `arc_add_prune_callback()`, `arc_remove_prune_callback()`, `arc_tuning_update()`, `arc_target_bytes()`, `arc_set_limits()`, and the opening of `arc_init()`.

## State And Data Model

- The ARC is keyed by `(spa load guid, DVA identity, physical birth)` in `buf_hash_table`, using CityHash and 2048 striped hash locks.
- Seven ARC states are declared: `arc_anon`, `arc_mru`, `arc_mru_ghost`, `arc_mfu`, `arc_mfu_ghost`, `arc_l2c_only`, and `arc_uncached`.
- `arc_buf_hdr_t` tracks identity, flags, sizes, compression, L1/L2 portions, raw encrypted ABDs, plaintext/physical ABDs, and linked `arc_buf_t` consumers.
- Memory accounting is split across data, metadata, bonus, dnode, dbuf, header, L2 header, raw, compressed, uncompressed, and overhead counters.
- Kstats are declared in `arc_stats`; fast-changing counters are maintained in `arc_sums` using `wmsum`/`aggsum`.

## Control Flow

- `arc_read()` handles L1 hits, in-flight I/O joins, ghost/L2 candidates, embedded block pointers, and true misses. Misses allocate or rehydrate headers, insert into the hash table, allocate ABD storage, optionally try L2ARC, then issue `zio_read()`.
- `arc_read_done()` records crypto and byteswap metadata, allocates callback buffers, converts auth/decrypt errors where needed, clears I/O-in-progress, removes the synthetic I/O reference, and invokes callbacks.
- `arc_access()` moves anonymous buffers to MRU/uncached, promotes MRU to MFU, handles ghost hits, and treats L2-only headers as new MRU entries after reallocation.
- `arc_evict_hdr()`, `arc_evict_state()`, and `arc_evict()` implement best-effort eviction, ghost-state movement, L2-only compaction, metadata/data balancing, dnode pruning, and waiter wakeups.
- `arc_write()` prepares raw/compressed/encrypted zio properties and issues `zio_write()`. `arc_write_ready()` fills header ABDs or shares data; `arc_write_done()` assigns final identity and inserts successful writes into the ARC.
- `arc_release()` anonymizes a buffer before modification, either reusing a single-buffer header or splitting it to a new anonymous header.
- `arc_tempreserve_space()` throttles dirty data based on ARC target, anonymous dirty bytes, pool dirty contribution, and platform memory pressure.

## Dependencies

- OpenZFS SPA/vdev, ZIO, ABD, DMU, dbuf/dnode, ZIL, txg dirty-data, crypto, checksum, and ereport subsystems.
- SPL/kernel primitives: mutexes, condition variables, taskqs, zthr timers, kmem caches, kstats, lists, multilists, refcounts, atomics, `wmsum`, `aggsum`, and DTrace probes.
- CityHash for ARC hash distribution and Fletcher/ZFS checksum helpers.
- L2ARC types and later functions including `l2arc_write_eligible()`, `l2arc_read_done()`, `l2arc_do_free_on_write()`, persistence rebuild helpers, and log-block helpers.

## Risks And Correctness Notes

- Header flag updates require either the hash lock or an undiscoverable header; violating this can race lookup, eviction, read completion, or L2ARC updates.
- Shared-buffer accounting is delicate. Incorrect `ARC_BUF_SHARED`/`ARC_FLAG_SHARED_DATA` transitions can corrupt state sizes or cause double-free/use-after-free.
- Eviction intentionally skips hash-lock misses and may fail to evict enough when buffers are pinned.
- `arc_release()` is high-risk because it moves a live consumer buffer while preserving accounting, checksums, sharing state, and L2ARC write constraints.
- Encryption/authentication paths differ for speculative I/O, in-place dnode bonus decryption, raw requests, and missing keys.
- The chunk cutoff occurs before `arc_init()` completes, so full startup ordering must be checked in the next chunk.

## Cross-Chunk References

- `arc_init()` continues after line 8086, applying tunings, initializing states/hash caches/taskqs/kstats/zthrs, and setting dirty-data limits.
- `arc_fini()` is later and must be paired with the initialization paths summarized here.
- Most L2ARC implementation is later: read completion, write eligibility, feed/write loops, trim/rate limiting, persistence rebuild/log blocks, device attach/detach, and module parameter registration.
- Platform memory helpers such as `arc_default_max()`, `arc_available_memory()`, `arc_free_memory()`, `arc_all_memory()`, `arc_memory_throttle()`, `arc_lowmem_init()`, and `arc_register_hotplug()` are outside this line range or platform-specific.