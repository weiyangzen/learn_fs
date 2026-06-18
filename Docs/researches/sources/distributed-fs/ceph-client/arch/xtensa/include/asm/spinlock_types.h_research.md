<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock_types.h

Purpose: exposes queued spinlock and queued rwlock type definitions for Xtensa while preventing direct inclusion outside Linux lock headers. Important contents are the inclusion guard check and includes of `asm-generic/qspinlock_types.h` and `asm-generic/qrwlock_types.h`.

Control flow is compile-time include validation only. State layout is the ABI of raw spinlock/rwlock objects embedded throughout the kernel. Dependencies are Linux lock header inclusion order and generic queued lock type definitions. Integration points are all raw/spin/rw lock declarations, lockdep, and generic locking code. Risks are direct inclusion errors, type-size mismatches if generic lock config changes, and ABI/layout assumptions in assembly or percpu structures. Test signals are allmodconfig-style builds, lock type compile checks, and locktorture on SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/spinlock_types.h -->
