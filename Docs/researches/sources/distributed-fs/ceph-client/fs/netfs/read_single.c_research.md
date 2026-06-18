<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/read_single.c -->
# sources/distributed-fs/ceph-client/fs/netfs/read_single.c

## Purpose
Supports synchronous reads of a single monolithic netfs object, such as an AFS directory blob. The object is fetched as one subrequest from cache or server, then optionally marked dirty for cache writeback if downloaded.

## Important APIs, Types, And Functions
Exports `netfs_single_mark_inode_dirty()` and `netfs_read_single()`. Internal helpers are `netfs_single_begin_cache_read()`, `netfs_single_cache_prepare_read()`, `netfs_single_read_cache()`, and `netfs_single_dispatch_read()`.

## Control Flow
`netfs_read_single()` allocates a `NETFS_READ_SINGLE` request, begins a cache read operation if possible, stores the caller iterator in the request buffer, dispatches exactly one subrequest, waits for read collection, drops the request, and returns bytes/error. Dispatch prepares the subrequest from cache resources; source is either cache read or server download. Cache reads call cache ops `read()`, while server reads call netfs `prepare_read()` and `issue_read()`. Completion in read collector marks downloaded cacheable single objects dirty.

## State And Persistence
The request covers offset zero and the full iterator count. `netfs_single_mark_inode_dirty()` may set inode dirty and pin the FS-Cache cookie using `I_PINNING_NETFS_WB`, unless `SINGLE_NO_UPLOAD` and no cache is enabled.

## Dependencies And Integration Points
Integrates with FS-Cache read resources, netfs `issue_read`, read collector, inode dirty/writeback handling, and the single-object writeback path.

## Risks
Only one subrequest is permitted; filesystems must support that semantic or retry logic must preserve it. Cache-only objects without caching enabled are not dirtied. Oversized buffers beyond EOF depend on lower layers/collector to zero unused space.

## Test Signals
Read single object from cache, cache miss download then dirty inode, no-cache path, `SINGLE_NO_UPLOAD`, iocb completion through collector, and failure from cache begin returning `-ENOMEM`/interrupt errors.
