# sources/distributed-fs/glusterfs/libglusterfs/src/inode.c

## Purpose
`inode.c` implements GlusterFS' in-memory inode table: GFID-indexed inode identity, parent/name dentry links, path reconstruction, translator-private inode context slots, lookup/reference accounting, LRU eviction, invalidation, and statedump support. It is a central library component used by protocol frontends, translators, FUSE integration, fd management, and graph teardown.

## Important APIs, Types, And Functions
The main data types are declared in `glusterfs/inode.h`: `inode_table_t`, `inode_t`, `dentry_t`, and `_inode_ctx`. An `inode_table_t` owns hash buckets for GFIDs and dentries, active/LRU/purge/invalidate lists, a root inode, a per-table fd mem-pool, and optional invalidator callback state. Each `inode_t` stores a GFID, inode type, fd and dentry lists, table-list membership flags, `ref`, atomic `nlookup`, atomic child count, namespace inode, and a variable-length `_ctx[]` array indexed by translator level/id.

Construction and destruction are handled by `inode_table_new()`, `inode_table_with_invalidator()`, `inode_table_destroy()`, `inode_table_destroy_all()`, `inode_new()`, and private helpers such as `inode_create()` and `__inode_table_init_root()`. Identity and namespace operations include `inode_link()`, `inode_unlink()`, `inode_rename()`, `inode_find()`, `inode_grep()`, `inode_grep_for_gfid()`, `inode_parent()`, `inode_resolve()`, `inode_path()`, `inode_find_directory_name()`, and `inode_set_namespace_inode()`.

Lifetime APIs are `inode_ref()`, `inode_unref()`, `inode_lookup()`, `inode_forget()`, `inode_forget_with_unref()`, `inode_ref_reduce_by_n()`, and `inode_invalidate()`. Translator context APIs include `inode_ctx_set0/1/2()`, `inode_ctx_get0/1/2()`, `inode_ctx_del2()`, `inode_ctx_reset0/1/2()`, `inode_ctx_merge()`, and `inode_needs_lookup()`. Observability APIs include `inode_dump()`, `inode_table_dump()`, `inode_dump_to_dict()`, and `inode_table_dump_to_dict()`.

## Control Flow
Inode identity is established by `inode_link()`: it computes a dentry hash, takes the table lock, calls `__inode_link()`, and returns a referenced linked inode. `__inode_link()` validates parent table/type/name, hashes a previously unhashed inode by `iatt->ia_gfid`, detects existing inodes with the same GFID, creates or replaces parent/name dentries, updates parent refs and child counters, sets namespace inheritance, rejects cycles, and inserts dentry hash entries. Unlink and rename reverse or combine these steps and then call `inode_table_prune()`.

Reference transitions are guarded by the table lock in `__inode_ref()` and `__inode_unref()`. Referencing a zero-ref inode removes it from LRU or invalidate lists and returns it to active or invalidate state. Unreferencing moves zero-ref inodes with positive `nlookup` to LRU and zero-lookup inodes to purge. The root inode is special-cased to remain active with a stable ref. `inode_forget_atomic()` decrements `nlookup`, with defensive correction for kernel forget underflow behavior. `inode_table_prune()` enforces the LRU limit, optionally calls one invalidator outside the table lock, splices purge entries, clears lookup counts, and destroys inodes.

Path reconstruction in `__inode_path()` walks arbitrary dentries upward, sizes the output, and builds either a root-relative path or a `<gfid:...>` pseudo-root path when the chain does not reach the root. Context access computes a stable translator slot using `inode_get_ctx_index()`, then stores two opaque 64-bit values per translator.

## State And Persistence
All state is in-memory and tied to a graph/table lifetime. Persistent identity enters through GFIDs from `struct iatt`; dentries are a cache of observed namespace relationships, not authoritative storage. `nlookup` tracks kernel/FUSE lookup references, while `ref` tracks internal Gluster references. LRU, purge, and invalidate lists are derived state. The table records `cleanup_started` to tolerate destructor-time parent unrefs. Statedump and dict exports expose current in-memory state but do not persist it.

## Dependencies And Integration Points
The module depends on Gluster list, locking, UUID, `iatt`, fd, mem-pool, statedump, logging/message IDs, and translator graph types. It invokes translator callbacks: `forget`, `ictxmerge`, `invalidate`, and optional dumpops. `fd_dump()` and `fd_ctx_dump()` integrate with fd state. `inode_table_destroy_all()` walks `glusterfs_ctx_t->graphs`. FUSE behavior strongly influences `nlookup`, invalidation, and forget handling.

## Risks
This file is concurrency-sensitive. Most table/list mutations require `inode_table_t.lock`; per-inode context and dump operations use `inode->lock`. Any future path that mixes these locks must preserve ordering to avoid deadlocks. Ref/list counters (`active_size`, `lru_size`, `invalidate_size`) must stay consistent with membership flags or pruning will corrupt lists. `hash_gfid()` assumes the inode hash size is a power of two and indexes from the first 32 bits of a UUID. `__inode_path()` detects likely cycles only after exceeding `PATH_MAX`, so corrupted dentry graphs can cause expensive walks. Destructor behavior force-retires active inodes and can expose use-after-free if external references survive graph teardown. `inode_forget()` only updates `nlookup` and prunes; callers expecting a paired unref must use `inode_forget_with_unref()`.

## Test Signals
High-value tests cover link/find/unlink/rename, hardlink-like multiple dentries, cycle rejection, root inode ref behavior, lookup/forget underflow, LRU limit pruning, invalidator success/failure transitions, context slot collisions across translator level/id layouts, namespace inode replacement, path generation for rooted and GFID-prefixed paths, and table destruction with active, LRU, and invalidate entries. Stress tests should run concurrent ref/unref/link/unlink/dump under thread sanitizers if available.
