# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/barrier.h

Purpose: defines PowerPC memory-ordering primitives for full barriers, SMP barriers, DMA barriers, acquire/release operations, speculation barriers, and persistent-memory write ordering.

Important APIs/types/functions: defines `__mb`, `__rmb`, `__wmb`, `__lwsync`, `__dma_rmb`, `__dma_wmb`, `__smp_mb`, `__smp_rmb`, `__smp_wmb`, `data_barrier(x)`, `__smp_store_release`, `__smp_load_acquire`, `barrier_nospec_asm`, `barrier_nospec()`, and `pmem_wmb()`.

Control flow: compile-time CPU family/config selects `SMPWMB` as `lwsync`, `mbar`, or `eieio`. Runtime control is limited to inline assembly barriers emitted at call sites.

State and persistence: no state is stored. Barriers constrain memory visibility, speculation, and persistent-store ordering.

Dependencies and integration points: depends on `<asm/ppc-opcode.h>` for patchable opcodes and `<asm-generic/barrier.h>` for generic wrappers. Used throughout locking, atomics, DMA, MMIO, PMEM, and side-channel mitigation paths.

Risks: using `lwsync` where `sync` is required can violate ordering, while excessive `sync` hurts performance. `barrier_nospec` relies on correct fixup slot sizing per CPU family. Persistent memory ordering assumes the preceding cache-block flush/persist instructions are used correctly.

Test signals: litmus/concurrency tests, DMA coherency tests, PMEM persistence tests, speculation-mitigation build/runtime checks, and inspection of generated opcodes for Book3S64/e500/BookE configs.
