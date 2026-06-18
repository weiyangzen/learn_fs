# Research: subset-b-009697

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_helpers.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_helpers.c

## Purpose
`mdcache_helpers.c` implements the central helper behavior for the MDCACHE stackable FSAL: cache-entry creation, keyed lookup, export mapping, parent-handle caching, directory-entry caching, chunked and uncached readdir, and final invalidation/attribute update helpers. It is the main bridge between lower FSAL object handles and the in-memory MDCACHE entry model.

## Important APIs, Types, and Functions
- `mdcache_new_entry()` creates or finds an MDCACHE entry for a lower FSAL handle, handles hash races, initializes directory/file state, copies attributes, inserts the entry into LRU, and releases duplicate lower handles through `merge()`/`release()`.
- `mdcache_find_keyed_reason()` looks up a cache key in the cache inode hash, takes an LRU reference, and ensures the active export mapping is valid.
- `mdcache_locate_host()` converts a host handle into a lower-FSAL key, tries the cache, otherwise creates a lower handle and caches it.
- `mdc_lookup()` and `mdc_lookup_uncached()` implement name lookup, including cached dirent lookup, negative-cache trust, lower-FSAL lookup on miss, and parent `..` special handling.
- `mdcache_dirent_add()`, `mdcache_dirent_remove()`, `place_new_dirent()`, `mdcache_dirent_invalidate_all()`, and `mdcache_clean_dirent_chunk()` maintain directory AVL indexes, chunk lists, detached dirent LRU lists, and trust flags.
- `mdcache_readdir_uncached()`, `mdcache_populate_dir_chunk()`, and `mdcache_readdir_chunked()` drive directory enumeration with either direct lower-FSAL callbacks or chunked cache population.
- `mdc_check_mapping()`, `mdc_clean_entry()`, `mdc_get_parent()`, and `mdc_get_parent_handle()` manage per-export entry ownership and cached parent handles.
- `_mdcache_kill_entry()` removes an entry from the cache hash and queues deferred cleanup if outstanding references remain.
- `mdc_update_attr_cache()` preserves and replaces owned ACL, fs_locations, and sec_label payloads while updating trust metadata.

## Control Flow
Cache entry creation starts by deriving a lower-FSAL key from `handle_to_key()`, probing the cache hash, then allocating/reusing an LRU entry only after a cache miss. The final insertion is protected by a cache hash latch so racing creators either win insertion or discard their provisional entry and merge the lower-FSAL handle into the existing object.

Lookup first tries cached directory content under `content_lock`. If the dirent cache is trusted, `mdc_try_get_cached()` resolves by cached key and can serve negative results when the directory is marked fully populated and export options allow negative cache trust. On stale/missing cache state and when uncached lookup is allowed, the path upgrades to a write lock, invalidates stale dirent structures if needed, calls the lower FSAL `lookup()`, and caches the result.

Chunked readdir keeps a directory content lock while walking resident chunks. Missing chunks are populated through lower-FSAL `readdir()` callbacks that create MDCACHE entries and dirents. The code handles readahead, gaps, chunk collisions, reloads when keyed entries are missing, and FSALs whose readdir cursor is a name rather than an opaque cookie. The callback path avoids promoting scan-created entries into the hot LRU path, preserving scan resistance.

Entry cleanup removes all export mappings under the documented lock order, invalidates directory content, removes hash-table membership, releases owned attributes/keys, and leaves final object release to LRU cleanup.

## State and Persistence Behavior
All cache state is in memory. Persistent filesystem state is not changed except via lower-FSAL calls made elsewhere; this file caches metadata and object identity. `mde_flags` track trust in attributes, ACLs, content, directory chunks, fs_locations, sec_label, and unreachable state. Directory state includes AVL trees by name, cookie, and sorted cookie order, resident `dir_chunk` lists, detached dirents, parent host-handle cache, and `first_ck`. Parent handles expire according to lower export parent-expire policy. Attribute timestamps and `expire_time_attr` govern cache validity.

