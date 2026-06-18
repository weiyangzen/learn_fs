# sources/distributed-fs/ceph-client/arch/parisc/include/asm/spinlock_types.h

Purpose: defines PA-RISC raw spinlock and rwlock storage layouts and unlocked values.

Important APIs/types/functions: provides `arch_spinlock_t`, `arch_rwlock_t`, `__ARCH_SPIN_LOCK_UNLOCKED_VAL`, `SPINLOCK_BREAK_INSN`, and rwlock initializer constants.

Control flow: `spinlock.h` operations interpret these fields during lock/unlock/trylock paths.

State and persistence: lock structures persist wherever embedded in kernel objects. Dependencies and integration: used by generic lock initializers, lockdep, and PA-RISC spinlock operations.

Risks and test signals: initializer mismatch makes static locks start locked or corrupt. Test compile-time initializers, locktorture, and objdump/assert checks for lock alignment.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
