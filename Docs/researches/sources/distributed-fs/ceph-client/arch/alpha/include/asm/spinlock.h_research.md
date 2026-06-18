<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock.h

**Purpose:** Implements Alpha raw spinlock and rwlock operations using load-locked/store-conditional loops and memory barriers.

**Important APIs/types/functions:** `arch_spin_is_locked`, `arch_spin_value_unlocked`, `arch_spin_unlock`, `arch_spin_lock`, `arch_spin_trylock`, `arch_read_lock`, `arch_write_lock`, `arch_read_trylock`, `arch_write_trylock`, `arch_read_unlock`, and `arch_write_unlock`.

**Control flow:** Spin lock acquisition loops with `ldl_l`/`stl_c`, writes owner-like nonzero values, calls `cpu_relax`, and uses `smp_mb`/`mb` to enforce lock ordering. RW locks count readers and use a negative writer marker.

**State and persistence behavior:** State is the volatile `lock` word inside `arch_spinlock_t` or `arch_rwlock_t`; no other persistence.

**Dependencies and integration points:** Depends on Alpha barriers, current task pointer for debug-like lock values, processor relax, and generic raw spinlock wrappers.

**Risks:** Alpha's weak memory model makes barrier placement critical. LL/SC loops can livelock under heavy contention if relax/order assumptions are wrong. RW lock count overflow is theoretically possible under misuse.

**Test signals:** Lock torture, SMP stress, lockdep builds, rwlock reader/writer fairness tests, and interrupt-context locking tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/spinlock.h -->
