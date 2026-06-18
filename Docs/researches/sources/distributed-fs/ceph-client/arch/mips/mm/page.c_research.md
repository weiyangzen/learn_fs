# sources/distributed-fs/ceph-client/arch/mips/mm/page.c

Purpose: generates optimized MIPS `clear_page` and `copy_page` routines at boot using the micro-assembler, with optional SiByte DMA page operations.

Important APIs/functions: `build_clear_page()` and `build_copy_page()` synthesize instruction streams into the slots from `page-funcs.S`. Helper `set_prefetch_parameters()` selects word sizes, cache line sizes, prefetch modes, and loop sizes by CPU type. Optional `clear_page()` and `copy_page()` use SB1 DMA descriptors when `CONFIG_SIBYTE_DMA_PAGEOPS` is enabled.

Control flow: the generator runs once per routine via atomics, initializes labels/relocs, validates prefetch assumptions, emits prefetch/cache/store/load loops with CPU errata workarounds, resolves relocations, checks code size, and logs debug words. The DMA variants fall back to CPU routines unless both addresses are KSEG0, then program per-CPU descriptors and busy-wait for interrupt completion.

State and persistence: generated code persists in kernel text slots. Static prefetch and loop parameters are boot-time state. SB1 DMA uses cacheline-aligned per-channel descriptors.

Dependencies and integration: called by CPU cache init (`r3k`, `r4k`, `octeon`) and used by core page allocator/copy paths. Depends on uasm, CPU feature bits, cache ops, and optional SiByte registers.

Risks and test signals: generated code size, R6 prefetch offsets, DADDIU workaround, cache-line assumptions, and DMA busy-wait are sensitive. Test clear/copy correctness, boot on CPU variants, KSEG0 and non-KSEG0 paths, and debug code dump when enabled.
