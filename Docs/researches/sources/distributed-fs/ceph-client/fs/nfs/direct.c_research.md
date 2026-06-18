# sources/distributed-fs/ceph-client/fs/nfs/direct.c

## Purpose
`direct.c` implements uncached NFS I/O for `O_DIRECT` and swapfile paths. It bypasses the page cache for application buffers, builds NFS page requests directly from user or swap iterators, schedules pageio reads/writes, handles asynchronous completion, and drives unstable-write COMMIT or retry behavior for both metadata-server and pNFS data-server commits.

## Important APIs, types, and functions
The main entry points are `nfs_file_direct_read`, `nfs_file_direct_write`, `nfs_swap_rw`, `nfs_init_cinfo_from_dreq`, `nfs_dreq_bytes_left`, `nfs_init_directcache`, and `nfs_destroy_directcache`. Internally, `struct nfs_direct_req` carries the inode, open context, lock context, byte accounting, error state, async kiocb, commit-info structures, refcounts, completion, spinlock, and work item.

Read completion is handled by `nfs_direct_read_completion_ops`; write completion and retry by `nfs_direct_write_completion_ops`; unstable-write commit by `nfs_direct_commit_completion_ops`. Scheduling centers on `nfs_direct_read_schedule_iovec` and `nfs_direct_write_schedule_iovec`.

## Control flow
A direct read allocates an `nfs_direct_req`, captures the NFS open and lock contexts, marks asynchronous requests with the kiocb, optionally starts direct-I/O exclusion, then pins iterator pages in chunks sized by server `rsize`. Each pinned page becomes an `nfs_page` request and is fed into `nfs_pageio_add_request`; completion updates byte counts, marks user-backed read pages dirty when appropriate, releases requests, and completes the direct request when the outstanding I/O count reaches zero.

A direct write performs generic write checks unless it is swap I/O, allocates a direct request, initializes pNFS commit info, starts direct-I/O exclusion, and pins iterator pages in chunks sized by server `wsize`. Requests are submitted through the NFS pageio write path with conditional stability for normal direct I/O and stable writes for swap. After submission, any overlapping page-cache range is invalidated for normal direct writes, then the caller waits or receives async completion.

Completion tracks `count`, `max_count`, and `error` under `dreq->lock`. EOF or header errors truncate the visible result to the first failed byte. Unstable writes are marked for COMMIT; verifier mismatch or soft `-EAGAIN` failures move requests to commit/retry lists and queue `nfsiod_workqueue` work to reschedule writes. Fatal commit errors truncate the result and complete with the first error.

## State and persistence behavior
This file owns runtime state only. Direct data persistence is server-side: normal direct writes use conditional stable writes and may need COMMIT, while swap writes request stable storage. `nfs_direct_file_adjust_size_locked` updates local `i_size` optimistically when a direct write extends the file, clearing invalid-size state after server write success.

The direct request lifetime uses both a kref and an I/O counter. The kref protects allocation lifetime across caller, async completion, and workqueue paths; `io_count` gates final completion after all pageio headers and commit work have drained.

## Dependencies and integration points
`direct.c` depends on NFS pageio, NFS request, commit, lock-context, open-context, pNFS commit-info, fscache invalidation, inode direct-I/O exclusion helpers, generic write sync, task I/O accounting, and `nfsiod_workqueue`. It is called from `file.c` for `IOCB_DIRECT` and from NFS swap address-space operations.

## Risks
Accounting bugs can return too many bytes, fail to rewind the iterator, or hide the first error. Retry and commit paths are sensitive to request reference counts, locked request state, verifier comparison, pNFS data-server commit buckets, and the transition between `NFS_ODIRECT_DO_COMMIT`, `NFS_ODIRECT_RESCHED_WRITES`, and done states. Page pin/release balance is also critical under short reads, allocation failures, and partial scheduling.

## Test signals
Exercise synchronous and asynchronous direct reads/writes, short reads at EOF, server write errors after partial success, unstable writes requiring COMMIT, COMMIT verifier mismatch, pNFS DS commit fallback, iterator rewind after partial direct I/O, page-cache invalidation for overlapping buffered readers, swap read/write paths, signal interruption of synchronous waits, and allocation failure in page pinning or request creation.
