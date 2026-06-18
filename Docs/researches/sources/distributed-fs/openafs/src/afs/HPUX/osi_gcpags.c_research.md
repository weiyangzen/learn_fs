# sources/distributed-fs/openafs/src/afs/HPUX/osi_gcpags.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_gcpags.c

Purpose: implements HP-UX process-table traversal for PAG garbage collection when `AFS_GCPAGS` is enabled. It lets shared AFS code scan active process credentials and count live PAG users.

Important APIs/types/functions: `afs_osi_TraverseProcTable` and `afs_osi_proc2cred`. It calls `afs_GCPAGs_perproc_func`, `p_cred`, `system_proc`, and HP-UX process locking primitives.

Control flow: traversal locks `activeproc_lock`, `sched_lock`, and process credential state with `pcred_lock`, walks the active-process chain via `p_fandx`, skips system processes, locks each process with `mp_mtproc_lock`, calls the generic PAG scanner, then unlocks in reverse order. `afs_osi_proc2cred` returns `p_cred(p)` or no value for NULL.

State/persistence: no persistent state is created; it observes process credentials while locks are held. Results are consumed by shared PAG garbage collection state elsewhere.

Dependencies/integration: tightly coupled to HP-UX private process list and credential locking rules. The comment notes ambiguity between documented `mp_mtproc_lock` and actual `pcred_lock` usage, so it uses both.

Risks/test signals: returning without an explicit NULL for null process is a C compatibility risk. Lock ordering and long scans under global process locks can affect scheduler latency. Test with PAG creation/destruction, many active processes, concurrent `setgroups`, and builds with `AFS_GCPAGS` disabled/enabled.
