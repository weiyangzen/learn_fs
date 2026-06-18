<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_types.h

Purpose: Defines the public `spinlock_t` type and initializers, selecting raw-spinlock-backed layout for non-RT kernels and rtmutex-backed layout for PREEMPT_RT kernels.

Important APIs/types/functions: `spinlock_t`, `__SPIN_LOCK_UNLOCKED()`, `DEFINE_SPINLOCK()`, `__LOCAL_SPIN_LOCK_UNLOCKED()` on RT, plus inclusion of `rwlock_types.h`.

Control flow: The preprocessor branches on `CONFIG_PREEMPT_RT`. Non-RT uses a union around `raw_spinlock_t` and optional lockdep overlay. RT includes `rtmutex.h` and defines `spinlock_t` as an `rt_mutex_base` plus optional lockdep map.

State and persistence behavior: Declares the memory layout for lock state. Non-RT state is a raw architecture lock and optional debug/lockdep metadata; RT state is rtmutex wait/owner state.

Dependencies: Depends on `spinlock_types_raw.h`, `rtmutex.h` when RT is enabled, and `rwlock_types.h`.

Integration points: Consumed by `spinlock.h` and any code that statically declares spinlocks.

Risks: Structure layout is configuration-dependent, so code must treat `spinlock_t` as opaque. Direct field access outside the locking implementation is fragile.

Test signals: Compile tests for static initializers in RT and non-RT builds; lockdep map offset assumptions; ABI-sensitive build checks in modules that embed `spinlock_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types.h -->
