# sources/distributed-fs/ceph-client/arch/sh/mm/init.c

Purpose: initializes SH memory, page tables, fixed mappings, bootmem/memblock reservations, zones, cache, PMB, ioremap, kmap, and final memory layout reporting.

Important APIs and state: `swapper_pg_dir`, `generic_mem_init`, weak `plat_mem_setup`, fixmap helpers `__set_fixmap`/`__clear_fixmap`, `page_table_range_init`, `allocate_pgdat`, `paging_init`, `mem_init`, and global `mem_init_done`.

Control flow: early setup adds configured memory, reserves kernel/zero-page/initrd/crashkernel ranges, enforces memory limits, computes low memory PFNs, initializes uncached/PMB/fixed ioremap/page tables, clears the initial PGD, sets TTB, creates fixmap page tables, and initializes coherent kmap. `mem_init` initializes cache hooks, flushes the zero page, initializes vsyscall, logs virtual layout, and marks memory init complete.

State and persistence: establishes permanent kernel page tables, node data, memblock reservations, memory boundary globals, fixmap mappings, cache hook state, and `mem_init_done`.

Dependencies and integration: memblock, NUMA/node data, TLB wiring, cacheflush, kexec/crashkernel, ioremap, PMB, uncached mapping, vsyscall, and platform `sh_mv` hooks.

Risks: early allocation/reservation mistakes can overlap kernel memory or lose RAM. Fixmap/TLB wired entries must be cleared consistently. `mem_init_done` gates ioremap strategy.

Test signals: boot memory maps, `/proc/iomem`, fixmap/ioremap early users, crashkernel/initrd reservation, and successful transition to normal allocation.