## Dependencies and Integration Points
This file depends on `mdcache_lru` for entry/chunk references and recycling, `mdcache_hash` for keyed entry lookup, `mdcache_avl` for dirent indexes, `fsal_commonlib` and lower-FSAL object/export ops for handle conversion, lookup, readdir, release, merge, and close, plus SAL state helpers and dynamic metrics. `subcall` and `supercall` macros from `mdcache_int.h` switch `op_ctx->fsal_export` between MDCACHE and the lower FSAL.

## Risks and Edge Cases
The main risks are lock-order regressions, reference leaks across chunk population, stale export mappings during unexport, FSAL cookie collisions, name/cookie inconsistencies in fast-mutating directories, and incorrect trust-flag transitions. Readdir paths are especially sensitive: dropping `content_lock` can invalidate dirent/chunk pointers, whence-is-name mode may force rescans, and chunk reload logic must avoid double-unref or stale `mde_entry` references. Attribute update code must preserve ownership of ACL/fs_locations/sec_label payloads exactly once.

## Test Signals
Useful tests include concurrent lookup/create races for one object, unexport while handles are being looked up, readdir of large and mutating directories with chunking enabled, FSALs with and without `fso_compute_readdir_cookie` and `fso_whence_is_name`, negative lookup caching under trusted and untrusted directory states, stale lower handles during readdir, ACL/fs_locations/sec_label refreshes, and parent `..` lookup across export roots.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_int.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_int.h

## Purpose
`mdcache_int.h` is the internal contract for the MDCACHE FSAL. It defines the cache entry, export wrapper, cache key, LRU metadata, directory chunk/dirent structures, trust flags, stackable-FSAL call macros, helper prototypes, and inline cache-validity utilities used by the MDCACHE implementation.

## Important APIs, Types, and Functions
- `struct mdcache_fsal_export` wraps `struct fsal_export`, stores MDCACHE upcall vectors, export entry lists, unexport flags, dirmap state, and cleanup counters.
- `mdcache_key_t` combines a hash value, lower FSAL identity, and lower-FSAL handle bytes; `mdcache_key_cmp()` orders keys by hash, length, FSAL pointer, and bytes.
- `mdcache_lru_t` stores queue membership, refcounts, active-refcounts, lane, flags, and confounder for both entries and chunks.
- `struct mdcache_fsal_obj_handle` is the cache entry: FSAL object handle, lower handle, attributes/timestamps, hash key, export mappings, LRU state, content lock, and type-specific state.
- `struct dir_chunk` and `mdcache_dir_entry_t` model chunked directory cache content.
- Inline helpers include `test_mde_flags()`, `mdc_export()`, `mdc_cur_export()`, `mdcache_key_dup/delete()`, parent-handle helpers, `mdc_fixup_md()`, `mdcache_test_attrs_trust()`, `mdcache_is_attrs_valid()`, `mdc_has_state()`, and `mdc_unreachable()`.
- Function prototypes expose lookup, readdir, object creation, I/O, xattr, handle ops, export ops, and upcall initialization.

## Control Flow
The header defines the state model used by other files rather than executing a top-level flow. The key inline paths are attribute refresh and validation: `mdc_fixup_md()` sets trust flags and refresh times based on requested and valid masks, while `mdcache_is_attrs_valid()` checks trust, valid bits, expiry, directory invalidation policy, and delegation conditions before allowing cached attributes to satisfy a request.

The stackable FSAL macros redirect `op_ctx->fsal_export` for lower-FSAL calls (`subcall*`) and for callbacks back into the upper layer (`supercall*`). Entry removal flow is also encoded here: `mdc_unreachable()` kills an entry immediately when it has no state, otherwise marks it `MDCACHE_UNREACHABLE` for later cleanup.

## State and Persistence Behavior
All structures represent volatile in-memory cache state. Entry state persists only for the lifetime of the Ganesha process or until LRU/unexport invalidation. The header documents lock ownership: `attr_lock` protects attributes, export mappings, and attribute times; `content_lock` protects directory/symlink cached content; LRU metadata has its own lane locking; `mde_flags` are updated atomically. Directory parent host handles and attribute timestamps are cached with expiry.

