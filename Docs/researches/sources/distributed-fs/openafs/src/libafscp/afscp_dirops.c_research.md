## sources/distributed-fs/openafs/src/libafscp/afscp_dirops.c

Purpose: Provides write-side directory and file-system operation wrappers for `libafscp`, mapping create, mkdir, symlink, lock, remove-file, and remove-dir operations onto RXAFS file server RPCs.

Important APIs and functions: Public functions are `afscp_CreateFile`, `afscp_MakeDir`, `afscp_Symlink`, `afscp_Lock`, `afscp_RemoveFile`, and `afscp_RemoveDir`. They accept directory or object FIDs, names or targets, and AFS store status structures, then return status through `afscp_errno` and optional new FID output parameters.

Control flow: Each operation resolves the containing volume with `afscp_VolumeById`, iterates volume server indexes, resolves each `afscp_server`, iterates that server's RX connections, and invokes the matching `RXAFS_*` RPC. Successful create and mkdir calls update parent stat cache via `_StatStuff`, add callbacks for new objects with `afscp_AddCallBack`, and optionally allocate a new `afscp_venusfid`. Remove operations invalidate or refresh parent status depending on the RPC result. `afscp_Lock` chooses `RXAFS_ReleaseLock` for `LockRelease` and `RXAFS_SetLock` for read, write, or extend locks.

State and persistence: No local durable state. The file-server RPCs mutate AFS namespace state. Local state changes are cache updates for statuses and callbacks, plus global `afscp_errno`.

Dependencies and integration: Integrates with volume/server lookup and RX connection creation from `afscp_volume.c` and `afscp_server.c`, callback bookkeeping from callback code outside this subset, and status cache routines from `afscp_fid.c`.

Risks: The retry loops treat any nonnegative RPC code as a loop break but later require `code == 0`, so unusual positive server results stop failover. `afscp_MakeDir` and `afscp_Symlink` do not explicitly validate null arguments like `afscp_CreateFile` does. On create/mkdir, `server` is used for callbacks after loops and assumes it still identifies the successful endpoint. Write operations depend on the caller choosing a writable volume.

Test signals: Mock or integration tests should verify server failover, null argument handling, parent stat refresh and invalidation, callback addition after create/mkdir, lock error mapping from AFS EAGAIN variants to `EWOULDBLOCK`, and read-only or missing-volume failures.
