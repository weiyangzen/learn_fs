# sources/distributed-fs/ceph-client/arch/mips/mm/Makefile

Purpose: Kbuild manifest for Linux/MIPS memory-management objects. It selects common MM, cache, TLB, page, ioremap, debug, and CPU-family-specific sources based on configuration.

Important build outputs: always builds `cache.o`, `context.o`, `extable.o`, `fault.o`, `init.o`, `mmap.o`, `page.o`, `page-funcs.o`, `pgtable.o`, `tlbex.o`, `tlbex-fault.o`, and `tlb-funcs.o`. It selects `uasm-micromips.o` or `uasm-mips.o`, includes `maccess.o` when EVA is disabled, and chooses 32-bit or 64-bit ioremap/pgtable variants.

Control flow: build-time conditionals wire CPU families: R3K, R4K, SB1, and Octeon cache/TLB/error-vector objects, plus optional secondary cache and debugfs modules.

State and persistence: no runtime state; it controls which code participates in the kernel image.

Dependencies and integration: central to all files in this subset. Mis-selection affects cache flush function pointer initialization, exception vectors, DMA coherency, and page table behavior.

Risks and test signals: verify configs combine exactly one appropriate cache/TLB family, 32/64-bit ioremap variants, highmem/hugetlb/DMA objects, and no missing object for selected CPU. Build matrix coverage is the primary test signal.