## Dependencies and Integration Points
The header includes FSAL, SAL state, upcall, conversion, display, and utility headers. It is consumed by MDCACHE helpers, LRU, main module wiring, config, upcall handling, and handle/export ops outside this subset. The prototypes connect this subset to other MDCACHE files such as open/read/write, xattr, export ops, AVL/hash logic, and NFS state/delegation code.

## Risks and Edge Cases
Because this header defines shared invariants, mismatches in lock discipline or refcount assumptions can corrupt many call paths. Risks include comparing FSAL pointers as key-order components, stale `first_export_id`, incorrect attribute trust when `expire_time_attr` is zero, parent-handle lifetime errors, and state-bearing unreachable entries that must not be freed prematurely.

## Test Signals
Test signals include assertions or stress tests for attr/content lock order, cache-key ordering and duplication/freeing, attribute validity with ACL/fs_locations/sec_label masks, directory parent expiration, unreachable entries with open/lock/delegation state, and stackable FSAL context restoration around nested lower-FSAL and upper-layer callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_lru.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_lru.c

## Purpose
`mdcache_lru.c` implements MDCACHE memory management: constant-time multi-lane LRU queues for entries and directory chunks, entry/chunk reference accounting, background demotion/release workers, export-aware cleanup, FD-cache integration, and dirmap eviction for whence-is-name readdir support.

## Important APIs, Types, and Functions
- `struct lru_q` and `struct lru_q_lane` implement per-lane L1, L2, cleanup, and active queues.
- `mdcache_lru_pkginit()` initializes LRU state, queues, fridge worker threads, and FD LRU parameters; `mdcache_lru_pkgshutdown()` stops workers and destroys queues.
- `mdcache_lru_get()` returns a newly allocated or recycled cache entry with sentinel and active references; `mdcache_lru_insert_active()` places a constructed entry on the active queue.
- `_mdcache_lru_ref()` and `_mdcache_lru_unref()` are the public ref/unref backends, handling active references, promotion, sentinel release, cleanup, final free, and pool accounting.
- `mdcache_lru_release_entries()` reaps reachable-but-idle entries while above high water.
- `mdcache_get_chunk()`, `_mdcache_lru_ref_chunk()`, `_mdcache_lru_unref_chunk()`, `lru_bump_chunk()`, and chunk reaping functions manage directory chunk cache memory.
- `mdc_lru_map_dirent()`, `mdc_lru_unmap_dirent()`, `dirmap_lru_init()`, and `dirmap_lru_stop()` maintain bounded cookie-to-name restart maps per export.

## Control Flow
Entries move among active, L1, L2, cleanup, and none states. Active references move entries to the active queue. When the final active reference is dropped, `make_inactive_lru()` returns the entry to L1 or L2 depending on whether it has ever been promoted. Background `lru_run()` demotes idle L1 entries to L2 and optionally releases entries above the high-water mark. Reaping uses the cache hash latch plus queue lane lock to ensure only sentinel-referenced, reachable entries are removed from the hash and recycled.

Cleanup is split from reachability. Killed entries are removed from the hash and pushed to cleanup; unref performs state wipe once, then final cleanup frees lower-FSAL resources, attributes, export mappings, keys, locks, and the pool object when refcount reaches zero.

Chunks follow a separate lane array. `chunk_lru_run()` demotes chunks and releases a target number based on chunk pressure and entry pressure. Chunk reaping must acquire the parent directory `content_lock` or skip the chunk to preserve lock order.

## State and Persistence Behavior
LRU state is process-local memory: `entries_used`, `entries_hiwat`, `entries_release_size`, `chunks_hiwat`, `chunks_lowat`, `chunks_used`, and `per_lane_work`. Entries and chunks are recycled when possible, not persisted. Dirmap entries are transient per-export cookie/name mappings with an LRU list, a high-water cap, and age-based cleanup.

## Dependencies and Integration Points
This file integrates with `mdcache_hash` for latch-protected hash removal, `mdcache_helpers` for entry and chunk cleaning, `fsal_close()` and lower-FSAL `release()` for object teardown, pool allocation for cache entries, fridgethr background workers, FD LRU helpers, export lookup via `get_gsh_export()`, and NFS initialization wait. LTTng tracepoints are emitted around ref/reap operations when enabled.

