<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/init.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/init.c

### Purpose
`init.c` owns early LoongArch memory-management setup: zone limits, initmem freeing, highmem fixed ranges, memory hotplug hooks, vmemmap population, fixmap PTE creation, global invalid page-table roots, and executable memory range setup.

### Important APIs, Types, And Functions
Key functions include `page_is_ram()`, `arch_zone_limits_init()`, `free_initmem()`, `fixrange_init()`, `arch_add_memory()`, `arch_remove_memory()`, `vmemmap_set_pmd()`, `vmemmap_check_pmd()`, `vmemmap_populate()`, `populate_kernel_pte()`, `__set_fixmap()`, and `execmem_arch_setup()`. Global tables include `swapper_pg_dir`, `invalid_pg_dir`, optional `invalid_pud_table`, optional `invalid_pmd_table`, and `invalid_pte_table`.

### Control Flow
Boot sets zone PFN limits for DMA32, normal, and highmem. Highmem builds PTE pages for pkmap and fixmap virtual ranges. Sparse vmemmap uses huge PMDs when possible. `populate_kernel_pte()` allocates missing P4D/PUD/PMD/PTE pages from memblock, initializes folded levels as needed, and returns the target PTE. `__set_fixmap()` writes or clears a fixed-address PTE and flushes on clear. Execmem setup describes the module range as executable allocation space.

### State, Persistence, And Dependencies
Persistent kernel state is early page-table memory, memblock reservations, zone PFN limits, vmemmap mappings, fixmap mappings, and exported invalid page-table tables. Dependencies include memblock, sparsemem/vmemmap, memory hotplug, highmem, hugetlb, execmem, LoongArch page-table allocators, and TLB flush APIs.

### Integration Points
`pgtable.c` initializes these tables; `kasan_init.c` temporarily switches page-directory roots; fixmap users include early ioremap, APIC/firmware mappings, and highmem. Memory hotplug calls `arch_add_memory()`/`arch_remove_memory()`.

### Risks
Memblock allocation failures panic during early boot. Incorrect invalid table initialization can make page-table walkers treat empty levels as present. Fixmap replacement checks reject non-empty PTEs; misuse can leave stale mappings. Hotplug removal currently delegates to generic removal and empty vmemmap free under vmemmap hotplug.

### Test Signals
Boot matrix across page-table levels, highmem, sparsemem, memory hotplug, and KASAN; run fixmap users, memory add/remove tests, vmemmap verification, and module allocation/execution tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/init.c -->
