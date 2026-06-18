# sources/distributed-fs/openafs/src/opr/opr_lock.h

Purpose: pthread-backed mutex and condition-variable wrapper API for OPR.

Important APIs/types/functions: typedefs `opr_mutex_t` as `pthread_mutex_t` and `opr_cv_t` as `pthread_cond_t`. Defines init/destroy/enter/exit/tryenter macros and CV init/destroy/wait/timedwait/signal/broadcast wrappers. With `OPR_DEBUG_LOCKS`, mutexes use `PTHREAD_MUTEX_ERRORCHECK` and `opr_mutex_assert` verifies ownership via `EDEADLK`.

Control flow: most operations call pthread functions and verify success with `opr_Verify`; timed wait allows success or `ETIMEDOUT` and returns the code.

State and persistence: synchronization objects are caller-owned memory. No persistence.

Dependencies/integration: includes pthreads, errno, and `afs/opr.h`. Installed as `opr/lock.h` and used by pthreaded OPR code, including cache.

Risks and test signals: macros abort on unexpected pthread errors, so callers cannot recover from misuse. Debug ownership assert temporarily locks error-check mutexes. Threaded unit tests should cover lock lifecycle and timed wait.