## Risks and Edge Cases
Major risks are refcount imbalance, freeing while state or export mappings still exist, lock inversion between hash partitions, LRU lanes, and directory content locks, cleanup queue double-processing, and export context mismatch during lower-FSAL release. Chunk reaping is risky because it may observe a parent entry being destroyed and must rely on lane locks plus successful content-lock acquisition. Dirmap returns names through a `fsal_cookie_t *` cast, so callers must free and interpret it carefully.

## Test Signals
Useful tests include concurrent lookup/ref/unref under high cache pressure, unexport with entries still referenced by protocol operations, repeated kill/unref cleanup, large directory chunk pressure, FD limit pressure, package shutdown while workers are running, dirmap eviction and expiry, and sanitizer runs for use-after-free or double-free in chunk/entry recycling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_lru.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_lru.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_lru.h

## Purpose
`mdcache_lru.h` exposes the MDCACHE LRU/cache-lifetime API used by helper, hash, export, and handle code. It documents the LRU design, declares global LRU state and the cache-entry pool, and defines reference flags and queue sizing constants.

## Important APIs, Types, and Functions
- `struct lru_state` stores entry/chunk watermarks, current counts, per-lane work, release size, and prior run time.
- `LRU_ACTIVE_REF`, `LRU_PROMOTE`, `LRU_FLAG_SENTINEL`, and `LRU_TEMP_REF` describe reference intent.
- `LRU_SENTINEL_REFCOUNT` defines the base reachable reference count, and `LRU_N_Q_LANES` sets the prime number of queue lanes.
- Public entry APIs include `mdcache_lru_pkginit()`, `mdcache_lru_pkgshutdown()`, `mdcache_lru_get()`, `mdcache_lru_insert_active()`, `mdcache_lru_ref()`, `mdcache_lru_unref()`, cleanup push helpers, and `mdcache_lru_release_entries()`.
- Public chunk and dirmap APIs include chunk ref/unref/get/bump and `mdc_lru_map_dirent()`, `mdc_lru_unmap_dirent()`, `dirmap_lru_init()`, and `dirmap_lru_stop()`.

## Control Flow
The header establishes the required calling contract: newly allocated entries from `mdcache_lru_get()` must later be inserted, references must be released through `mdcache_lru_unref()`, and callers must not touch an entry after unref because it may free or recycle the object. Chunk APIs similarly require callers to respect content-lock expectations described in the implementation.

## State and Persistence Behavior
The exposed state is volatile process memory. `lru_state` is global and records resource pressure thresholds and counters; `mdcache_entry_pool` owns cache-entry allocations. No persistent data is written by this interface.

## Dependencies and Integration Points
The header depends on `mdcache_int.h`, logging, and FSAL types. It is the shared contract between `mdcache_helpers.c`, `mdcache_lru.c`, hash cleanup, and other MDCACHE handle/export code that needs object lifetime control.

## Risks and Edge Cases
The largest risk is misuse of reference flags: omitting `LRU_ACTIVE_REF`, incorrectly releasing the sentinel, or accessing entries after unref can cause leaks or use-after-free. The header declares `mdcache_lru_kill()` and `mdcache_lru_kill_for_shutdown()` even though their definitions are outside this file subset or absent in this implementation view, so consumers must verify linkage.

## Test Signals
Compilation/link tests should catch missing API definitions. Runtime tests should assert balanced refs for lookup/readdir/open paths, correct high-water release behavior, and safe chunk lifecycle under directory cache churn.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_lru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_main.c

## Purpose
`mdcache_main.c` wires MDCACHE into the FSAL module system. It defines module identity and fsinfo defaults, global cache statistics and entry pool, export create/update/uninit paths, package init/unload, and optional DBus reporting.

