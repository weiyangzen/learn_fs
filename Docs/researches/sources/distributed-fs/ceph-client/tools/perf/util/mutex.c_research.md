
# sources/distributed-fs/ceph-client/tools/perf/util/mutex.c

Purpose: provides perf-local wrappers for `pthread_mutex_t` and `pthread_cond_t` that centralize attribute setup and error reporting.

Important APIs/types/functions: `mutex_init`, `mutex_init_pshared`, and `mutex_init_recursive` share `__mutex_init`, which creates attributes, uses error-checking mutexes in non-`NDEBUG` builds, optionally sets recursive or process-shared type, initializes the mutex, and destroys attributes. `mutex_destroy`, `mutex_lock`, `mutex_unlock`, and `mutex_trylock` wrap pthread calls. `cond_init`, `cond_init_pshared`, `cond_destroy`, `cond_wait`, `cond_signal`, and `cond_broadcast` wrap condition variables. `check_err` prints pthread error strings through perf debug logging.

Control flow: initialization constructs and tears down pthread attribute objects around the pthread primitive. Runtime lock/unlock/wait/signal calls only forward and log nonzero errors. `mutex_trylock` returns true on success, false on `EBUSY`, and false after logging other errors.

State and persistence: only initializes/destroys caller-owned synchronization objects. No global state is kept.

Dependencies: depends on pthreads, `debug.h`, Linux string helpers, and errno constants. The header's thread-safety annotations are suppressed for lock/unlock bodies with `NO_THREAD_SAFETY_ANALYSIS`.

Integration points: used by perf code that wants consistent debug diagnostics and optional static thread-safety annotations without using pthread APIs directly.

Risks: errors are logged but not fatal, so caller logic must not assume initialization succeeded after severe pthread failures. Recursive initialization overrides error-checking type. Process-shared primitives require shared storage and platform support. Test signals include build coverage with/without `NDEBUG`, simple lock/trylock/cond smoke tests, and process-shared usage tests where supported.
