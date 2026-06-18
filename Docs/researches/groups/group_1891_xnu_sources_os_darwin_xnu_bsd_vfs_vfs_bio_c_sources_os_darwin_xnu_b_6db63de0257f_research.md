# Group Research: XNU BSD VFS Buffer I/O And Name Cache

Scope checked against `Docs/research_subset_a.md`: `sources/os/darwin/xnu` is included in subset A. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_bio.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_bio.c

## Purpose

`vfs_bio.c` implements Darwin/XNU's BSD buffer I/O layer: `buf_t` state accessors, block read/write helpers, buffer-cache lookup and recycling, metadata buffer allocation, asynchronous I/O completion, delayed-write laundering, UBC-backed regular-file buffers, and temporary I/O buffers used by lower storage paths. It is the bridge between vnode-level filesystem operations, VM/UBC pages, and device `VNOP_STRATEGY` calls.

## Main Responsibilities

- Exposes the public kernel `buf_*` API for flags, sizes, credentials, device/vnode fields, UPL mapping, callbacks, verification metadata, and content-protection attributes.
- Maintains hashed cached buffers by `(vnode, logical block)` through `bufhashtbl`, with invalid buffers stored on `invalhash`.
- Maintains global free/reuse queues: `BQ_LOCKED`, `BQ_LRU`, `BQ_AGE`, `BQ_EMPTY`, `BQ_META`, and `BQ_LAUNDRY`.
- Provides synchronous, asynchronous, delayed, metadata, and read-ahead I/O paths through `buf_bread`, `buf_meta_bread`, `buf_breadn`, `buf_bwrite`, `buf_bdwrite`, and `buf_bawrite`.
- Integrates regular-file data buffers with UBC UPLs, while metadata buffers use kernel heap or kernel-map wired storage.
- Handles delayed-write pressure using `nbdwrite`, vnode write throttling, and a dedicated `bcleanbuf_thread`.
- Implements buffer invalidation and flushing by vnode through safe list iteration helpers.
- Provides shadow buffers for metadata I/O and callback/filter ownership patterns.
- Registers VM pressure cleanup via `vm_set_buffer_cleanup_callout(buffer_cache_gc)` and supports filesystem GC callouts.

## Key Data Structures And State

- `struct buf` headers are initialized in `bufinit()` from `buf_headers`; more can be allocated from `buf_hdr_zone` up to `max_nbuf_headers`, with temporary overcommit support.
- `bufhashtbl` stores valid cacheable buffers by vnode/block; `invalhash` stores invalid or empty buffers.
- `bufqueues[]` are tail queues used as buffer reuse lists. Timestamp thresholds (`lru_is_stale`, `age_is_stale`, `meta_is_stale`) drive `getnewbuf()` queue choice.
- `iobufqueue` stores reserved I/O-only headers for clone, cluster, shadow, and lower-level operations.
- `delaybufqueue` is declared, while delayed-write laundering actually uses `BQ_LAUNDRY`.
- `bufstats`, `nbdwrite`, `blaundrycnt`, `buf_busycount`, `needbuffer`, and `need_iobuffer` track pressure and waiters.
- `fs_callouts[]` stores up to 16 buffer-cache GC callbacks.

## Important Control Flow