## Important APIs, Types, and Functions
- Global `MDCACHE` defines the module and default FSAL capability information.
- `mdcache_fsal_init()` registers the FSAL, sets module ops, and initializes object-handle ops.
- `mdcache_pkginit()` creates the entry pool, initializes LRU, and initializes the cache inode hash package.
- `mdcache_fsal_create_export()` allocates an MDCACHE export wrapper, initializes export ops and upcall ops, creates the underlying FSAL export, stacks MDCACHE above it, starts dirmap LRU if supported, updates `op_ctx`, and marks upcalls ready.
- `mdcache_export_uninit()` unwinds export setup on startup error.
- `mdcache_fsal_update_export()` forwards export updates to the lower FSAL.
- `mdcache_fsal_unload()` destroys hash/LRU/pool state and unregisters the module.
- `mdcache_dbus_show()` and `mdcache_utilization()` report stats and LRU/FD utilization when DBus is enabled.

## Control Flow
Initialization registers the FSAL first, then package initialization creates runtime cache resources. Export creation happens after the lower FSAL is known. MDCACHE allocates a wrapper export, installs MDCACHE export/upcall operations, asks the lower FSAL to create its export with MDCACHE upcalls, takes references, stacks exports, initializes per-export dirmap support, and switches `op_ctx` to the MDCACHE export.

Unload reverses global state: hash package destruction, LRU shutdown, pool destruction, and FSAL unregister. Export update is intentionally thin because MDCACHE has no per-export config in this file.

## State and Persistence Behavior
This file owns global in-memory state: `mdcache_entry_pool`, `cache_st`, and the module descriptor. Export wrappers allocate transient names, entry lists, locks, dirmap state, and upcall readiness. No persistent data is stored; all state is recreated on server start.

## Dependencies and Integration Points
It integrates with FSAL registration, export stacking, lower-FSAL module ops, MDCACHE handle/export/upcall initialization, `mdcache_lru`, `mdcache_hash`, pool allocation, DBus, and global FD LRU counters. It also exposes delegation transition forwarding to the lower FSAL.

## Risks and Edge Cases
Potential issues include incomplete cleanup when export creation fails after lower-FSAL creation or dirmap init, reference mismatches between MDCACHE and lower FSAL modules, upcalls arriving before `up_ready_set()`, and shutdown ordering if LRU cleanup still references hash/export state. The dirmap failure path frees the wrapper but must also consider lower-FSAL export resources already created.

## Test Signals
Test startup/shutdown loops, export create failure injection at lower-FSAL create and dirmap init, export update pass-through, DBus counter reporting under cache activity, module unload after active/recent cache entries, and delegation transition forwarding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_read_conf.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_read_conf.c

## Purpose
`mdcache_read_conf.c` defines the MDCACHE configuration block, defaults, validation, and post-parse derived parameters. It populates the global `mdcache_param` used by cache sizing, directory chunking, FD caching, LRU workers, dirmap limits, delegation heuristics, and owner-override behavior.

## Important APIs, Types, and Functions
- Global `struct mdcache_parameter mdcache_param` stores parsed configuration.
- `mdcache_params[]` maps config item names to struct fields with bounds and defaults, including `NParts`, `Cache_Size`, directory chunk settings, entry/chunk watermarks, LRU/FD reaper settings, `Dirmap_HWMark`, delegation percent, and cached owner override.
- `mdcache_param_init()` returns the singleton config target.
- `mdcache_param_commit()` validates that `Chunks_LWMark` does not exceed `Chunks_HWMark`.
- `mdcache_param_blk` registers the `MDCACHE` block with `CacheInode` as an alternate name.
- `mdcache_set_param_from_conf()` loads config, handles legacy `Dir_Chunk = 0`, computes `avl_chunk_split` and `avl_detached_max`, and derives `g_max_files_delegatable`.

## Control Flow
During startup, `load_config_from_parse()` fills `mdcache_param` from the parse tree and invokes commit validation. After successful parse, legacy directory-chunk disablement is normalized into the newer enable flag, chunk split threshold is computed as 1.5 times chunk size rounded to an even value, detached dirent capacity is computed from chunk size and multiplier, and the global delegation cap is computed from the configured percentage of `Entries_HWMark`.

## State and Persistence Behavior
Configuration is process-global and in-memory. It is loaded at startup/config processing time and consumed by LRU initialization, directory caching, FD caching, and delegation logic. No runtime persistence is performed.

