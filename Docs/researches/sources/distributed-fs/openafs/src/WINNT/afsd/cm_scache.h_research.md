# sources/distributed-fs/openafs/src/WINNT/afsd/cm_scache.h

## Purpose
`cm_scache.h` defines the stat-cache object model for the Windows AFS cache manager. It describes FIDs, byte-range locks, cached file status, callback state, access cache links, buffer/redirector state, synchronization flags, file-type constants, and the public scache API.

## Important APIs and types
- `cm_fid_t` identifies AFS objects by cell, volume, vnode, unique, and cached hash.
- `cm_key_t`, `cm_range_t`, and `cm_file_lock_t` model per-client byte-range locks.
- `cm_prefetch_t` tracks the last prefetch scan range.
- `cm_scache_t` is the central cached-vnode object, containing LRU/hash links, locks, refcount, file status, volume/callback data, ACL cache, file-lock state, directory B+ tree state, open counts, sync wait queue, redirector buffer queue, and active RPC count.
- File-type constants map AFS file status to cache-manager categories, including mount points, symlinks, DFS links, and invalid entries.
- `CM_SCACHEFLAG_*`, `CM_SCACHESYNC_*`, and `CM_MERGEFLAG_*` define persistent scache state, operation synchronization requests, and status-merge context.
- Public APIs include initialization, lookup/create, synchronization, status merge, refcounting, recycle, hash removal, directory reset, root lookup, validation, dump, suspend, and shutdown.

## Control flow and state behavior
The header defines the flags that drive `cm_scache.c` control flow. `CM_SCACHEFLAG_*` bits record in-progress RPCs, callback state, read-only state, quota/space errors, local modifications, redirector use, and watcher state. `CM_SCACHESYNC_*` flags request synchronization for one operation and map to those state bits. `CM_MERGEFLAG_*` tells `cm_MergeStatus()` why status is being merged so it can interpret data-version changes correctly.

## Dependencies and integration points
It includes Jenkins hash support via `opr/jhash.h`, then later includes `cm_conn.h` and `cm_buf.h` because scache synchronization touches connections and buffers. It exposes global locks and lists used across the cache manager. Redirector, SMB, callback, volume, ACL, directory, and daemon code all depend on this header's struct layout and flag meanings.

## Risks and edge cases
- `CM_FID_GEN_HASH` hashes volume/vnode/unique but intentionally excludes cell, so comparisons must still use `cm_FidCmp()` and callback-revocation paths must understand possible cross-cell hash collisions.
- Many fields are protected by different locks (`cm_scacheLock`, `scp->rw`, `redirMx`, `dirlock`, atomics), making the comments part of the correctness contract.
- `cm_scache_t` is large and shared broadly; layout changes can affect persisted memory-map assumptions or debugger tooling.
- Flag overlap between RPC sync flags and local sync flags requires careful use of masks.

## Test signals
Compile-time and runtime tests should verify FID hash/comparison behavior, lock count accounting, sync flag to scache flag transitions, file type mapping, read-only flag propagation, redirector queue protection, B+ directory invalidation, and refcount/list invariant validation through `cm_ValidateSCache()`.
