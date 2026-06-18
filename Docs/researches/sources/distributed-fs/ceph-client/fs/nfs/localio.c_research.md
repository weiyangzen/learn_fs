# sources/distributed-fs/ceph-client/fs/nfs/localio.c

## Purpose
`localio.c` implements NFS client support for bypassing the network path when the NFS server is local to the same kernel. It probes server locality using the `nfslocalio` auxiliary RPC program, opens local filehandles through nfsd helpers, performs reads/writes using VFS `read_iter` and `write_iter`, and maps results back into normal NFS page-IO and commit completion callbacks.

## Important APIs, Types, And Functions
Important private types are `struct nfs_local_kiocb`, which wraps a kernel `kiocb`, bvec array, page-IO header, local nfsd file, work item, and up to three `iov_iter` segments; and `struct nfs_local_fsync_ctx`, which carries local commit/fsync work. Exported functions include `nfs_server_is_local()`, `nfs_local_probe_async_work()`, `nfs_local_probe_async()`, `nfs_local_open_fh()`, `nfs_local_doio()`, and `nfs_local_commit()`.

Locality is probed by `nfs_init_localioclient()`, `nfs_server_uuid_is_local()`, and `nfs_local_probe()`. I/O setup is handled by `nfs_local_iocb_alloc()`, `nfs_is_local_dio_possible()`, `nfs_local_iters_setup_dio()`, and `nfs_local_iters_init()`. Completion flows through `nfs_local_pgio_done()`, `nfs_local_pgio_release()`, and read/write-specific completion helpers. Writes also update verifiers through `nfs_set_local_verifier()` and collect post-write attrs with `nfs_local_vfs_getattr()`. Commits run `vfs_fsync_range()` in `nfs_local_fsync_work()`.

## Control Flow And Integration Points
The probe path is asynchronous on `nfsiod_workqueue` and requires `localio_enabled`, `AUTH_SYS`, and a successful `UUID_IS_LOCAL` RPC response with initialized local UUID fields. Open uses `nfs_open_local_fh()` and disables/reprobes localio on selected stale/local-open failures. Read/write I/O obtains the underlying file from the nfsd file, builds bvec iterators from the NFS page array, optionally splits direct I/O into misaligned start, aligned middle, and misaligned end segments, then queues actual VFS I/O on `nfslocaliod_workqueue`. On completion it calls the same RPC call-done/release callbacks normal network I/O would use.

## State And Persistence Behavior
Global `localio_enabled` gates all use. Per-client locality is represented by `clp->cl_uuid` state accessed with RCU helpers and `nfs_uuid_begin/end`. Opened local files are reference-counted nfsd files and released through `nfs_local_file_put()`. `nfs_local_kiocb` state lives until all iter segments complete. Boot verifiers are stored in `cl_nfssvc_boot` under `cl_boot_lock` and reset on write/commit errors to make unstable-write verification conservative.

## Dependencies
The implementation depends on nfsd local-file APIs from `linux/nfslocalio.h`, SunRPC program binding, VFS file operations, workqueues, bvec/iov_iter helpers, credential scoping, tracepoints, pNFS/NFS page-IO types, and NFSv3/NFSv4 stable-write verifier semantics.

## Risks And Edge Cases
Direct I/O alignment is the riskiest area: incorrect split boundaries or callback ordering can produce short I/O, unexpected `-EINVAL`, or page-IO completion before all segments finish. The file explicitly clears `hdr->res.replen` after local reads to avoid NFSv3 corruption if future I/O returns to RPC. Write paths must restore task flags after `PF_LOCAL_THROTTLE | PF_MEMALLOC_NOIO`. Localio must disable itself after local server restart or stale handles and avoid using non-`READ`/`WRITE` modes.

## Test Signals
Tests should cover enabling/disabling the module parameter, AUTH_SYS versus non-AUTH_SYS mounts, local server restart, read/write fallback after localio disablement, mixed direct and buffered localio, short reads/writes, stable and unstable writes, commit/fsync ranges, and xfstests comparing localio results against normal RPC.
