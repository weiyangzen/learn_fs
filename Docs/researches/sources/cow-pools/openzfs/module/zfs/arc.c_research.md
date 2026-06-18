# File Research: sources/cow-pools/openzfs/module/zfs/arc.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8086, source bytes 262123, report `Docs/researches/chunks/chunk_sources_cow_pools_openzfs_module_zfs_arc_c_1_1_8086_74cfd49eec7d_research.md`
- chunk 2: lines 8087-11797, source bytes 116009, report `Docs/researches/chunks/chunk_sources_cow_pools_openzfs_module_zfs_arc_c_2_8087_11797_914698d03929_research.md`

## Chunk Research

### Chunk 1: lines 1-8086

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
- Important internal helpers include `buf_hash_find()/insert()/remove()`, `arc_change_state()`, `arc_access()`, `arc_evict_hdr()`, `arc_evict_state()`, `arc_evict()`, `arc_read_done()`, `arc_write_ready()`, `arc_write_done()`, `arc_buf_alloc_impl()`, `arc_hdr_alloc()/realloc()/destroy()`, and crypt/compression helpers such as `arc_buf_fill()`, `arc_fill_hdr_crypt()`, `arc_hdr_authenticate()`, and `arc_hdr_decrypt()`.

## State And Data Model

- The ARC is keyed by `(spa load guid, DVA identity, physical birth)` in `buf_hash_table`, using CityHash and 2048 striped hash locks.
- Seven ARC states are declared: `arc_anon`, `arc_mru`, `arc_mru_ghost`, `arc_mfu`, `arc_mfu_ghost`, `arc_l2c_only`, and `arc_uncached`. Active states use multilists by buffer content type (`ARC_BUFC_DATA`, `ARC_BUFC_METADATA`); `arc_l2c_only` has an index function that panics if anything is inserted because L2-only headers should not have L1 multilist membership.
- `arc_buf_hdr_t` tracks identity, flags, sizes, compression, L1/L2 header portions, raw encrypted ABDs, plaintext/physical ABDs, and linked `arc_buf_t` consumers. Full headers are allocated from `hdr_full_cache`; L2-only compact headers are allocated from `hdr_l2only_cache`.
- `arc_buf_t` is the consumer-facing buffer. A buffer may have private data or share the header's linear ABD, with strict invariants around `ARC_BUF_FLAG_SHARED`, `ARC_FLAG_SHARED_DATA`, compression, encryption, and list position.
- Memory accounting is split among data, metadata, bonus, dnode, dbuf, header, L2 header, raw, compressed, uncompressed, and overhead counters. State-local `arcs_size` tracks total state bytes; `arcs_esize` tracks evictable bytes.
- Tunables and targets include `arc_c`, `arc_c_min`, `arc_c_max`, `arc_meta`, `arc_pd`, `arc_pm`, `arc_dnode_limit`, `zfs_arc_max`, `zfs_arc_min`, `zfs_arc_eviction_pct`, `zfs_arc_no_grow_shift`, `arc_shrink_shift`, prefetch lifetimes, dirty-data percentages, and multiple L2ARC module parameters.
- Kstats are declared in `arc_stats`; fast-changing counters are maintained in `arc_sums` using `wmsum`/`aggsum` and projected by `arc_kstat_update()`.

## Control Flow

- L1 lookup path:
  - `arc_read()` rejects holes/redacted blocks, handles embedded block pointers specially, looks up the header in `buf_hash_table`, validates the block pointer, and separates L1 hits, in-flight I/O joins, ghost/L2 candidates, and true misses.
  - On an L1 hit, `arc_access()` updates MRU/MFU/prefetch state and `arc_buf_alloc_impl()` returns a caller buffer with compressed, encrypted, authenticated, or decompressed contents as requested.
  - On an in-flight hit, the caller either waits through an `arc_callback_t`, attaches a callback/dummy zio, or returns `ENOENT` for cached-only reads.
  - On a miss, the code allocates or rehydrates a header, inserts it into the hash table, marks `ARC_FLAG_IO_IN_PROGRESS`, allocates an ABD, optionally tries an L2ARC physical read, and otherwise issues `zio_read()`.
  - `arc_read_done()` records crypto metadata, byteswap state, compression level, allocates callback buffers, converts auth/decrypt checksum errors to I/O errors where needed, clears I/O-in-progress, removes the synthetic I/O reference, and invokes callbacks in original order.