## Dependencies and Integration Points
This file depends on config parsing infrastructure, `mdcache_int.h`/`mdcache_ext.h` for parameter definitions, logging, and global delegation state. Its outputs are consumed by `mdcache_lru.c`, `mdcache_helpers.c`, and other MDCACHE access/delegation paths.

## Risks and Edge Cases
Risk centers on invalid or surprising parameter interactions: low chunk watermark above high watermark is rejected, but equal values are allowed; very large chunk/detached settings can increase memory pressure; `Entries_Release_Size = 0` disables entry release attempts; legacy `Dir_Chunk = 0` changes two fields; and delegation percentage directly scales with the entry high-water mark.

## Test Signals
Test parse defaults, legacy `Dir_Chunk = 0`, invalid chunk low/high ordering, bounds on each config item, computed `avl_chunk_split` and `avl_detached_max`, DBus block naming, and resulting `g_max_files_delegatable` for boundary percentages and high-water marks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_read_conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_up.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_up.c

## Purpose
`mdcache_up.c` implements MDCACHE's lower-FSAL upcall vector. It consumes cache-related invalidation, update, close, and try-release upcalls, and forwards lock/delegation/layout notifications to the upper layer after establishing the correct MDCACHE operation context.

## Important APIs, Types, and Functions
- `mdc_up_invalidate()` finds a cached entry by lower-FSAL handle key, clears requested trust flags, optionally closes cached file state, invalidates cached parent handles, and releases cached ACLs.
- `mdc_up_try_release()` removes an otherwise idle entry from the cache hash when only the sentinel reference remains.
- `mdc_up_update()` applies a safe subset of lower-FSAL attribute updates and invalidates directory content when directory attributes change.
- `mdc_up_invalidate_close()` schedules asynchronous invalidation with close semantics.
- `mdc_up_lock_grant()`, `mdc_up_lock_avail()`, `mdc_up_layoutrecall()`, and `mdc_up_delegrecall()` pass state notifications upward through `super_up_ops`.
- `mdcache_export_up_ops_init()` copies upper upcall ops, initializes readiness, then overrides cache-aware operations with MDCACHE handlers.

## Control Flow
Each cache-affecting upcall takes a reference to the Ganesha export and creates a simple `op_ctx` for the MDCACHE export before touching cache state. Invalidation hashes the lower handle, looks up an MDCACHE entry with an active promoted ref, treats cache miss as success, clears trust bits, performs requested close/parent/ACL cleanup, then unrefs. Attribute update validates that immutable identity fields are not changed, filters flags, looks up the entry, handles zero link count by invalidating content and closing, updates only trusted cached attributes, and clears attribute trust when no meaningful update was possible.

Try-release is latch-based: it keeps the hash partition locked, checks refcount, takes a temp ref if the entry is otherwise idle, removes the hash entry, releases the latch, then drops the temp ref to allow cleanup.

Pass-through state notifications do not consume cache content; they set context and call the corresponding upper vector function.

## State and Persistence Behavior
Upcalls mutate volatile cache state: trust flags, cached attributes, cached ACL/fs_locations/sec_label ownership, parent-handle cache, hash reachability, and open FD state. They do not persist data, but they reflect lower-FSAL change notifications so future NFS operations see fresh metadata or miss the cache.

## Dependencies and Integration Points
This file integrates with lower-FSAL upcall registration from `mdcache_main.c`, MDCACHE hash lookup, LRU references, FSAL close, NFS ACL and fs_locations memory management, state/delegation/layout notification paths, general async invalidation fridge, and export/op-context lifetime helpers.

## Risks and Edge Cases
Important risks include missing `release_op_context()` on all paths, updating attributes that are not currently trusted, ownership transfer of ACL/fs_locations/sec_label payloads, clearing the right trust flags for directory changes, races between try-release and new lookups, and handling upcalls during export teardown. In `mdc_up_update()`, incremental timestamp flags must only move cached times forward when requested.

## Test Signals
Test cache miss invalidation as success, invalidate-close closing open cached objects, parent and ACL invalidation, zero-link updates, each incremental attribute update flag, immutable attribute rejection, try-release success with sentinel-only refs and failure with active refs, async invalidate-close scheduling, and pass-through lock/layout/delegation callbacks with correct context.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_up.c -->
