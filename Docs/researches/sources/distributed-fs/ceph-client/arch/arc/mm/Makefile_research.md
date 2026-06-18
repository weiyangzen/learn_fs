# sources/distributed-fs/ceph-client/arch/arc/mm/Makefile

Purpose: selects ARC memory-management implementation objects.

Important entries: always builds `extable.o`, `ioremap.o`, `dma.o`, `fault.o`, `init.o`, `tlb.o`, `tlbex.o`, `cache.o`, and `mmap.o`; adds `highmem.o` when `CONFIG_HIGHMEM` is enabled.

Control flow: build-time only. The selected objects provide page fault handling, TLB refill/flush, cache maintenance, DMA coherency, I/O remapping, memory boot setup, mmap policy, and optional highmem kmap setup.

State and persistence: no runtime state.

Dependencies and integration: tied to ARC MMU, cache, and memory-map Kconfig options. `tlbex.o` provides assembly exception entry points consumed by low-level vector code.

Risks: omitting an object breaks required architecture hooks. Optional highmem must be built only when the generic highmem infrastructure expects ARC kmap setup.

Test signals: architecture build matrix with and without `CONFIG_HIGHMEM`, boot, page fault, TLB, DMA, and ioremap smoke tests.
