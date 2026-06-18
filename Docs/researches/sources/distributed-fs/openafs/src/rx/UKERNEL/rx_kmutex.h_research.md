# sources/distributed-fs/openafs/src/rx/UKERNEL/rx_kmutex.h

Purpose: user-space implementation of Rx kernel mutex/CV abstraction for UKERNEL builds.

Important APIs/types/functions: `afs_kmutex_t` as `opr_mutex_t`, `afs_kcondvar_t` as `opr_cv_t`, macros mapping to `opr_mutex_*` and `opr_cv_*`, plus no-op priority macros `SPLVAR`, `NETPRI`, and `USERPRI`.

Control flow: `CV_WAIT` drops the AFS global lock if held, waits on the OPR CV with the OPR mutex, then restores global-lock ordering by temporarily releasing/reacquiring the mutex around `AFS_GLOCK`.

State/persistence: OPR mutex and CV state supplied by callers.

Dependencies/integration: OpenAFS OPR lock library and UKERNEL global-lock emulation.

Risks: no `MUTEX_ASSERT` implementation; global-lock restoration must stay compatible with userspace thread scheduler. Test signals are UKERNEL listener/server thread handoff and CV wakeups.
