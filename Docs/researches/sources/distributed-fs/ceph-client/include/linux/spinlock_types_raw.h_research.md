<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types_raw.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_types_raw.h

Purpose: Defines `raw_spinlock_t`, the low-level lock type used when callers require true spinning semantics and by regular spinlocks on non-RT kernels.

Important APIs/types/functions: `raw_spinlock_t`, `SPINLOCK_MAGIC`, `SPINLOCK_OWNER_INIT`, `RAW_SPIN_DEP_MAP_INIT()`, `SPIN_DEP_MAP_INIT()`, `LOCAL_SPIN_DEP_MAP_INIT()`, `SPIN_DEBUG_INIT()`, `__RAW_SPIN_LOCK_INITIALIZER()`, `__RAW_SPIN_LOCK_UNLOCKED()`, and `DEFINE_RAW_SPINLOCK()`.

Control flow: Selects architecture raw lock types from `<asm/spinlock_types.h>` on SMP or `spinlock_types_up.h` on UP, then layers debug ownership and lockdep metadata over `arch_spinlock_t`.

State and persistence behavior: Raw lock state is the architecture lock word plus optional debug magic, owner CPU, owner pointer, and dependency map. Static initializers define the persistent initial state for global locks.

Dependencies: Uses `linux/types.h`, architecture or UP spinlock types, and `lockdep_types.h`.

Integration points: Foundation for `spinlock_types.h`, `spinlock.h`, raw lock APIs, and synchronization in low-level code where sleeping is not allowed.

Risks: Debug and lockdep fields affect size/layout. Callers must not assume raw locks are interchangeable with `spinlock_t` under RT.

Test signals: Static initializer build tests, debug spinlock owner tracking, lockdep wait-type validation, and architecture-specific raw lock tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types_raw.h -->
