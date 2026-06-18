# sources/distributed-fs/ceph-client/fs/xfs/xfs_mru_cache.h

Purpose: Declares the opaque MRU cache interface and the element structure that clients must allocate and pass to the cache.

Important APIs, types, and functions: `struct xfs_mru_cache_elem` contains the intrusive list node and unsigned long key. `xfs_mru_cache_free_func_t` defines the callback used for deletion and error cleanup. Public functions cover global workqueue init/uninit, cache create/destroy, insert, remove, delete, lookup, and lookup completion.

Control flow: Clients create a cache with lifetime and group count, allocate elements embedding or containing `struct xfs_mru_cache_elem`, insert by key, use lookup plus `xfs_mru_cache_done` for locked access, and destroy the cache to flush all elements.

State and persistence behavior: The header exposes no persistent state. The element key is stored in each element so the implementation can remove radix-tree entries while walking expiration lists.

Dependencies and integration points: Depends on Linux list infrastructure through the element. The cache is intentionally generic and opaque so users do not depend on radix-tree or timing internals.

Risks: The locked-return lookup API must be documented at every call site; failing to call `xfs_mru_cache_done` deadlocks the cache. Passing stack or shared elements can corrupt lists because the cache owns the list node until removal/free.

Test signals: Compile users with sparse lock annotations; verify all successful lookup paths call `xfs_mru_cache_done`; validate callback ownership conventions in each cache user.
