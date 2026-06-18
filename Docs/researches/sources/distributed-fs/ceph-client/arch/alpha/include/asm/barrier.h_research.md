# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/barrier.h

This header defines Alpha memory barrier primitives. `mb()` and `rmb()` emit `mb`; `wmb()` emits `wmb`. `__smp_load_acquire` performs a compile-time atomic-type assertion and a single `__READ_ONCE`, relying on Alpha-specific atomic rules and generic barrier composition. `__ASM_SMP_MB` expands to an assembly `mb` only under SMP.

It integrates with `asm-generic/barrier.h`, atomics, futexes, bitops, and I/O wrappers. There is no persistence; the state effect is CPU memory-order visibility. The key risk is Alpha's weak memory model: replacing these with weaker operations can break lockless code even when it works on stronger architectures. Tests are SMP boot/stress, atomic/futex paths, and memory-model litmus coverage.
