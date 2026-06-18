# sources/distributed-fs/openafs/src/opr/lockstub.h

Purpose: no-op lock and condition-variable facade for non-pthread/LWP builds.

Important APIs/types/functions: typedefs `opr_mutex_t` and `opr_cv_t` as `int`; defines mutex and CV operations as no-ops, with `opr_mutex_tryenter` returning success.

Control flow: no runtime logic. It intentionally disables synchronization in code that is only cooperatively scheduled or single-threaded.

State and persistence: no state.

Dependencies/integration: hard-errors if included under `AFS_PTHREAD_ENV`. Used by `opr_cache.c` when pthreads are not active.

Risks and test signals: including this in real pthreaded code would create data races, so the preprocessor guard is critical. Build configuration tests should ensure pthread builds include `opr/lock.h` instead.
