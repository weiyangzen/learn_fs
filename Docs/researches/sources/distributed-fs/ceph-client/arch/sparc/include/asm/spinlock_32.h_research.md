# sources/distributed-fs/ceph-client/arch/sparc/include/asm/spinlock_32.h

Purpose: SPARC32 spin/rwlock implementation using `ldstub`, interrupt masking around readers, and out-of-line rwlock slow paths.

Important APIs/types/functions: functions/helpers `arch_spin_lock`, `arch_spin_trylock`, `arch_spin_unlock`, `__arch_read_lock`, `__arch_read_unlock`, `arch_write_lock`, `arch_write_unlock`, `arch_write_trylock`, `__arch_read_trylock`; macros/constants `__SPARC_SPINLOCK_H`, `arch_spin_is_locked`, `arch_read_lock`, `arch_read_unlock`, `arch_read_trylock`.

Control flow: The file is driven by preprocessor gates such as `__SPARC_SPINLOCK_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, locking, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is the lock byte/word itself; rwlocks encode a writer byte plus a 24-bit reader counter and temporarily mask IRQs for reader operations.

Dependencies and integration points: Includes/dependencies: `asm/psr.h`, `asm/barrier.h`, `asm/processor.h`. Integration points include memory-management, locking, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Lockdep/debug-spinlock, IRQ-context readers, writer starvation, trylock behavior, and SMP stress tests are required signals.