- State transitions:
  - `arc_access()` moves anonymous buffers to MRU or uncached, promotes MRU to MFU after `ARC_MINTIME`, moves ghost hits back to MRU/MFU, updates ghost-hit sums, and treats L2-only headers as new MRU entries after reallocation.
  - `add_reference()` removes newly referenced headers from state multilists and evictable accounting; `remove_reference()` returns unreferenced headers to evictable lists or destroys anonymous/uncached headers.
  - `arc_change_state()` is the central accounting and multilist transition function. It also removes headers from the hash table when they become anonymous and synchronizes L2 state stats when an L2 header is present.
- Eviction and reclaim:
  - `arc_evict_hdr()` evicts L1 data from MRU/MFU/uncached states, moves MRU/MFU headers to ghost states, deletes ghost headers, or compacts L1+L2 headers to L2-only headers.
  - `arc_evict_state()` walks state multilists with marker headers and can dispatch parallel eviction work via `arc_evict_taskq`. It makes best-effort progress, skips hash-lock misses, and tracks real bytes freed for waiters.
  - `arc_evict()` balances metadata/data and MRU/MFU targets using recent ghost-hit feedback, prunes pinned dnodes when metadata is not evictable enough, and trims ghost-list sizes relative to active-state sizes.
  - `arc_reap_cb_check()` and `arc_reap_cb()` respond to memory pressure by reaping kmem/ABD/zstd caches and reducing `arc_c`.
  - `arc_wait_for_eviction()` classifies overflow as none/some/severe and either wakes the evict zthr or queues a condition-variable waiter keyed by `arc_evict_count`.
- Write path:
  - `arc_write()` prepares raw/compressed/encrypted zio properties, drops stale header ABDs, and issues `zio_write()` from the consumer buffer.
  - `arc_write_ready()` updates protected-data metadata, computes debug checksums, sets physical size/compression, and fills `b_pabd` or `b_rabd` by copying transformed data or sharing the user buffer when allowed.
  - `arc_write_done()` assigns final DVA/birth identity, inserts into the hash table, handles rewrite/nopwrite/dedup collisions, clears I/O-in-progress, accesses anonymous successful writes into ARC states, invokes the caller's done callback, and frees the write callback/ABD wrapper.
- Release and dirty-data throttling:
  - `arc_release()` makes a buffer anonymous before modification. It either reuses a single-buffer header or splits the buffer onto a new anonymous header when other buffers/references or L2ARC write constraints exist.
  - `arc_tempreserve_space()` can grow `arc_c` for large reservations, invokes platform memory throttling, and rejects transactions when total dirty/anonymous/pool dirty data exceed configured ARC fractions.
- Flush and prune:
  - `arc_flush()` and `arc_flush_async()` evict all evictable data for a spa load guid or globally. Async flushes are tracked in `arc_async_flush_list`.
  - Prune callbacks let ARC ask consumers such as dbuf/ZPL to drop externally pinned references when metadata pressure prevents eviction.

## Dependencies

- Internal OpenZFS subsystems: SPA/vdev config and load GUIDs, ZIO read/write/compression/checksum/encryption, ABD allocation and ownership, DMU object type/byteswap helpers, dbuf/dnode accounting, ZIL crypto MAC handling, txg dirty-data tracking, and ZFS ereports/debug logging.
- Kernel/SPL primitives: mutexes, condition variables, taskqs, zthr timers, kmem caches, kstats, lists, multilists, refcounts, atomics, `wmsum`, `aggsum`, DTrace probes, and platform memory-pressure hooks.
- Hashing/checksum libraries: CityHash for ARC hash distribution and Fletcher/ZFS checksum helpers for debug freeze verification and L2ARC validation.
- L2ARC integration in this chunk depends on `l2arc_dev_t`, L2 header fields, device buflists, L2 stats, and prototypes for later functions such as `l2arc_write_eligible()`, `l2arc_read_done()`, `l2arc_do_free_on_write()`, `l2arc_get_write_rate()`, persistence rebuild helpers, and log-block helpers.

