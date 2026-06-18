<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/objects.c -->
# sources/distributed-fs/ceph-client/fs/netfs/objects.c

## Purpose
Owns allocation, reference counting, cleanup, and tracing for `netfs_io_request` and `netfs_io_subrequest` objects.

## Important APIs, Types, And Functions
Defines `netfs_alloc_request()`, `netfs_get_request()`, `netfs_clear_subrequests()`, `netfs_put_request()`, `netfs_put_failed_request()`, `netfs_alloc_subrequest()`, `netfs_get_subrequest()`, and `netfs_put_subrequest()`. Internal cleanup is split through `netfs_free_request()`, `netfs_deinit_request()`, `netfs_free_request_rcu()`, and `netfs_free_subrequest()`.

## Control Flow
Request allocation chooses a filesystem-specific mempool or the global pool, sleeps/retries until allocation succeeds, initializes origin-dependent collector work, two IO streams, waitqueue, locks, refcount of two, netfs ops, and optional `init_request()`. It increments the inode IO count and adds proc visibility. Last put queues cleanup work; cleanup cancels collector work, unlinks proc state, clears subrequests, frees netfs private state, ends cache resources, unpins direct pages, clears rolling buffer, decrements inode IO count, and frees via RCU. Subrequests similarly use per-netfs or global mempool and hold a request reference.

## State And Persistence
All state is transient. Request fields track start/len, origin, mapping/inode, i_size, streams, flags, buffer, direct bvecs, cache resources, and debug ids. Refcounting is the persistence boundary for async operations.

## Dependencies And Integration Points
Used by all read/write issue paths. Depends on mempools from `main.c`, netfs inode ops, proc helpers, rolling buffer, FS-Cache resources, RCU, and tracepoints.

## Risks
Refcount imbalance can leak or use-after-free requests/subrequests. `netfs_put_failed_request()` assumes a just-allocated refcount of two. Cleanup cancels work that has no own ref, so changing collector ref rules is risky. Allocation loops sleep indefinitely under severe memory pressure.

## Test Signals
Fault-inject `init_request()` failure, subrequest allocation pressure, async completion after caller return, direct IO bvec unpin cleanup, proc add/delete, and final wake on inode `io_count` reaching zero.
