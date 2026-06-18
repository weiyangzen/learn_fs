# sources/distributed-fs/ceph-client/fs/nfs/nfs42proc.c

## Purpose

`nfs42proc.c` implements the client-side NFSv4.2 procedure layer for operations that are exposed upward through VFS file operations, pNFS layout code, and xattr handlers. It prepares RPC argument/result structures, selects stateids, performs synchronous or asynchronous SUNRPC calls, handles NFSv4 recovery exceptions, updates inode/page-cache state after successful server-side mutations, and downgrades server capability bits when peers return unsupported-operation errors.

## Important APIs, Types, and Functions

The public API exported through `nfs42.h` includes `nfs42_proc_allocate`, `nfs42_proc_deallocate`, `nfs42_proc_zero_range`, `nfs42_proc_copy`, `nfs42_proc_copy_notify`, `nfs42_proc_llseek`, `nfs42_proc_layoutstats_generic`, `nfs42_proc_layouterror`, `nfs42_proc_clone`, `nfs42_proc_getxattr`, `nfs42_proc_setxattr`, `nfs42_proc_listxattrs`, and `nfs42_proc_removexattr`. These functions are invoked from `nfs4file.c`, `nfs4proc.c`, pNFS layout modules, and server-side-copy support.

The fallocate family is built around `_nfs42_proc_fallocate`, which fills `nfs42_falloc_args`, chooses a write stateid with `nfs4_set_rw_stateid`, asks for post-op attributes via `nfs4_bitmask_set`, performs `nfs4_call_sync`, updates suid/cache invalidation, and traces allocate/deallocate results. The copy path uses `_nfs42_proc_copy`, `handle_async_copy`, `process_copy_commit`, `nfs42_copy_dest_done`, `nfs42_proc_offload_status`, and `nfs42_do_offload_cancel_async` to coordinate source/destination stateids, async CB_OFFLOAD completion, OFFLOAD_STATUS polling, commit verifier checks, and cancellation.

## Control Flow

Most exported functions check a capability bit, acquire a lock/open context when a stateid is needed, flush or synchronize local dirty data, call a private `_nfs42_proc_*` RPC helper, feed errors to `nfs4_handle_exception`, and loop while retry is requested. The private helpers are narrow RPC marshalling/adaptation layers; the exported wrappers own policy, retries, capability fallback, and VFS-visible errno translation.

Copy is the most complex flow. `nfs42_proc_copy` obtains source and destination lock contexts, locks the destination inode, calls `_nfs42_proc_copy`, and retries or falls back based on `-EAGAIN`, `NFS4ERR_OFFLOAD_NO_REQS`, `NFS4ERR_OFFLOAD_DENIED`, `-ESTALE`, and same-server/inter-server status. `_nfs42_proc_copy` writes back the source range, obtains destination write state, blocks direct I/O, syncs the destination inode, sends COPY, handles synchronous verifier checks or async completion, then invalidates destination cache and source atime.

## State and Persistence Behavior

This file mutates in-memory client state, not durable local metadata. It updates server capability bits, sets and clears NFS state flags for server-side copy, maintains async copy objects on `nfs_client` callback lists, invalidates page cache and inode attribute cache after remote mutation, and caches successful xattr GET replies. Persistent changes happen on the NFS server through RPCs.

## Dependencies and Integration Points

The implementation depends on SUNRPC, NFSv4 sequencing and recovery, VFS inode/page-cache helpers, pNFS layout APIs, and NFS tracepoints. Procedure numbers and XDR handlers are provided by `nfs4_procedures[]` and `nfs42xdr.c`. Primary callers include `nfs4file.c`, `nfs4proc.c`, `pnfs.c`, and pNFS layout drivers such as flexfiles.

## Risks and Edge Cases

Risk clusters include stale stateid recovery loops, verifier mismatch after COPY/COMMIT, async copy completion races with CB_OFFLOAD, cancellation behavior for inter-server copy, page-cache coherency after sparse-file operations, and capability-bit clearing that can disable features after unsupported replies. Xattr paths must keep page allocation/freeing balanced and respect negotiated xattr sizes.

## Test Signals

Useful tests are fallocate allocate/punch-hole/zero-range over NFSv4.2, sparse file `SEEK_HOLE`/`SEEK_DATA`, same-server and cross-server `copy_file_range`, async copy interruption and cancellation, clone/remap alignment handling, pNFS layoutstats/layouterror with stale layout stateids, and xattr get/set/list/remove including ERANGE/E2BIG and cache hit/miss behavior.
