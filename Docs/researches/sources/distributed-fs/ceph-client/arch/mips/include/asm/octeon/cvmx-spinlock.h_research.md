# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spinlock.h

Purpose: implements CVMX spinlocks for synchronization with the OCTEON boot monitor and non-Linux programs, distinct from Linux kernel spinlocks.

Important APIs/types/functions: `cvmx_spinlock_t` wraps a volatile 32-bit value. Constants define unlocked/locked values and an initializer. APIs are `cvmx_spinlock_init`, `cvmx_spinlock_locked`, `cvmx_spinlock_unlock`, `cvmx_spinlock_trylock`, `cvmx_spinlock_lock`, plus bit-lock variants `cvmx_spinlock_bit_lock`, `cvmx_spinlock_bit_trylock`, and `cvmx_spinlock_bit_unlock`.

Control flow: lock and trylock use MIPS `ll`/`sc` loops in inline assembly. Full-word locks spin until the value is zero and then store one. Bit locks test and set bit 31 while preserving the lower 31 bits. Unlock paths issue `CVMX_SYNCWS`, clear the lock word or bit, and issue another `CVMX_SYNCWS`.

State and persistence: lock state is in caller-provided memory. It is volatile process/hardware synchronization state only. The bit-lock form intentionally shares a word with low 31 data bits protected by the lock.

Dependencies and integration points: includes `cvmx-asm.h` for synchronization and OCTEON/MIPS assembly helpers. Intended integration is firmware/monitor/shared-memory coordination, not Linux `spinlock_t` replacement.

Risks: these locks lack Linux lockdep, IRQ, preemption, and SMP debug semantics. Bit unlock is non-atomic and assumes the lower bits are protected by the lock. Inline assembly uses `$at` and OCTEON bit instructions, so toolchain/ISA compatibility matters. Recursive lock debugging is disabled by default.

Test signals: compile tests must target the OCTEON MIPS assembler. Runtime tests should exercise lock acquisition under contention, trylock return semantics matching Linux convention, memory ordering around shared monitor data, and bit-lock preservation of lower bits.
