# sources/distributed-fs/ceph-client/arch/parisc/include/asm/spinlock.h

Purpose: implements PA-RISC raw spinlock and rwlock operations on top of the `ldcw` primitive.

Important APIs/types/functions: defines `arch_spin_val_check`, `arch_spin_is_locked`, `arch_spin_lock`, `arch_spin_unlock`, `arch_spin_trylock`, `arch_read_trylock`, `arch_write_trylock`, `arch_read_lock`, `arch_write_lock`, and unlock helpers.

Control flow: lock acquisition spins on an aligned lock word with PA-RISC load-and-clear semantics; rwlocks encode reader counts and writer state in the lock word.

State and persistence: lock words persist in shared kernel structures. Dependencies and integration: depends on barriers, `ldcw.h`, processor relax behavior, and spinlock type definitions.

Risks and test signals: fairness, alignment, and barrier behavior are SMP-critical. Test locktorture, rwlock stress, IRQ-safe locking, and lockdep.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
