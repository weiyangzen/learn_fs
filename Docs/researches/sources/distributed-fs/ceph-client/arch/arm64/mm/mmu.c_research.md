# sources/distributed-fs/ceph-client/arch/arm64/mm/mmu.c

## Purpose
This is the central ARM64 kernel page-table construction and mutation file. It creates the early linear map and ID map, enforces safe live attribute changes, handles block/contiguous mapping splitting, protects rodata, sets up KPTI trampoline/non-global mappings, supports KFENCE and vmemmap mappings, implements memory hotplug map/unmap, frees kernel page-table pages safely around ptdump, provides user PTE protection modification hooks for errata, and replaces TTBR1 safely.

## Important APIs, Types, and Functions
Important global state includes `arm64_ptdump_lock_key`, `kimage_voffset`, `__boot_cpu_mode`, `rodata_is_rw`, `__early_cpu_boot_status`, `swapper_pgdir_lock`, `fixmap_lock`, `linear_map_requires_bbml2`, and `idmap_kpti_bbml2_flag`.

Core mapping helpers include `pgattr_change_is_safe()`, `early_pgtable_alloc()`, `init_pte()`, `alloc_init_cont_pte()`, `init_pmd()`, `alloc_init_cont_pmd()`, `alloc_init_pud()`, `alloc_init_p4d()`, `__create_pgd_mapping_locked()`, `__create_pgd_mapping()`, `early_create_pgd_mapping()`, `create_mapping_noalloc()`, `create_pgd_mapping()`, `update_mapping_prot()`, and `__map_memblock()`.

Splitting and mutation helpers include `split_contpte()`, `split_pmd()`, `split_contpmd()`, `split_pud()`, `split_kernel_leaf_mapping()`, `range_split_to_ptes()`, `linear_map_maybe_split_to_ptes()`, `mark_linear_text_alias_ro()`, and `mark_rodata_ro()`. Boot and layout functions include `map_mem()`, `declare_kernel_vmas()`, `create_idmap()`, and `paging_init()`. Hotplug and vmemmap functions include `vmemmap_populate()`, `vmemmap_free()`, `arch_add_memory()`, `arch_remove_memory()`, `arch_get_mappable_range()`, and the memory removal notifier. Other integration points include `pud_set_huge()`, `pmd_set_huge()`, `pud_free_pmd_page()`, `pmd_free_pte_page()`, `modify_prot_start_ptes()`, `ptep_modify_prot_start()`, `modify_prot_commit_ptes()`, `__cpu_replace_ttbr1()`, and `arch_set_user_pkey_access()`.

## Control Flow
Initial paging setup starts at `paging_init()`: `map_mem()` builds the linear map, `memblock_allow_resize()` enables later memblock changes, `create_idmap()` builds identity mappings for idmap text and optional KPTI/BBML2 synchronization data, and `declare_kernel_vmas()` registers early vmalloc metadata for kernel segments.

`map_mem()` decides whether the linear map must use PTE mappings by consulting debug pagealloc, rodata-full, KFENCE, Realm state, and BBML2 capability. It temporarily marks kernel text/rodata as `NOMAP`, maps all memblock memory as tagged Normal kernel memory with executable mappings disabled, maps the kernel image linear alias separately without contiguous mappings, clears the `NOMAP`, and maps the early KFENCE pool if allocated.

The mapping builder walks top-down from PGD to PTE. It prefers PUD/PMD block mappings and contiguous PTE/PMD groups when alignment and flags permit, otherwise allocates lower-level tables through the selected allocator. Every live update is checked by `pgattr_change_is_safe()`, which allows only safe permission-like changes to existing valid mappings and rejects PFN changes, contiguous live changes, unsafe global transitions, and memory-type changes other than Normal/Normal-Tagged.

Permission and direct-map changes rely on splitting. `split_kernel_leaf_mapping()` ensures a target range is represented at safe granularity, using `linear_map_requires_bbml2` and runtime capabilities to decide whether live splitting is allowed. On systems that cannot tolerate live large-to-small mapping transitions, `linear_map_maybe_split_to_ptes()` stops all CPUs and has CPU0 split the linear map while secondaries wait on the idmap. `mark_rodata_ro()` changes rodata and early text ranges to read-only after alternative patching.

KPTI setup uses `kpti_install_ng_mappings()` and `idmap_kpti_install_ng_mappings` in `proc.S` to rewrite global kernel mappings to non-global when needed. `map_entry_trampoline()` builds a trampoline page table and fixmap entries for EL0 kernel-unmapped transitions.

Memory hotplug mapping uses `arch_add_memory()` to create linear mappings, clear memblock `NOMAP`, and call `__add_pages()`. Removal calls `__remove_pages()` and unmaps/free empty page-table tables. The notifier prevents boot memory removal and rejects removals whose linear-map or vmemmap edges would split a leaf entry. Vmemmap population uses huge PMD mappings for suitable 4K-page section-sized ranges and base pages otherwise.

## State and Persistence
Persistent state is mostly page-table content in `swapper_pg_dir`, `idmap_pg_dir`, `tramp_pg_dir`, and dynamically allocated page-table pages. `rodata_is_rw` tracks whether direct writes to `swapper_pg_dir` are still possible; after rodata is protected, `set_swapper_pgd()` uses a fixmap and spinlock. `linear_map_requires_bbml2` records boot-time linear-map splitting policy. KFENCE pool state, memory hotplug mappings, vmemmap mappings, and KPTI non-global conversion persist for the lifetime of the kernel.

## Dependencies and Integration Points
The file integrates with memblock, KASAN, KFENCE, KPTI, stop_machine, generic page-table walkers, ptdump, memory hotplug, sparse vmemmap, pkeys/POE, Realm/CCA state, TLB flushing, fixmap, ID map assembly routines, module/vmalloc layout symbols, and generic MM page table constructors/destructors. It also exports architecture behavior to `/dev/mem` through `phys_mem_access_prot()` and to page attribute code through `split_kernel_leaf_mapping()`.

## Risks
This file is high-risk because it mutates live kernel mappings. Bugs can create TLB conflicts, stale permissions, executable writable mappings, invalid table descriptors, or memory hotplug removal of still-needed memory. Break-before-make and BBML2 capability windows are subtle, especially before CPU capabilities are finalized. `pgattr_change_is_safe()` is a key safety boundary; relaxing it incorrectly would permit unsafe live changes. Hotplug removal must avoid freeing page tables visible to ptdump, hence the static-key and mmap-lock synchronization.

## Test Signals
Important signals include successful boot across page sizes and VA/PA widths, `ptdump_check_wx()` passing, rodata write-protection tests, debug pagealloc and KFENCE tests, KASAN/MTE tagged linear-map boot tests, KPTI boot and syscall tests, memory hotplug add/remove/offline tests, sparse vmemmap validation, pkey selftests, hibernate/kexec ID-map interactions, and warning-free page-table split/permission changes. Failures often show as early boot translation faults, `BUG_ON()` from unsafe mapping updates, W+X warnings, memory hotplug notifier rejections, or TLB-related data aborts.
