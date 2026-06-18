# sources/distributed-fs/openafs/src/util/pthread_nosigs.h

Purpose: Provides macros to temporarily block most signals around `pthread_create()` so child threads do not receive process signals intended for the main thread.

Important macros: `AFS_SIGSET_DECL` declares saved and temporary signal sets, or a dummy integer on Windows. `AFS_SIGSET_CLEAR()` fills a signal set, removes fatal/debug signals such as `SIGSEGV`, `SIGBUS`, `SIGILL`, `SIGTRAP`, `SIGABRT`, and `SIGFPE` when present, and blocks it. `AFS_SIGSET_RESTORE()` restores the old mask.

Control flow and state: Header-only macro flow; callers wrap thread creation with clear/restore. On AIX it uses `sigthreadmask`; elsewhere pthread builds use `pthread_sigmask`. Windows macros only adjust a dummy variable.

Dependencies and integration: Requires signal and pthread types from surrounding includes plus `opr_Assert()`. Used by server threading setup and pthread worker creation.

Risks and test signals: Macro use requires correct lexical scope because declarations and temporary variables are emitted at call sites. Fatal signals are intentionally left unblocked for diagnostics. Test signals are signal handling behavior in pthreaded servers.
