# sources/distributed-fs/ceph-client/arch/arm/lib/bitops.h

Purpose: macro template for ARM atomic bit operations and test-and-bit operations used by `changebit.S`, `clearbit.S`, `setbit.S`, and test variants.

Control flow differs by architecture: ARMv6+ uses LDREX/STREX retry loops with optional SMP prefetch and barriers, while older CPUs disable IRQs around word load/modify/store. Test operations return the previous bit value and sync variants use stronger barriers. State is the target bit word only; no global state exists. Dependencies include `asm/assembler.h`, unwind annotations, SMP alternatives, and word-aligned bitmaps. Risks are unaligned bitmap pointers, missing memory barriers for synchronization use, exclusive-store livelock under contention, and IRQ masking latency on old CPUs. Test signals include atomic bitop stress under SMP, alignment fault checks, and verifying sync variants order surrounding memory accesses.