- `bufinit()` initializes queues, hash tables, buffer headers, cluster support, the laundry thread, and VM pressure callback registration.
- `buf_getblk()` is the central cache acquisition path. It first probes the hash, waits on busy buffers when allowed, maps UBC pages for regular-file data, allocates metadata storage for metadata buffers, or obtains a recycled/new header via `getnewbuf()`.
- `getnewbuf()` prefers empty buffers, can grow header count, then chooses stale AGE/LRU/META buffers. Dirty reusable buffers are moved to `BQ_LAUNDRY` instead of being reused immediately.
- `bcleanbuf()` removes a buffer from its free queue, handles delayed-write laundering, detaches vnode/hash state, releases credentials and metadata storage, and returns a busy clean header ready for reuse.
- `bio_doread()` and `do_breadn_for_type()` implement `bread`/read-ahead on top of `buf_getblk()` and `VNOP_STRATEGY`.
- `buf_strategy()` maps logical file offsets to physical blocks with `VNOP_BLOCKMAP`, handles sparse/fragmented blocks, dispatches cluster buffers, sets content-protection offsets, and finally calls the device vnode strategy operation.
- `buf_bwrite()` clears delayed-write state, charges process/vnode output, issues `VNOP_STRATEGY`, and waits/releases for synchronous writes.
- `bdwrite_internal()` marks a buffer delayed and may force async writeback when delayed writes exceed 75% of buffer headers.
- `buf_brelse()` is the main release path: it commits or aborts UPLs, frees verification data, invalidates nocache/error buffers, moves buffers to an appropriate queue, handles shadow-master waits, clears busy state, and wakes waiters.
- `buf_biodone()` finalizes I/O, updates mount pending I/O counters, traces disk I/O, clears throttle/passive metadata, invokes callbacks or filters, releases async buffers, or wakes synchronous waiters.
- `buffer_cache_gc()` evicts stale metadata buffers in bounded batches, sending dirty ones to laundry and freeing clean metadata storage.

## Concurrency And Locking

- `buf_mtx` protects buffer hash membership, vnode clean/dirty lists, free queues, busy counts, and most buffer-cache state transitions.
- `iobuffer_mtxp` protects `iobufqueue`, I/O buffer usage counters, and virtual-device I/O buffer throttling.
- `buf_gc_callout` protects registration and dispatch of filesystem buffer-cache GC callbacks.
- Busy buffers use `BL_BUSY` plus `BL_WANTED` wait/wakeup discipline. Public wait paths commonly set wait bits under `buf_mtx`, sleep on the buffer, and retry.
- Vnode buffer iteration uses `VBI_ITER` and a temporary local list to avoid corrupting vnode clean/dirty lists while callbacks may drop locks.
- Shadow buffers require careful handling: parent buffers can stay off free lists while `b_shadow_ref` is nonzero, and `BL_WAITSHADOW`/`BL_WANTED_REF` coordinate waiters.
- The laundry thread avoids recursive stack/deadlock patterns by moving delayed write cleaning out of `getnewbuf()` callers.

## Edge Cases And Invariants

- Buffer hash list links use a `0xdeadbeef` sentinel through `BLISTNONE()` and diagnostic checks to catch double insertion/removal.
- `buf_getblk()` rechecks `incore_locked()` after `getnewbuf()` because allocating/recycling can drop `buf_mtx`.
- Metadata buffers smaller than `MAXMETA` are allocated from `KHEAP_VFS_BIO`; larger metadata buffers use `kmem_alloc`.
- Regular-file data buffers are usually UBC-backed; several development/debug checks panic if Apple filesystems call old `buf_getblk()` paths unexpectedly.
- Sparse block reads with physical block `-1` are zero-filled and completed without device I/O.
- `buf_strategy_fragmented()` splits logically contiguous but physically fragmented I/O into per-extent synchronous strategy calls.
- `buf_brelse()` treats metadata `B_FILTER` callbacks specially so HFS journaling filters are cleaned up even on invalidation.
- `alloc_io_buf()` reserves `NRESERVEDIOBUFS` for privileged callers and throttles disk-image/virtual-device mounts separately.
- Verification buffers are sized by block count and hash kind; cluster verification data is retrieved from UPL verification storage.
- Content-protection fields are compiled under `CONFIG_PROTECT`; non-protection builds provide no-op/NULL implementations.

## Filesystem Relevance

This file is central for understanding Darwin's historical BSD buffer cache as it coexists with UBC. Filesystem metadata still uses `buf_t` as a cache and I/O object, while regular-file data paths are VM-page backed. The file also shows how vnode-level operations are turned into block-device strategy calls, how dirty metadata is throttled and laundered, and how the kernel avoids deadlocks under memory and virtual-device pressure.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_cache.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_cache.c

