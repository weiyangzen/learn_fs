<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/main.c -->
# sources/distributed-fs/ceph-client/fs/netfs/main.c

## Purpose
Module/init glue for the netfs support library. It creates request/subrequest slab caches and mempools, exposes procfs diagnostics, publishes tracepoints and debug module parameter, initializes embedded FS-Cache, and tears everything down.

## Important APIs, Types, And Functions
Defines module metadata and `netfs_debug` module parameter. Owns `netfs_request_pool`, `netfs_subrequest_pool`, `netfs_io_requests`, and `netfs_proc_lock`. Main functions are `netfs_init()` and `netfs_exit()`, plus proc seq operations for `/proc/fs/netfs/requests`.

## Control Flow
`netfs_init()` creates request slab, initializes request mempool, creates subrequest slab and mempool, creates `/proc/fs/netfs` and request/stat files when configured, then calls `fscache_init()`. Error paths unwind in reverse order. `netfs_exit()` calls `fscache_exit()`, removes proc subtree, exits mempools, and destroys slab caches.

## State And Persistence
Runtime state includes slabs/mempools and proc list of active IO requests. No persistent data is stored. The request proc output snapshots refcount, flags, error, origin, start/submitted/len.

## Dependencies And Integration Points
Depends on Linux module, mempool, procfs, seq_file, trace/events/netfs, and FS-Cache init. `objects.c` allocates from the pools and links requests into proc state.

## Risks
Initialization order is important: object allocation depends on pools, proc sequence files depend on active request list locking, and FS-Cache teardown must occur before destroying resources it can reference. Proc output reads active request structures under RCU.

## Test Signals
Module boot/init path, proc file creation, stats creation with `CONFIG_FSCACHE_STATS`, allocation pressure against mempools, and clean unload with no active requests.
