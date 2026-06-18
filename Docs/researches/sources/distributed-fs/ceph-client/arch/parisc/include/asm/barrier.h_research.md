# sources/distributed-fs/ceph-client/arch/parisc/include/asm/barrier.h

Purpose: defines PA-RISC memory-ordering primitives for normal CPU, SMP, and DMA contexts.

Important APIs/types/functions: exports `synchronize_caches()`, `mb`, `rmb`, `wmb`, `dma_rmb`, `dma_wmb`, SMP acquire/release helpers, and then includes generic barrier fallbacks.

Control flow: on SMP-capable builds barriers issue PA-RISC `sync` sequences, with alternatives available for cache-related behavior; on simpler configurations they may collapse to compiler barriers.

State and persistence: no state is stored, but ordering affects visibility of shared memory, MMIO, and DMA descriptors. Dependencies and integration: integrates with `alternative.h`, atomics, spinlocks, device drivers, and page-table updates.

Risks and test signals: too-weak barriers cause rare data races or device coherency failures; too-strong barriers cost performance. Test with memory-model litmus tests, DMA stress, and SMP filesystem/network workloads.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
