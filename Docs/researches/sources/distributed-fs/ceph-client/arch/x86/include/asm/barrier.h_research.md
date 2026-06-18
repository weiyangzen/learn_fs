
# sources/distributed-fs/ceph-client/arch/x86/include/asm/barrier.h

Purpose: x86 memory, speculation, DMA, SMP, acquire/release, and atomic-barrier definitions.

Important APIs and control flow: 32-bit `mb/rmb/wmb` use alternatives from locked stack add to SSE fences; 64-bit defines raw `mfence/lfence/sfence` helpers. `array_index_mask_nospec()` emits compare/sbb to build an all-ones or zero mask. `barrier_nospec()` patches to `lfence` when required. SMP barriers exploit x86 ordering, locked add, compiler barriers, and `xchg` for store-mb.

State, dependencies, and risks: no direct state; effects are ordering constraints visible to all lockless code and device interactions. Dependencies include alternatives, cpufeatures, generic barrier fallbacks, and x86 TSO assumptions. Risks include weakening required speculation barriers, using DMA barriers where real device ordering is needed, and compiler reordering around acquire/release primitives. Test signals are memory-model litmus tests, nospec tests, KCSAN, and driver DMA stress.
