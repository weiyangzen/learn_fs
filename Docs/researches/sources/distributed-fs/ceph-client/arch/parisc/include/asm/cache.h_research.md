# sources/distributed-fs/ceph-client/arch/parisc/include/asm/cache.h

Purpose: declares PA-RISC cache geometry, alignment rules, cache/TLB purge instructions, and cache-initialization globals.

Important APIs/types/functions: defines `L1_CACHE_BYTES`, `ARCH_DMA_MINALIGN`, `ARCH_KMALLOC_MINALIGN`, `arch_slab_minalign`, `cache_line_size`, `pdtlb`, `pitlb`, `asm_io_fdc`, `asm_io_sync`, `asm_syncdma`, and declarations for cache setup and SID management.

Control flow: runtime cache setup populates stride and PDC cache information; low-level code uses inline assembly macros to flush TLB/cache lines and synchronize I/O.

State and persistence: globals such as `split_tlb`, `dcache_stride`, `icache_stride`, `cache_info`, and `btlb_info` persist after boot probing. Dependencies and integration: consumed by DMA, cacheflush, page-table, and allocator code.

Risks and test signals: wrong alignment or stride corrupts DMA and aliasing-cache behavior. Test with cache-info proc output, DMA stress, page alias tests, and boot on split/non-split TLB systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