## Notable Behavior

- ARC supports compressed ARC storage: `b_pabd` may contain the on-disk compressed representation, while consumer `arc_buf_t` objects can request compressed or decompressed views.
- Raw encrypted data is kept separately in `b_crypt_hdr.b_rabd`; plaintext/authenticated data may be materialized in `b_l1hdr.b_pabd`. Raw encrypted buffers are not shared.
- Authentication for authenticated-but-not-encrypted protected blocks is best effort and deferred until the key is available; `ARC_FLAG_NOAUTH` records unauthenticated data.
- Prefetch buffers have minimum lifetimes before eviction, with a longer lifetime for prescient prefetches.
- L2ARC reads use the existing header metadata and can allocate a padded I/O ABD when vdev physical size differs. If L2ARC read fails in synchronous mode, the path falls back to the main pool read.
- L2ARC writes can race header/data freeing, so ABD frees are deferred through `l2arc_free_on_write` when `HDR_L2_WRITING` is set.
- `arc_freed()` aggressively destroys cached headers for freed blocks when they have no active L1 references; otherwise it leaves them alive because in-flight I/O or dedup/dmu_sync cases may still hold references.

## Risks And Correctness Notes

- Header flag updates require either the hash lock or an undiscoverable header. Violating this rule can race cache lookup, eviction, read completion, or L2ARC state updates.
- State accounting is delicate: data may be owned by a header, by one or more buffers, or shared between them. Incorrect `ARC_BUF_SHARED`/`ARC_FLAG_SHARED_DATA` transitions can corrupt `arcs_size`, `arcs_esize`, compressed/uncompressed/overhead stats, or cause double-free/use-after-free.
- Lock ordering is explicit: callers must avoid taking hash locks while holding ARC list locks except with try-lock patterns. Eviction intentionally skips headers whose hash lock cannot be acquired.
- `arc_release()` has several special cases for multi-buffer headers, shared data, and L2ARC writes. These are high-risk because it moves a live consumer buffer to a new anonymous header while preserving accounting and debug checksums.
- Encryption and authentication errors are translated differently depending on speculative I/O, in-place dnode bonus decryption, and raw/authenticated requests. Mistakes can either leak plaintext or incorrectly fail reads when keys are absent.
- `arc_evict_state()` is best effort and may fail to evict enough due to lock misses or pinned buffers. Severe-overflow waiters rely on `arc_evict_count`, `arc_need_free`, and correct wakeups from the evict zthr.
- Hash table sizing is based on physical memory and `zfs_arc_average_blocksize`; extreme tunables or allocation failure shrink the table, affecting chain length and mutex contention.
- The chunk cutoff occurs before `arc_init()` completes, so startup ordering after `arc_dnode_limit` must be checked in the next chunk before reasoning about fully initialized globals, zthrs, taskqs, kstats, and dirty-data limits.

## Cross-Chunk References

- `arc_init()` continues after line 8086. The continuation applies tunings, initializes ARC states and hash caches, creates prune/evict/flush taskqs, installs kstats, allocates eviction markers, starts `arc_evict`/`arc_reap` zthrs, and sets dirty-data limits.
- `arc_fini()` is after this chunk and must be paired with the initialization paths summarized here to verify teardown ordering for taskqs, zthrs, markers, hash caches, kstats, states, and low-memory hooks.
- L2ARC functions declared or partially used here are implemented later: read completion, write eligibility, free-on-write draining, feed/write loops, trim/rate limiting, persistence rebuild/log-block read/write/restore, device attach/detach, and tunable module parameters.
- Platform memory helpers referenced here, such as `arc_default_max()`, `arc_available_memory()`, `arc_free_memory()`, `arc_all_memory()`, `arc_memory_throttle()`, `arc_lowmem_init()`, and `arc_register_hotplug()`, are outside this line range or platform-specific files.
- The later code must validate all module parameter registration and final L2ARC kstat fields referenced by this chunk's global tunables and `arc_kstat_update()`.

