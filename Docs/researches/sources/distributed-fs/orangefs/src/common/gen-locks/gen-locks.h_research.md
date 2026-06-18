# sources/distributed-fs/orangefs/src/common/gen-locks/gen-locks.h

Purpose: Defines OrangeFS's portable locking abstraction across POSIX pthreads, Win32 handles, and null-lock builds.

Important APIs/types: Selects default locking at compile time unless `__GEN_NULL_LOCKING__` is set: Win32 selects `__GEN_WIN_LOCKING__`, other platforms select `__GEN_POSIX_LOCKING__`. Defines `gen_mutex_t`, `gen_thread_t`, `gen_cond_t`, initializer macros, and `gen_mutex_*`, `gen_cond_*`, `gen_thread_self()` mappings.

Control flow contract: Callers use `gen_*` APIs without knowing the platform implementation. Static initializers are provided for mutexes/conditions; Windows implementation lazily initializes sentinel values.

State/persistence: Header does not persist state, but type selection determines ABI and static initializer values.

Dependencies/integration: Includes `pvfs2-internal.h`, pthreads or Windows headers, and is used widely in common OrangeFS code.

Risks: Null-lock branch contains an apparent typo in `gen_cond_timedwait(gen_cond_t *cond, gen_mutex_t *mutex\`, ...)`, which would break compilation if `__GEN_NULL_LOCKING__` is enabled. Some null-lock init/destroy macros expand to `do{}while(0)` and do not return an int despite call sites possibly expecting one. POSIX initializer macros include trailing semicolons.

Test signals: Compile all three locking modes, including `__GEN_NULL_LOCKING__`, and run contention/condition-variable tests on POSIX and Windows.
