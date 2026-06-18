# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/qspinlock_types.h

Purpose: This header defines the PowerPC queued spinlock word layout, static initializer, and byte ordering for the locked byte.

Important APIs/types/functions: It defines `_Q_SPINLOCK_LOCKED_BYTE` as byte 0 on big-endian and byte 3 on little-endian. `struct qspinlock` overlays a 32-bit `val` with `locked` and `locked_pending` byte/halfword views selected by endian layout. `__ARCH_SPIN_LOCK_UNLOCKED` initializes `.val = 0`. Bitfield constants define locked, pending, tail index, tail CPU offset, and masks. `_Q_TAIL_CPU_BITS` is 14 and `_Q_TAIL_CPU_MASK` spans the tail CPU field.

Control flow: There is no executable flow. Lock algorithms in `qspinlock.h` and slowpath code use these offsets and masks to test, set, and preserve locked/tail state.

State and persistence: The persistent state is the 32-bit lock word embedded in every queued spinlock. Endian-specific byte layout ensures `smp_store_release(&lock->locked, 0)` clears the correct byte across BE and LE kernels.

Dependencies and integration points: It depends on Linux type definitions and is consumed by architecture spinlock code, generic qspinlock slowpath, atomic operations, and assembly fast paths.

Risks and test signals: Layout mistakes break every spinlock on the architecture. The tail CPU bit width limits representable CPUs in the queue encoding and must align with NR_CPUS expectations. Tests include compile-time layout checks, locktorture on BE/LE, SMP stress with high CPU counts, qspinlock slowpath contention, and objdump/source checks of locked byte offset.
