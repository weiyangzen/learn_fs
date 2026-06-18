<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types_up.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_types_up.h

Purpose: Defines UP architecture spinlock and rwlock placeholder types for use under `spinlock_types_raw.h`.

Important APIs/types/functions: `arch_spinlock_t`, `__ARCH_SPIN_LOCK_UNLOCKED`, `arch_rwlock_t`, and `__ARCH_RW_LOCK_UNLOCKED`.

Control flow: With `CONFIG_DEBUG_SPINLOCK`, `arch_spinlock_t` stores a volatile integer with inverted semantics: `1` unlocked, `0` locked. Without debug, the type is empty. RW locks are empty in both modes.

State and persistence behavior: Only debug UP spinlocks carry a lock state value. Non-debug UP locks have no storage.

Dependencies: Must be included through `spinlock_types_raw.h`.

Integration points: Used by UP builds to satisfy generic lock type declarations without pulling architecture SMP primitives.

Risks: Empty lock storage means layout and behavior differ sharply from SMP; code must not inspect lock internals.

Test signals: UP debug and non-debug builds; compile checks for static lock initialization; debug tests that catch uninitialized or double-lock patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types_up.h -->