### Chunk 2: lines 8087-11797

# Chunk Research: sources/cow-pools/openzfs/module/zfs/arc.c lines 8087-11797

## Scope

This chunk starts inside `arc_init()` and covers ARC initialization tail, `arc_fini()`, the full explanatory comment and implementation core for L2ARC write/read/feed/rebuild/device lifecycle, exported ARC symbols, and ARC/L2ARC module parameters.

The first line is a continuation from the previous chunk: memory limit setup, `arc_c`, ARC metadata ratios, and `arc_dnode_limit` are established before line 8087. This chunk applies tunables, starts ARC/L2ARC services, then defines the L2ARC cache device machinery.

## APIs And Entry Points

- `arc_fini()` tears down low-memory hooks, flush task queues, ARC buffers, kstats, prune lists, eviction/reap threads, L2ARC free-on-write ABDs, buf caches, ARC state, and hotplug registration.
- L2ARC write/read callback path: `l2arc_write_done()`, `l2arc_untransform()`, `l2arc_read_done()`, and `l2arc_blk_fetch_done()` complete device I/O, update headers/statistics, validate checksums, decrypt/decompress as needed, and fall back to primary storage on bad L2ARC reads.
- L2ARC feed path: `l2arc_feed_thread()`, `l2arc_write_size()`, `l2arc_get_write_rate()`, `l2arc_dwpd_rate_limit()`, `l2arc_evict()`, `l2arc_write_buffers()`, and `l2arc_write_sublist()` select ARC buffers, evict overwrite regions, issue physical writes, and regulate feed interval/rate.
- L2ARC device lifecycle APIs: `l2arc_add_vdev()`, `l2arc_remove_vdev()`, `l2arc_rebuild_vdev()`, `l2arc_vdev_present()`, `l2arc_vdev_get()`, `l2arc_init()`, `l2arc_fini()`, `l2arc_spa_rebuild_start()`, and `l2arc_spa_rebuild_stop()`.
- Persistent L2ARC rebuild helpers: `l2arc_rebuild_dev()`, `l2arc_dev_rebuild_thread()`, `l2arc_rebuild()`, `l2arc_dev_hdr_read()`, `l2arc_log_blk_read()`, `l2arc_log_blk_restore()`, `l2arc_hdr_restore()`, `l2arc_log_blk_fetch()`, `l2arc_log_blk_fetch_abort()`, `l2arc_dev_hdr_update()`, `l2arc_log_blk_commit()`, `l2arc_log_blkptr_valid()`, `l2arc_log_blk_insert()`, and `l2arc_range_check_overlap()`.
- Pool-position marker helpers: `l2arc_get_list()`, `l2arc_sublist_lock()`, `l2arc_pool_has_devices()`, `l2arc_pool_markers_init()`, `l2arc_pool_markers_fini()`, `l2arc_get_state_size()`, `l2arc_flag_pass_reset()`, and `l2arc_reset_all_markers()`.
- Public integration at the end exports `arc_buf_size`, `arc_write`, `arc_read`, `arc_buf_info`, `arc_getbuf_func`, `arc_buf_destroy`, `arc_add_prune_callback`, and `arc_remove_prune_callback`; module params expose ARC sizing, eviction, prefetch, dnode, compression, and L2ARC feed/rebuild/endurance controls.

## Control Flow

ARC initialization tail applies tunings, clamps debug builds to a smaller target, registers hotplug handlers, initializes ARC states and buffer caches, creates prune/flush task queues, installs `arcstats`, starts eviction/reap zthreads, marks ARC cold, and derives `zfs_dirty_data_max`, `zfs_dirty_data_max_max`, and `zfs_wrlog_data_max` from memory/tunables. `arc_fini()` reverses this order carefully: it first stops low-memory and async flush activity, flushes all ARC buffers, deletes kstats and prune state, cancels zthreads, frees pending L2ARC ABDs before aggsums disappear, then runs `buf_fini()` before `arc_state_fini()` to avoid callbacks into freed ARC state.

