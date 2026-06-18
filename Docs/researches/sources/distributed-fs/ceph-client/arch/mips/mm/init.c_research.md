# sources/distributed-fs/ceph-client/arch/mips/mm/init.c

Purpose: MIPS memory initialization and architecture MM glue. It sets up zero pages, coherent kmap mappings, user page copy helpers, fixmap page tables, MAAR speculative regions, zone limits, highmem constraints, init memory freeing, percpu areas, root page tables, and execmem module ranges.

Important APIs/functions: `arch_setup_zero_pages()`, `kmap_coherent()`, `kmap_noncoherent()`, `kunmap_coherent()`, `copy_user_highpage()`, `copy_to_user_page()`, `copy_from_user_page()`, `fixrange_init()`, `maar_init()`, `arch_zone_limits_init()`, `arch_mm_preinit()`, `free_initmem()`, and `setup_per_cpu_areas()`.

Control flow: boot code allocates zero pages with optional page coloring, creates temporary wired TLB mappings for coherent aliases, handles dcache alias-safe user copies, allocates fixmap PTE pages under highmem, records/configures MAAR ranges for RAM, trims unsupported highmem, frees init sections, and initializes percpu offsets.

State and persistence: exports `empty_zero_page`, `zero_page_mask`, page table roots/invalid tables, `pgd_current`, per-CPU offsets, and recorded MAAR config for secondary CPUs.

Dependencies and integration: tightly integrated with memblock, TLB wired entries, cache aliases, highmem, kcore, execmem, pgalloc, and CPU feature bits.

Risks and test signals: high risk around aliases and wired TLB slots. Test boot memory maps, highmem enable/disable, user page copy on aliasing CPUs, MAAR logging, secondary CPU MAAR replay, initmem poisoning/freeing, and module exec ranges.