## Purpose

`vfs_cache.c` implements XNU's vnode name cache, vnode identity helpers, path reconstruction, cached authorization state, firmlink support, negative lookup caching, SMR-assisted lockless cache lookup, and interned pathname string storage. It is the fast path that lets VFS path lookup avoid filesystem calls when names, parent links, mount crossings, and access decisions can be resolved from cached vnode state.

## Main Responsibilities

- Maintains namecache entries keyed by directory vnode plus CRC32 name hash.
- Supports positive entries mapping `(directory, name)` to a child vnode and negative entries recording known misses.
- Provides lookup APIs: `cache_lookup_path()`, `cache_lookup_ext()`, and `cache_lookup()`.
- Provides insertion APIs: `cache_enter()`, `cache_enter_create()`, and `cache_enter_with_gen()`.
- Provides purge APIs for individual vnodes, negative children, and entire mounts.
- Maintains vnode identity fields: `v_name`, `v_parent`, `v_ncchildren`, `v_nclinks`, `v_cred`, and cached authorized actions.
- Reconstructs paths from vnode parent/name chains through `build_path_with_parent()` and `build_path()`.
- Determines parent/descendant relationships with cached parent pointers first, then filesystem `VNOP_LOOKUP("..")` when needed.
- Implements an interned string table for vnode and namecache names via `vfs_addname()` and `vfs_removename()`.
- Supports Darwin-specific firmlinks and named resource fork path handling when configured.

## Key Data Structures And State

- `nchashtbl` is an SMR queue hash table of `struct namecache` entries.
- `nchead` is the global LRU-style list of namecache entries, and `neghead` tracks negative entries separately.
- `numcache`, `desiredNodes`, `desiredNegNodes`, and `ncs_negtotal` bound total and negative cache growth.
- `namecache_zone` allocates `struct namecache`; when SMR is enabled, entries are freed through `zfree_smr`.
- `nc_counter` is a sequence counter plus valid bit; odd values mean a valid entry, and lockless readers verify the counter before and after reading fields.
- `string_ref_table` stores interned strings as `string_t` entries with refcounts, protected by `strtable_rw_lock` plus 1024 bucket mutexes.
- `namecache_rw_lock` protects serialized namecache mutation and locked lookup.
- `rootvnode_rw_lock` is declared for root vnode coordination elsewhere.

## Important Control Flow

- `nchinit()` sizes the positive and negative cache targets from `desiredvnodes`, enables SMR if requested, initializes the CRC table, creates the name hash table, initializes the string table, and initializes string bucket locks.
- `hash_string()` and the path parser in `cache_lookup_path()` use the same CRC32-style hash, replacing hash value `0` with `1` because zero means "not computed."
- `cache_lookup_path()` is the high-performance multi-component lookup fast path. It parses components, handles repeated/trailing slashes, dot and dotdot, named resource fork suffixes, authorization cache checks, mount traversal, firmlinks, local/devfs/removable restrictions, and returns `ni_dvp`/`ni_vp` with iocounts where needed.
- `cache_lookup_path()` first attempts SMR lockless traversal when `nc_smr_enabled` is active. If it sees instability, chroot dotdot cases needing parent-chain validation, invalid counters, or vnode identity mismatch, it restores saved nameidata state and retries under the shared namecache lock.
- `cache_lookup_locked()` and `cache_lookup_smr()` are internal child-entry probes used by path lookup.
- `cache_lookup_ext()` is the classic one-component cache API. It uses the SMR fast path when possible, falls back to `cache_lookup_fallback()` when mutation, negative-create handling, or invalid state requires locking.
- `cache_enter_locked()` allocates or reuses a cache entry, fills vnode/directory/name/hash state, inserts into hash, links it into child and vnode reverse lists, handles negative-entry limits, and marks it valid by incrementing `nc_counter`.
- `cache_delete()` invalidates an entry by incrementing `nc_counter`, removes it from hash/list structures, drops its interned name, drops held vnode references, and optionally frees the entry.
- `vnode_update_identity()` updates vnode parent and/or name, purges affected cache entries, handles firmlink purge, invalidates cached credentials/actions, and carefully avoids recursive reclaim chains when releasing old parents.
- `build_path_with_parent()` walks cached parent/name state backward into a caller buffer, optionally entering filesystems to repair missing parent/name information, respecting chroot roots, mount crossings, volume-relative mode, hardlinks, firmlinks, access checks, and moved-parent detection.
- `vnode_issubdir()` uses cached parent chains first, then falls back to `VNOP_LOOKUP("..")` when hardlinks or missing parents prevent a purely cached answer.
- `resize_namecache()` grows the namecache hash table and rehashes live entries under exclusive namecache lock.
- `resize_string_ref_table()` grows the interned string table when bucket occupancy exceeds 75%.