L2ARC feed is per device. `l2arc_feed_thread()` sleeps until the next scheduled feed, exits if signaled or if the vdev is dead, takes `SCL_L2ARC` as reader, aborts under low-memory/header pressure, computes a target write size/rate, evicts the next overwrite span, writes selected buffers, adjusts the next interval based on actual bytes written, and releases the spa config lock.

Write selection prefers metadata and MFU before MRU data through `l2arc_get_list()`. `l2arc_write_buffers()` decides whether to use persistent per-pool markers based on total L2ARC capacity, resets markers after enough cumulative writes or scan depth, optionally skips metadata after repeated metadata-only cycles, round-robins multilists, and protects each sublist with busy flags so multiple L2ARC device threads avoid scanning the same sublist. `l2arc_write_sublist()` uses either persistent markers or head/tail scanning depending on ARC warmness, skips locked/ineligible buffers, bounds scan headroom, applies copy/compress/encrypt transforms if the L2ARC write cannot directly use the ARC ABD, records L2ARC metadata on the header, queues writes under a root zio, and periodically commits L2ARC log blocks.

Write completion in `l2arc_write_done()` walks headers inserted after a dummy head marker, retries when hash locks are unavailable to avoid leaving `ARC_FLAG_L2_WRITING` set, drops failed L2ARC entries and log block pointers, restores device-header log pointers on failure, frees temporary log-block ABDs, removes the dummy head, updates vdev space for dropped bytes, drains device-specific free-on-write ABDs, and frees the callback.

Read completion in `l2arc_read_done()` copies temporary read buffers into real ARC storage when needed, rewrites the zio block pointer to the cached BP copy, validates checksum, decrypts/decompresses through `l2arc_untransform()` unless raw encrypted data is being used, and hands successful reads to `arc_read_done()`. Bad checksum, transform error, I/O error, or concurrent L2 eviction causes stats updates and fallback to primary storage; async fallbacks update existing ARC callbacks with the new zio head.

Eviction in `l2arc_evict()` handles rotary wraparound, optional TRIM ahead, persistent evict-hand recording, log-block pointer reclamation, L2-only header destruction, L1-cached L2 metadata destruction, and marking in-flight L2 reads as evicted. Wraparound resets write/evict hands and DWPD counters when the first sweep finishes.

Persistent rebuild starts when `l2arc_rebuild_dev()` accepts an on-disk device header and marks the device pending, or schedules whole-device TRIM/new header if rebuild cannot proceed on a writable pool. `l2arc_spa_rebuild_start()` launches one rebuild thread per eligible spa cache vdev after import; stop/remove paths set cancel flags and wait. `l2arc_rebuild()` restores device hands/trim state from the header, walks the two interleaved log-block chains with one-block lookahead I/O, aborts on memory pressure, validates loop/eviction boundaries, reconstructs L2-only ARC headers via `l2arc_log_blk_restore()` and `l2arc_hdr_restore()`, records restored log-block pointers/stats, and logs success, disabled, no-valid-blocks, cancellation, or abort outcomes.

Device add/remove is explicit. `l2arc_add_vdev()` allocates `l2arc_dev_t`, reserves space after labels/header, initializes lists/refcounts/DWPD/feed-thread fields, reads or initializes rebuild state before publishing the device, initializes per-pool markers for the first device, updates capacity counters, and starts a named per-device feed thread for writable pools. `l2arc_remove_vdev()` cancels rebuild, stops the feed thread, removes the device from the global list under `SCL_L2ARC` writer protection, updates pool capacity/markers, and either tears down synchronously or queues asynchronous teardown when the pool is exported/destroyed.

## State And Dependencies

