# sources/distributed-fs/openafs/src/opr/threadname.c

Purpose: sets the operating-system-visible name for the current pthread where supported.

Important APIs/types/functions: `opr_threadname_set(const char *threadname)` chooses among platform variants of `pthread_set_name_np`/`pthread_setname_np` based on configure macros and expected argument count.

Control flow: compiled only for pthread, non-NT builds. If no supported pthread naming function is detected, the function body effectively does nothing.

State and persistence: thread name is stored by the OS/thread library; no OpenAFS global state.

Dependencies/integration: public inline/no-op declaration is in `afs/opr.h`; this file provides the real implementation under pthread builds. Includes optional `pthread_np.h`.

Risks and test signals: platform APIs differ in name length limits and argument order; configure macros must be accurate. Tests can verify thread names through debugger/procfs where available, but compile coverage is the primary signal.
