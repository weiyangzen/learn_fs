# sources/distributed-fs/ceph-client/fs/nfs/cache_lib.c

## Purpose
This file contains shared helpers for NFS client cache upcalls and cache registration in rpc_pipefs. It launches the configured userspace cache helper, supports deferred cache requests with completion/refcount handling, and registers `struct cache_detail` objects for a superblock or network namespace.

## Important APIs, types, and functions
Exports include `nfs_cache_upcall()`, `nfs_cache_defer_req_alloc()`, `nfs_cache_defer_req_put()`, `nfs_cache_wait_for_upcall()`, `nfs_cache_register_net()`, `nfs_cache_unregister_net()`, `nfs_cache_register_sb()`, and `nfs_cache_unregister_sb()`. Module parameters `cache_getent` and `cache_getent_timeout` control the userspace helper path and wait timeout.

Deferred request plumbing is implemented by `nfs_dns_cache_defer()` and `nfs_dns_cache_revisit()`, which connect SUNRPC cache deferral callbacks to `struct completion`.

## Control flow
`nfs_cache_upcall()` constructs argv as helper path, cache name, and entry name, then calls `call_usermodehelper()` with `UMH_WAIT_EXEC`. If the helper is missing or denied, it clears the helper path to disable further upcalls until the admin resets the module parameter.

For deferred cache misses, callers allocate `struct nfs_cache_defer_req`, pass its embedded `cache_req`, and wait in `nfs_cache_wait_for_upcall()`. The cache subsystem calls the defer hook, which increments the refcount and returns the embedded deferred request. Revisit completes the waiter and drops that extra reference.

## State and persistence behavior
The helper path and timeout are module-wide tunables. Deferred request state is heap allocated and released by refcount. Cache registration state lives in SUNRPC cache/rpc_pipefs infrastructure; this file initializes/destroys `cache_detail` objects around registration.

## Dependencies and integration points
Dependencies include Linux kmod/usermodehelper APIs, completions, refcounts, SUNRPC cache APIs, rpc_pipefs superblock lookup, and network namespace handling. NFS DNS or ID-mapping style client caches use this library rather than duplicating upcall and pipefs registration code.

## Risks and test signals
Risks include disabled upcalls after transient `ENOENT`/`EACCES`, timeout tuning that is too short for slow helpers, refcount leaks in deferred paths, and missing pipefs superblocks causing registration to be skipped. Tests should cover helper success/failure, timeout, revisit completion, unregister after partial register failure, and per-net pipefs availability.
