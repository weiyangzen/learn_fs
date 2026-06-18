<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock_types.h

Purpose: selects the concrete spinlock type definitions for LoongArch.
Important APIs and types: includes `asm-generic/qspinlock_types.h` and read-write lock type definitions expected by generic locking code.
Control flow: no runtime flow; compile-time type selection only.
State and persistence: defines in-memory lock word layout through included type headers.
Dependencies and integration: must match `spinlock.h`, qspinlock code, and architecture atomic operations.
Risks and test signals: type/layout mismatch breaks locking ABI for static initializers and debug code. Signals include compile coverage, lockdep, and locktorture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/spinlock_types.h -->