Key global/module state touched includes `arc_c`, `arc_c_min`, dirty/write-log maxima, `arc_warm`, `arc_stats`, ARC prune/flush task queues, eviction/reap zthreads, `l2arc_dev_list`, `l2arc_ndev`, `l2arc_free_on_write`, rebuild locks/CVs, and module tunables such as `l2arc_write_max`, `l2arc_dwpd_limit`, `l2arc_headroom`, `l2arc_meta_cycles`, `l2arc_ext_headroom_pct`, `l2arc_trim_ahead`, and `l2arc_rebuild_enabled`.

Per-device state mutated includes `l2ad_spa`, `l2ad_vdev`, `l2ad_start/end/hand/evict`, `l2ad_first`, `l2ad_writing`, `l2ad_trim_all`, DWPD counters, feed-thread flags/CV/lock, `l2ad_buflist`, log-block pointer list, log block assembly fields, allocation/log-block refcounts, `l2ad_rebuild*` flags, and the in-memory persistent device header.

Per-pool state under `spa->spa_l2arc_info` includes marker arrays for each feed pass/sublist, sublist busy/reset flags, next-sublist cursors, extended scan counters, total/smallest L2ARC capacity, and cumulative writes used to reset marker depth.

Dependencies span ARC header/list/refcount helpers, multilist sublists, ABD allocation/copy/free, ZIO physical read/write/root/wait, SPA config locks, vdev space accounting and TRIM, crypto key lookup and ABD encryption/decryption, compression/decompression, Fletcher checksums, kstats/history/debug logging, kernel thread/CV/mutex APIs, taskqs, and module-parameter registration macros.

## Risks And Cross-Chunk References

- This chunk begins mid-`arc_init()`; the function prologue, ARC sizing defaults, low-memory initialization, and parameter setter definitions are in chunk 1.
- Many L2ARC helpers rely on types, flags, tunables, stats, macros, and small helpers defined earlier in `arc.c`, including `arc_buf_hdr_t`, `l2arc_dev_t`, `l2arc_log_blk_phys_t`, `HDR_*`, `ARCSTAT_*`, `l2arc_free_abd_on_write()`, `arc_hdr_l2hdr_destroy()`, and log-block property macros.
- Lock ordering is delicate: several paths use `mutex_tryenter(HDR_LOCK())` while holding `l2ad_mtx` to avoid deadlock with writer selection; missed locks cause retries and stats bumps.
- `l2arc_write_done()` must always clear `ARC_FLAG_L2_WRITING`; failed lock acquisition paths deliberately reinsert the dummy head to resume where they left off.
- Temporary transformed ABDs are queued for free-on-write and drained after zio completion. Missing this would risk either use-after-free during physical writes or leaked ABDs.
- Persistent marker logic is shared across per-device feed threads; incorrect busy/reset flag handling could skip sublists indefinitely or cause repeated scanning of hot areas.
- DWPD rate limiting treats first-pass writes specially and resets at device wrap; capacity or time arithmetic errors could over-throttle or overrun endurance budgets.
- Persistent rebuild intentionally restores possibly stale L2-only headers; correctness depends on DVA plus birth TXG validation in ARC read paths outside this chunk.
- Rebuild cancellation depends on `l2arc_rebuild_thr_lock`/CV and spa config lock retry loops. Remove/export paths must set cancel before tearing down device memory.
- `l2arc_log_blkptr_valid()` and `l2arc_range_check_overlap()` encode rotary-buffer validity; off-by-one errors here can restore overwritten log blocks or discard valid ones.
- The exported symbols and module parameters integrate earlier ARC APIs and tunables with kernel/module users; several setter callbacks are declared outside this chunk.

## Summary

This chunk is the L2ARC operational core of OpenZFS ARC: it completes ARC startup/shutdown, implements per-device L2ARC feeding, write completion, read fallback, rotary eviction, persistent metadata logging, import-time rebuild, device add/remove, and exposes the relevant ARC/L2ARC tunables. The highest-risk areas are concurrency and lifetime management around ARC header locks, per-device lists, asynchronous zios, persistent rebuild cancellation, and rotary address validation.
