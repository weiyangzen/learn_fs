<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/security.c -->
# sources/distributed-fs/ceph-client/fs/afs/security.c

## Purpose
Manages AFS authentication key lookup, anonymous fallback keys, per-vnode access permit caching, and VFS permission checks.

## Important APIs, Types, And Functions
Exports `afs_request_key()`, `afs_request_key_rcu()`, `afs_put_permits()`, `afs_clear_permits()`, `afs_cache_permit()`, `afs_check_permit()`, `afs_permission()`, and `afs_clean_up_permit_cache()`. It uses a global hash table of immutable `afs_permits` lists, protected by spinlock and RCU, and an anonymous key allocation mutex.

## Control Flow
Permission checks request a key for the cell. RCU pathwalk uses nonblocking key lookup and cached validity only; blocking checks validate the vnode, then fetch/cache CallerAccess if missing. `afs_cache_permit()` builds or reuses sorted immutable permit arrays, handles callback-break races, and swaps them into the vnode under lock.

## State And Persistence
State includes cell anonymous keys, key refs in permit lists, vnode `permit_cache`, and the global permit-list deduplication hash. Caches are invalidated on callback break and freed through RCU. No durable persistence exists beyond keyring contents.

## Dependencies And Integration Points
Uses Linux keyrings/RxRPC key type, VFS permission hooks, AFS callback validation, `afs_fetch_status()`, vnode status ACL fields, and AFS ACL bit definitions.

## Risks And Edge Cases
RCU pathwalk must return `-ECHILD` when blocking work or allocation is required. Callback breaks during permit update must prevent stale ACL use. Key pointer sorting/hashing assumes stable key object identity and careful ref ownership.

## Test Signals
Authenticated and anonymous access, RCU pathwalk permission checks, ACL changes with callback invalidation, concurrent permission checks, key expiration/revocation, and permit-cache cleanup warnings at module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/security.c -->