## Authorization Cache Behavior

- `vnode_cache_authorized_action()` caches actions for the current credential on a vnode, with optional TTL behavior for mounts marked `MNTK_AUTH_OPAQUE` or `MNTK_AUTH_CACHE_TTL`.
- `vnode_cache_is_authorized()` validates cached action bits against the current credential and mount TTL policy.
- `vnode_uncache_authorized_action()` and `vnode_uncache_credentials()` clear cached rights, dropping credentials after releasing the namecache lock.
- `cache_lookup_path()` uses cached `KAUTH_VNODE_SEARCH` or `KAUTH_VNODE_SEARCHBYANYONE` to skip filesystem authorization checks where safe, but still performs MACF lookup checks when configured.

## Concurrency And Locking

- The name cache uses `namecache_rw_lock`; mutation requires exclusive lock, while many lookups and path reconstruction use shared lock.
- SMR lookup avoids the rw lock for hot paths, but relies on `nc_counter`, stable vnode IDs, `vnode_hold_smr()`, and fallback retries.
- `v_parent`, `v_name`, `v_ncchildren`, `v_nclinks`, vnode cached credentials, and authorization bits are treated as namecache-protected identity state.
- String interning uses a table-level rw lock to stabilize resizing and per-bucket mutexes to update chains/refcounts.
- Credential references are dropped after releasing namecache locks to avoid expensive or unsafe work while holding global locks.
- Parent vnode reference release in `vnode_update_identity()` defers reclaim recursion through `uu_defer_reclaims`.

## Edge Cases And Invariants

- Negative cache entries have `nc_vp == NULL`; they are useful for avoiding repeated filesystem misses but are purged for create/rename cases.
- The negative cache is capped at `desiredNegNodes`; the oldest negative is removed when the cap is exceeded.
- A vnode is allowed only one positive namecache link in `cache_enter_locked()`; if another entry already exists, the new insert is skipped.
- For case-insensitive filesystems, `cache_enter_locked()` may replace the lookup spelling with `vp->v_name` so the cached spelling matches filesystem identity.
- Dotdot lookup respects chroot/root constraints, `NAMEI_RESOLVE_BENEATH`, and `NAMEI_NODOTDOT`.
- Directory hardlinks and vnodes marked `VISHARDLINK` force filesystem participation for accurate parent/name resolution.
- Firmlink source/target handling rewrites traversal for configured synthetic paths and manages forced vnode references.
- Mount traversal uses real root vnode generation data and refuses stale mount roots.
- `build_path_with_parent()` returns path length including the trailing NUL byte, a contract explicitly relied on elsewhere in the kernel.
- `vfs_removename()` frees interned strings with SMR when enabled; otherwise it frees string memory immediately after refcount reaches zero.

## Filesystem Relevance

This file is the main reference for Darwin path lookup acceleration. It shows how VFS avoids filesystem calls by caching vnode names, parent links, negative misses, and authorization decisions, while still preserving correctness around chroot, mount points, hardlinks, firmlinks, MAC checks, vnode recycling, and concurrent cache mutation. It is also the companion to vnode lifecycle code because vnode identity and cached path reconstruction are maintained here rather than in individual filesystems.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_cache.c -->