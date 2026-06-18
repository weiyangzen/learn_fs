# sources/distributed-fs/ceph-client/fs/nfsd/lockd.c

## Purpose
`lockd.c` provides the binding glue that lets lockd/NLM open and close files through NFSD without creating a hard module dependency between the NFS client, lockd, and nfsd modules.

## Important APIs, types, and functions
The binding object is `nfsd_nlm_ops` with callbacks `nlm_fopen()` and `nlm_fclose()`. Public lifecycle functions are `nfsd_lockd_init()` and `nfsd_lockd_shutdown()`, which assign or clear global `nlmsvc_ops`.

## Control flow
`nlm_fopen()` constructs a temporary `svc_fh` from an NFS filehandle, computes read or write access from POSIX open flags, adds NLM-specific bypass flags, calls `nfsd_open()`, releases the filehandle, and maps NFS status values to lockd errno values. `nfserr_jukebox` is translated to `-EWOULDBLOCK` so delegation conflicts can be retried. `nlm_fclose()` simply `fput()`s the file acquired through NFSD.

## State and persistence
The only state is the global lockd binding pointer. Opened files are ordinary `struct file` references held by lockd until `nlm_fclose()`.

## Dependencies and integration points
It integrates lockd's `nlmsvc_binding` interface with NFSD filehandle verification and VFS open behavior. The access flags intentionally allow GSS bypass and `NFSD_MAY_NLM` so exports with `insecure_locks` can authorize legacy NLM requests.

## Risks and test signals
Risks include incorrect NFS-to-errno mapping, accepting AUTH_NULL/AUTH_SYS NLM where exports did not intend it, delegation conflict behavior causing client-visible lock failures, and global binding races at module shutdown. Test signals include NLM read/write lock opens, stale filehandles, GSS NFS with AUTH_SYS NLM, `NFSEXP_NOAUTHNLM` exports, delegation conflict retries, and lockd activity across nfsd module load/unload.
