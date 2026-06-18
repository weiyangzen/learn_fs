<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock_types.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock_types.h

**Purpose:** Defines Alpha raw spinlock and rwlock storage types for the generic spinlock layer.

**Important APIs/types/functions:** `arch_spinlock_t`, `__ARCH_SPIN_LOCK_UNLOCKED`, `arch_rwlock_t`, and `__ARCH_RW_LOCK_UNLOCKED`.

**Control flow:** No runtime flow; generic spinlock code instantiates these volatile words and uses operations from `spinlock.h`.

**State and persistence behavior:** The lock word is the entire lock state.

**Dependencies and integration points:** Must be included through `linux/spinlock_types_raw.h`; depends on generic raw spinlock layering.

**Risks:** Direct inclusion is rejected. Layout changes affect every raw lock object and module ABI assumptions.

**Test signals:** Compile raw spinlock users, run lockdep/locking selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock_types.h -->
