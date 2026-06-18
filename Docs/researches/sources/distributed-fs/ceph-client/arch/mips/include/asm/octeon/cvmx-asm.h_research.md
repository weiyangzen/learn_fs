# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-asm.h

## Purpose
This header centralizes Octeon executive assembly primitives for memory ordering, I/O DMA ordering, cache operations, special prefetch commands, population count, and hardware-register reads. It hides Cavium-toolchain versus generic-assembler differences behind CVMX macros.

## Important APIs, Types, and Functions
Important macros include `CVMX_SYNC`, `CVMX_SYNCW`, `CVMX_SYNCWS`, `CVMX_SYNCS`, string forms for inline assembly, `CVMX_SYNCIOBDMA`, `CVMX_PREPARE_FOR_STORE`, `CVMX_DONT_WRITE_BACK`, `CVMX_ICACHE_INVALIDATE`, `CVMX_ICACHE_INVALIDATE2`, `CVMX_DCACHE_INVALIDATE`, `CVMX_CACHE`, L2 helpers (`CVMX_CACHE_LCKL2`, `CVMX_CACHE_WBIL2`, `CVMX_CACHE_WBIL2I`, `CVMX_CACHE_LTGL2I`), `CVMX_POP`, `CVMX_DPOP`, `CVMX_RDHWR`, and `CVMX_RDHWRNV`.

## Control Flow
There is no C control flow. Each macro emits one or more MIPS/Octeon instructions directly at the caller site. `CVMX_SYNCW` intentionally emits two `syncw` instructions when Octeon instructions are available to work around CN3XXX Core-401 ordering errata; non-Octeon assembler paths fall back to portable `sync`.

## State and Persistence Behavior
The macros do not keep software state. They affect CPU ordering, cache state, prefetch/dirty status, or return transient hardware values. Cache invalidation and L2 operations have system-visible side effects and must be paired with correct address ranges and barriers by callers.

## Dependencies and Integration Points
It depends on `octeon-model.h` and compile-time `__OCTEON__` feature selection. It is included by low-level CVMX code such as FPA, FAU, command queues, packet I/O, and boot paths that need precise ordering around non-coherent bus, scratchpad, cache, and LL/SC operations.

## Risks
These macros are correctness-critical and architecture-specific. Replacing `syncw` sequences, dropping the memory clobber, or using cache op macros on the wrong address can introduce rare SMP ordering bugs, stale instruction/data cache state, or assembler incompatibilities. Deprecated no-op `CVMX_SYNCIO*` forms may mislead new code if it expects real I/O ordering.

## Test Signals
Useful signals are successful MIPS/Octeon builds with and without `__OCTEON__`, SMP stress around FPA/command-queue/FAU operations, instruction patching or generated-code tests after I-cache invalidation, and hardware data-path tests that would expose missing store or IOBDMA barriers.
