# sources/distributed-fs/openafs/src/afs/IRIX/osi_gcpags.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_gcpags.c

Purpose: intended to implement IRIX process traversal for PAG garbage collection, but it is incomplete.

Important APIs/types/functions: `SGI_ProcScanFunc`, `afs_osi_TraverseProcTable`, and `afs_osi_proc2cred`.

Control flow: when `AFS_GCPAGS` is enabled, traversal calls `procscan(SGI_ProcScanFunc, afs_GCPAGs_perproc_func)`. The scan callback currently returns 0 without invoking its argument, and `afs_osi_proc2cred` always returns NULL.

State/persistence: no state is maintained and no live credentials are exposed to PAG GC.

Dependencies/integration: tied to IRIX `procscan` and the shared `afs_GCPAGs_perproc_func` contract, but the TODO indicates the integration is not functional.

Risks/test signals: PAG garbage collection on IRIX may never see process credentials, causing token/PAG accounting leaks or premature cleanup depending on caller behavior. Test with `AFS_GCPAGS`, PAG creation, process exit, token cleanup, and instrumentation proving the generic per-process callback is invoked.
