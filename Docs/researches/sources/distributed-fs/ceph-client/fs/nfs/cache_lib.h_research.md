# sources/distributed-fs/ceph-client/fs/nfs/cache_lib.h

## Purpose
This header declares the shared NFS client cache helper interface and defines the deferred request wrapper used by `cache_lib.c`.

## Important APIs, types, and functions
`struct nfs_cache_defer_req` embeds `struct cache_req`, `struct cache_deferred_req`, a `completion`, and a `refcount_t`. The declarations expose helper launching, deferred request allocation/release/waiting, and cache registration/unregistration for both network namespaces and rpc_pipefs superblocks.

## Control flow
Users allocate a deferred request, submit or attach it to SUNRPC cache handling through the embedded `cache_req`, then wait on completion and release their reference. Registration callers pass a prepared `struct cache_detail` to the net or superblock helpers.

## State and persistence behavior
The header defines only transient in-kernel state. Lifetime is explicit through refcounting, and completion state represents one outstanding cache upcall wait.

## Dependencies and integration points
It depends on Linux completion, SUNRPC cache, and atomic/refcount headers. It is consumed by NFS client cache implementations that need rpc_pipefs-visible cache_detail entries and userspace upcalls.

## Risks and test signals
The main risk is misuse of the embedded objects: callers must not free the wrapper before the cache subsystem releases deferred references. Compile coverage should verify all users include the proper net/superblock forward declarations; runtime tests should exercise deferred request completion and timeout.
