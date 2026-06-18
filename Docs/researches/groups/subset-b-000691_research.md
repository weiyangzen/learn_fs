# subset-b-000691 Research

Grouped research for ARM64 memory-management and networking support files under `sources/distributed-fs/ceph-client`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/hugetlbpage.c

## Purpose
This file implements the ARM64 HugeTLB architecture hooks. It translates generic hugetlb requests into ARM64 page-table formats for PUD, PMD, contiguous-PMD, and contiguous-PTE huge pages, while preserving the architecture's break-before-make requirements for contiguous mappings. It also registers the supported hstates at boot and handles ARM64-specific HugeTLB migration, lookup, clearing, access-flag, write-protect, and protection-modification flows.

## Important APIs, Types, and Functions
The public hooks are `arch_hugetlb_cma_order()`, `arch_hugetlb_migration_supported()`, `huge_ptep_get()`, `set_huge_pte_at()`, `huge_pte_alloc()`, `huge_pte_offset()`, `hugetlb_mask_last_page()`, `arch_make_huge_pte()`, `huge_pte_clear()`, `huge_ptep_get_and_clear()`, `huge_ptep_set_access_flags()`, `huge_ptep_set_wrprotect()`, `huge_ptep_clear_flush()`, `arch_hugetlb_valid_size()`, `huge_ptep_modify_prot_start()`, and `huge_ptep_modify_prot_commit()`. The key helpers are `__hugetlb_valid_size()`, `num_contig_ptes()`, `find_num_contig()`, `get_clear_contig()`, `get_clear_contig_flush()`, `clear_flush()`, and `__cont_access_flags_changed()`.

`arch_hugetlb_cma_order()` chooses the largest gigantic HugeTLB page order for CMA reservation, preferring PUD-sized sections when supported and otherwise contiguous-PMD size. `__hugetlb_valid_size()` defines the ARM64 HugeTLB support matrix. `arch_make_huge_pte()` sets the correct huge/contiguous attributes for the chosen page size, converting through `pud_pte()` and `pmd_pte()` where needed.

## Control Flow
Boot initialization flows through `hugetlbpage_init()`, which asserts `HUGE_MAX_HSTATE >= 4` and registers PUD, contiguous-PMD, PMD, and contiguous-PTE hstates according to platform support. Allocation follows the page-table hierarchy in `huge_pte_alloc()`: PGD/P4D/PUD are allocated first, then the function returns a cast PUD entry, a shared or allocated PMD entry, an allocated PTE page, or a contiguous-PMD pointer depending on `sz`. Lookup mirrors this in `huge_pte_offset()`, including normalization to `CONT_PMD_MASK` or `CONT_PTE_MASK` for contiguous groups.

Contiguous entries drive most mutation complexity. `set_huge_pte_at()` computes the number of entries and underlying granule size, emits invalid entries directly, and performs `clear_flush()` before a valid-to-valid contiguous update. `huge_ptep_set_access_flags()` detects whether write, dirty, or accessed bits differ across the contiguous group; if so, it clears and flushes the whole group, preserves dirty/young state, and writes the rebuilt entries. `huge_ptep_set_wrprotect()` and `huge_ptep_clear_flush()` use the same group-wide clear/flush path.

## State and Persistence
Persistent state is stored in page tables, not file-local dynamic structures. Dirty and young bits are folded from all entries in a contiguous group into the returned representative PTE by `huge_ptep_get()` and `get_clear_contig()`. Boot hstate registration persists in the generic hugetlb subsystem. The CMA order hook affects long-lived CMA reservation sizing when `CONFIG_CMA` is enabled.

## Dependencies and Integration Points
The file depends on generic hugetlb, MM, TLB flush, and page-table helpers from `<linux/hugetlb.h>`, `<asm/tlbflush.h>`, and `<asm/tlb.h>`. It integrates with generic hugetlb through standard `arch_*` and `huge_ptep_*` hooks, with architecture feature detection through `pud_sect_supported()` and `alternative_has_cap_unlikely(ARM64_WORKAROUND_2645198)`, and with PMD sharing through `want_pmd_share()` and `huge_pmd_share()`.

## Risks
The major risk is violating ARM64 break-before-make rules for contiguous entries, which can produce TLB conflicts or architectural undefined behavior. Incorrect contiguous group sizing can lose dirty/accessed state or clear the wrong entries. `huge_pte_offset()` returns cast pointers at multiple levels, so callers must pass matching sizes. Erratum 2645198 adds a conditional flush when executable user mappings become non-executable; missing that path can leave stale executable permissions.

## Test Signals
Useful signals include hugetlb mmap/fault/unmap tests for all supported huge sizes, migration tests under `CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION`, dirty/accessed preservation tests for contiguous huge pages, PMD sharing tests, and boot logs showing expected `hugetlb_add_hstate()` sizes. TLB or permission regressions often surface as memory faults, failed hugepage mappings, warnings from the `VM_WARN_ON()`/`WARN_ON()` checks, or architecture-specific selftests around mprotect and exec permission changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/init.c

## Purpose
This file performs ARM64 early memory initialization. It selects the linear-map physical base, prunes memory that cannot be addressed, reserves kernel/initrd/crashkernel ranges, computes DMA zone limits, initializes SWIOTLB policy, marks page allocation availability, frees init memory, and configures executable memory allocation ranges for modules, kprobes, and BPF when `CONFIG_EXECMEM` is enabled.

## Important APIs, Types, and Functions
Exported or externally visible state includes `memstart_addr`, `arm64_dma_phys_limit`, `pfn_is_map_memory()`, `arch_zone_limits_init()`, `arm64_memblock_init()`, `bootmem_init()`, `arch_setup_zero_pages()`, `arch_mm_preinit()`, `page_alloc_available`, `mem_init()`, `free_initmem()`, `dump_mem_limit()`, and `execmem_arch_setup()`.

Key internal helpers include `arch_reserve_crashkernel()`, `max_zone_phys()`, `dma_limits_init()`, early parameter parser `early_mem()`, `random_bounding_box()`, and `module_init_limits()`. The file defines alignment policy through `ARM64_MEMSTART_SHIFT` and `ARM64_MEMSTART_ALIGN`, which are chosen from page granule and sparsemem constraints.

## Control Flow
The `mem=` early parameter sets `memory_limit`. `arm64_memblock_init()` then computes the usable linear region, caps it for 52-bit VA plus KVM nVHE constraints when needed, removes unsupported physical ranges above `PHYS_MASK_SHIFT`, aligns `memstart_addr`, removes memory outside the linear map, handles 52-bit VA fallback placement, applies `mem=`, restores mandatory kernel and initrd ranges, reserves the kernel image, converts initrd physical addresses to virtual addresses, and scans FDT reserved memory.

`bootmem_init()` derives min/max PFNs from memblock, runs early memory tests, initializes NUMA, reserves KVM hyp memory, initializes DMA limits, reserves CMA, reserves crashkernel memory, and dumps memblock. `arch_mm_preinit()` initializes SWIOTLB, forcing it for Realm guests and tuning it for unaligned kmalloc DMA bouncing. `mem_init()` marks `page_alloc_available` and updates SWIOTLB memory attributes. `free_initmem()` frees the linear-map alias of init sections and unmaps the virtual init range.

When executable memory support is built, `module_init_limits()` computes optional direct-branch and PLT-capable module windows, with KASLR-aware random bounding boxes. `execmem_arch_setup()` returns an `execmem_info` with ranges for modules, kprobes, and BPF.

## State and Persistence
`memstart_addr`, `arm64_dma_phys_limit`, `memory_limit`, `page_alloc_available`, `module_direct_base`, `module_plt_base`, and `execmem_info` are persistent boot-time state, mostly marked `__ro_after_init`. The memblock reservations and removals persist into the physical memory layout handed to the page allocator. The initrd virtual range and crashkernel reservations are globally visible to generic subsystems.

## Dependencies and Integration Points
The file integrates with memblock, DT/ACPI DMA discovery, NUMA, KVM hyp reservation, CMA, crashkernel, SWIOTLB, EFI/initrd, Realm services, and the generic execmem allocator. It relies on symbols from linker sections (`_text`, `_end`, `__init_begin`, etc.), ARM64 address translation helpers, and boot command line parsing.

## Risks
Incorrect linear-map sizing or `memstart_addr` alignment can make real RAM inaccessible or create invalid virtual-to-physical translations. Re-adding initrd or kernel ranges after memory limiting must avoid exceeding the linear-map window. DMA limit mistakes can break devices with restricted addressing. SWIOTLB policy is security-sensitive for Realm guests. Module range calculations must satisfy ARM64 relocation reach limits; otherwise modules may fail to load or require unnecessary PLTs.

## Test Signals
Boot logs for memory-limit warnings, SWIOTLB initialization, module range pages, crashkernel reservation, and initrd accessibility are primary signals. Kselftests or boot tests covering `mem=`, crashkernel, initrd placement, KASLR, memory hotplug baseline, DMA on limited devices, and module/BPF/kprobe allocation help validate this file. `pfn_is_map_memory()` correctness is indirectly tested by `/dev/mem`, ioremap, and pfn validation users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/ioremap.c

## Purpose
This file implements ARM64 `ioremap` policy around the generic remapper. It rejects physical addresses outside `PHYS_MASK`, refuses to ioremap normal mapped RAM, allows a single architecture hook to adjust or reject the mapping protection, initializes early ioremap support, and declares when `memremap()` may remap RAM.

## Important APIs, Types, and Functions
The main APIs are `arm64_ioremap_prot_hook_register()`, `__ioremap_prot()`, `early_ioremap_init()`, and `arch_memremap_can_ram_remap()`. The file-local state is `static ioremap_prot_hook_t ioremap_prot_hook`, registered once and rejected with `-EBUSY` on duplicate registration.

## Control Flow
`__ioremap_prot()` computes `last_addr = phys_addr + size - 1`, checks the address stays within `PHYS_MASK`, rejects attempts to map RAM using `pfn_is_map_memory()`, calls the optional hook with `(phys_addr, size, &pgprot)` and rejects on non-zero return, then delegates to `generic_ioremap_prot()`. `early_ioremap_init()` simply calls `early_ioremap_setup()` after fixmap setup. `arch_memremap_can_ram_remap()` returns whether the offset PFN is mapped memory.

## State and Persistence
Only the hook pointer persists. It is intended for one-time registration, for example by confidential-computing code that needs to alter page attributes before MMIO mappings are installed.

## Dependencies and Integration Points
The file depends on `pfn_is_map_memory()` from ARM64 init code, generic ioremap APIs, fixmap-backed early ioremap setup, and optional confidential computing or platform code registering an `ioremap_prot_hook_t`.

## Risks
The `last_addr` calculation assumes caller-provided size is sane; overflow behavior matters for boundary checks. Incorrect hook behavior can map MMIO with inappropriate cacheability or sharing attributes. Rejecting RAM ioremap is intentional, but platform code that historically relied on it must use the correct RAM remap path instead.

## Test Signals
Boot and driver probes using MMIO should succeed without warnings. Attempts to ioremap RAM should trigger the `WARN_ONCE()` path. Confidential-computing platforms should test hook registration, hook rejection, and protection rewriting. `memremap()` users can validate RAM remapping through `arch_memremap_can_ram_remap()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/kasan_init.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/kasan_init.c

## Purpose
This file initializes ARM64 KASAN shadow mappings for generic and software-tag KASAN modes. It first installs an early shadow that maps the entire shadow region to a shared zero page, then replaces that with real shadow pages for the kernel image and physical memory while preserving enough temporary mappings to keep instrumented code executable during the transition.

## Important APIs, Types, and Functions
External entry points are `kasan_early_init()`, `kasan_populate_early_vm_area_shadow()` under `CONFIG_KASAN_VMALLOC`, and `kasan_init()`. Internal helpers allocate shadow tables/pages (`kasan_alloc_zeroed_page()`, `kasan_alloc_raw_page()`), walk and populate page-table levels (`kasan_p4d_offset()`, `kasan_pud_offset()`, `kasan_pmd_offset()`, `kasan_pte_offset()`, `kasan_pgd_populate()` and lower-level populate helpers), manage root-level alignment (`root_level_aligned()`, `root_level_idx()`, `next_level_idx()`), clone temporary next-level tables (`clone_next_level()`), clear old shadow mappings (`clear_next_level()`, `clear_shadow()`), and build the full shadow (`kasan_init_shadow()`).

## Control Flow
`kasan_early_init()` performs build-time alignment checks, handles a misaligned shadow start by installing a one-off table to avoid sharing/corrupting the linear-region table, and populates `[KASAN_SHADOW_START, KASAN_SHADOW_END)` with early shadow tables and the early zero page.

`kasan_init()` calls `kasan_init_shadow()`, resets `init_task.kasan_depth`, then runs `kasan_init_generic()`. `kasan_init_shadow()` computes shadow ranges for the kernel image, modules, vmalloc, and memory banks. It copies `swapper_pg_dir` into `tmp_pg_dir`, optionally clones boundary next-level tables, switches TTBR1 to the temporary directory, clears the early shadow from the real swapper tables, maps real shadow pages for the kernel image and all memblock memory ranges, preserves early zero-shadow mappings for gaps, changes early shadow PTEs to read-only zero-page mappings, initializes the early shadow page, and switches TTBR1 back to `swapper_pg_dir`.

## State and Persistence
Persistent state is the KASAN shadow page-table structure and allocated shadow pages. `tmp_pg_dir` and cloned boundary tables are `__initdata` transition state. Early shadow tables and the early shadow page are reused as read-only zero shadow after full initialization. `init_task.kasan_depth` is reset so KASAN instrumentation becomes fully active.

## Dependencies and Integration Points
This code integrates with memblock allocation, ARM64 page-table population primitives, TTBR1 replacement, NUMA node lookup, linker section symbols, KASAN generic initialization, and optional vmalloc shadow population. It relies on `lm_alias()`, `__pa_symbol()`, and `__phys_to_kimg()` because it runs before all ordinary virtual mappings are safe.

## Risks
The transition from early to full shadow must not leave instrumented code without shadow coverage. Boundary handling is subtle when shadow start/end are not root-level aligned, especially with 4-level or 5-level paging and 64K page configurations. Incorrect table population can corrupt shared linear-map tables. Missing `dsb()` or TTBR replacement ordering can expose stale page-table entries to walkers.

## Test Signals
KASAN-enabled boot is the main integration test. Memory error injection or KASAN selftests should report valid diagnostics after `kasan_init()`. VMALLOC KASAN users should exercise `kasan_populate_early_vm_area_shadow()`. Boot-time failures usually appear as early panics, translation faults inside instrumented code, or KASAN shadow address range warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/kasan_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/mem_encrypt.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/mem_encrypt.c

## Purpose
This file is a top-level dispatcher for ARM64 memory encryption and decryption APIs. It deliberately avoids hard-coding the low-level implementation because details differ across confidential-computing environments such as pKVM or CCA.

## Important APIs, Types, and Functions
The important interfaces are `arm64_mem_crypt_ops_register()`, `set_memory_encrypted()`, and `set_memory_decrypted()`. The registered implementation is a `const struct arm64_mem_crypt_ops *crypt_ops` with `encrypt` and `decrypt` methods.

## Control Flow
Platform or realm-specific code calls `arm64_mem_crypt_ops_register()` once; duplicate registration returns `-EBUSY` and warns. `set_memory_encrypted()` and `set_memory_decrypted()` return success immediately when no ops are registered or the address alignment warning fires. Otherwise they dispatch to the registered `encrypt()` or `decrypt()` callback.

## State and Persistence
`crypt_ops` is the only persistent state. It is effectively a singleton process-wide hook for the architecture memory encryption API.

## Dependencies and Integration Points
This file integrates with generic memory encryption callers through exported GPL symbols and with ARM64 platform code through `<asm/mem_encrypt.h>`. In this source set, `pageattr.c` registers Realm operations using this hook.

## Risks
The dispatcher treats no registered operations as success, which is correct for systems without encryption transitions but can hide missing registration on systems that expected one. Alignment violations only warn and return success because the early guard condition is shared with the no-op case. Callback implementations must provide the real state transition and page-table synchronization.

## Test Signals
Confidential-computing tests should verify successful registration, duplicate registration failure, and actual encrypt/decrypt transitions through the registered callbacks. Non-confidential boots should exercise callers that expect no-op success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/mem_encrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/mmap.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/mmap.c

## Purpose
This file defines ARM64 user VMA protection translation and `/dev/mem` physical range validation. It maps generic `vm_flags` combinations to ARM64 `pgprot_t` values, adjusts that table for features such as Enhanced PAN and LPA2, and adds feature-specific bits for GCS, BTI, MTE, and permission overlays.

## Important APIs, Types, and Functions
The important data is `protection_map[16]` and `gcs_page_prot`. The main functions are `valid_phys_addr_range()`, `valid_mmap_phys_addr_range()`, initcall `adjust_protection_map()`, and exported `vm_get_page_prot()`.

## Control Flow
`valid_phys_addr_range()` accepts `/dev/mem` reads/writes only when the whole range is memblock memory and the start address is map memory. `valid_mmap_phys_addr_range()` rejects mmap requests beyond `PHYS_MASK`. During `adjust_protection_map()`, Enhanced PAN converts execute-only entries from readable executable to `PAGE_EXECONLY`, and LPA2 clears `PTE_SHARED` from all protections and GCS protection.

`vm_get_page_prot()` selects GCS shadow-stack protection if supported and requested, otherwise indexes `protection_map` by read/write/exec/shared flags. It then adds `PTE_GP` for BTI, Normal-Tagged memory attributes for MTE mappings, and POE pkey bits when supported.

## State and Persistence
`protection_map` and `gcs_page_prot` are initialized once and then become read-only after init. There is no per-VMA persistence in this file beyond the protection bits returned to generic mmap/mprotect paths.

## Dependencies and Integration Points
The file depends on memblock for `/dev/mem` validation and on ARM64 CPU feature helpers for EPAN, LPA2, GCS, MTE, BTI, and POE. It integrates directly with generic MM through `vm_get_page_prot()` and with userspace ABI flags such as `VM_MTE`, `VM_ARM64_BTI`, `VM_SHADOW_STACK`, and pkey flags.

## Risks
Protection-bit composition is security-sensitive. Incorrect execute-only handling can expose readable executable mappings; missing BTI or MTE attributes can break user ABI promises; wrong LPA2 shareability bits can produce invalid descriptors. `/dev/mem` checks can be too strict across adjacent memblock regions with differing attributes, as noted in the source comment.

## Test Signals
Signals include mmap/mprotect tests for read/write/execute combinations, EPAN execute-only behavior, BTI-enabled mappings, MTE `PROT_MTE` mappings, GCS shadow-stack VMAs, POE pkey behavior, and `/dev/mem` range validation tests. Boot-time feature combinations with LPA2 are especially useful for catching descriptor-bit mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/mmu.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/mteswap.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/mteswap.c

## Purpose
This file preserves ARM64 MTE allocation tags across swap-out and swap-in. Because tags are separate metadata from page contents, the file stores per-page tag snapshots in an xarray keyed by swap entry value and restores them when swapped pages return.

## Important APIs, Types, and Functions
Persistent storage is `static DEFINE_XARRAY(mte_pages)`. Public helpers include `mte_allocate_tag_storage()`, `mte_free_tag_storage()`, `mte_save_tags()`, `mte_restore_tags()`, `mte_invalidate_tags()`, `mte_invalidate_tags_area()`, `arch_prepare_to_swap()`, and `arch_swap_restore()`. Internal cleanup helper `__mte_invalidate_tags()` derives the swap entry from a page.

## Control Flow
`arch_prepare_to_swap()` exits immediately without MTE support. Otherwise it iterates over each page in the folio and calls `mte_save_tags()`. `mte_save_tags()` skips untagged pages, allocates `MTE_PAGE_TAG_STORAGE`, saves tags from `page_address(page)`, and stores the buffer in `mte_pages` under `page_swap_entry(page).val`; replacement frees the old buffer. On failure, `arch_prepare_to_swap()` invalidates entries saved earlier in the folio.

`arch_swap_restore()` iterates over folio pages and increasing swap entries. `mte_restore_tags()` loads the saved buffer, attempts to enable page tagging with `try_page_mte_tagging()`, restores tags, and marks the page tagged. `mte_invalidate_tags()` and `mte_invalidate_tags_area()` erase per-entry or whole-swap-type metadata and free buffers.

## State and Persistence
Tag snapshots persist in the `mte_pages` xarray while the corresponding swap entries remain valid. The key is the raw `swp_entry_t.val`, so state lifetime must track swap invalidation. The page's `page_mte_tagged` state controls whether tags are saved and is restored after successful tag restoration.

## Dependencies and Integration Points
The file integrates with generic swap through `arch_prepare_to_swap()` and `arch_swap_restore()`, with swap invalidation through `mte_invalidate_tags*()`, with xarray for indexed storage, and with ARM64 MTE primitives such as `mte_save_page_tags()`, `mte_restore_page_tags()`, `try_page_mte_tagging()`, and `set_page_mte_tagged()`.

## Risks
Leaking tag buffers is the main state risk if swap invalidation paths miss an entry. Incorrect entry arithmetic for multi-page folios could restore tags to the wrong page. Allocation failure during swap preparation must clean up already-saved tags for the folio, which this file handles. Concurrency relies on xarray locking semantics; direct area invalidation uses explicit `xa_lock()`.

## Test Signals
MTE swap tests should allocate tagged memory, force swap-out/in, and verify tag preservation. Swapoff or swap-area invalidation should leave no leaked buffers. Multi-page folio swapping is an important edge case. Error-injection for `kmalloc()` or `xa_store()` should exercise cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/mteswap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/pageattr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/pageattr.c

## Purpose
This file implements ARM64 runtime page-attribute changes for vmalloc mappings, direct-map validity changes, and Realm memory encryption/decryption transitions. It walks kernel page tables, updates PTE/PMD/PUD attributes, splits large mappings when necessary, and flushes TLBs when valid cached translations may exist.

## Important APIs, Types, and Functions
The main exported behavior is through `set_memory_ro()`, `set_memory_rw()`, `set_memory_nx()`, `set_memory_x()`, `set_memory_valid()`, `set_direct_map_invalid_noflush()`, `set_direct_map_default_noflush()`, `set_direct_map_valid_noflush()`, `__kernel_map_pages()` under `CONFIG_DEBUG_PAGEALLOC`, `kernel_page_present()`, and `realm_register_memory_enc_ops()`.

Important helpers and types include `struct page_change_data`, `set_pageattr_masks()`, `pageattr_pud_entry()`, `pageattr_pmd_entry()`, `pageattr_pte_entry()`, `pageattr_ops`, `rodata_full`, `can_set_direct_map()`, `update_range_prot()`, `__change_memory_common()`, `change_memory_common()`, and `__set_memory_enc_dec()`.

## Control Flow
The page-table walk callbacks update leaf entries by clearing `clear_mask` first and then setting `set_mask`, because some bits alias each other. `update_range_prot()` first calls `split_kernel_leaf_mapping()` for the range, then walks kernel page tables under lazy MMU mode. `__change_memory_common()` wraps this and flushes the TLB unless the transition is only present-invalid to valid.

`change_memory_common()` validates that the requested range is page-aligned and fully covered by one vmalloc/vmap area with `VM_ALLOC` and without `VM_ALLOW_HUGE_VMAP`. For read-only changes under `rodata_full`, it also applies the same permission update to each backing page's linear-map alias. It flushes lazy vmalloc aliases before updating the vmalloc mapping itself.

Direct-map helpers use `can_set_direct_map()` to no-op unless the platform requires page-granular direct-map control. Realm encryption/decryption uses `__set_memory_enc_dec()`: it requires Realm world and a linear-map address, invalidates the mapping while setting or clearing `PROT_NS_SHARED`, calls RSI to change protected/shared state, then makes the mapping valid again. Realm failures warn that pages may be leaked.

## State and Persistence
`rodata_full` is a boot-time policy flag that affects whether backing linear-map aliases are updated alongside vmalloc mappings. Page-table entries themselves persist the changed protections. Realm transitions persist both in page-table attributes (`PROT_NS_SHARED`, valid/invalid state) and in external Realm state managed through RSI calls.

## Dependencies and Integration Points
This file depends on the `mmu.c` split and walk infrastructure, generic vmalloc metadata, cache/TLB flush helpers, mem_encrypt dispatcher, KFENCE, debug pagealloc, Realm services (`rsi_set_memory_range_*()`), and page-table bit definitions. It registers Realm memory encryption ops with `arm64_mem_crypt_ops_register()`.

## Risks
Changing attributes on live kernel mappings is unsafe unless the range is already page-granular or can be split safely. The vmalloc area checks intentionally reject huge vmaps to avoid splitting live section mappings. Missing linear-map alias updates under `rodata_full` could leave writable aliases of read-only text/data. Realm transitions intentionally invalidate mappings before RSI calls; failures can force callers to leak memory to avoid unsafe reuse.

## Test Signals
Useful tests include module text permission changes, BPF executable memory transitions, debug pagealloc direct-map invalidation, KFENCE pool behavior, rodata alias checks, Realm shared/protected memory conversion tests, and `kernel_page_present()` checks. TLB flush issues may appear as stale executable/write permissions or data aborts after validity toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/pageattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/pgd.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/pgd.c

## Purpose
This file allocates and frees user PGD tables on ARM64, accounting for runtime-folded page-table levels. When the effective PGD size is one page it delegates to the generic page-table allocator; otherwise it uses a dedicated slab cache with architecture-required alignment.

## Important APIs, Types, and Functions
The primary functions are `pgd_alloc()`, `pgd_free()`, and `pgtable_cache_init()`. The internal helper `pgdir_is_page_size()` determines whether `PGD_SIZE == PAGE_SIZE` or whether configured 4/5-level paging has folded at runtime. Persistent state is `static struct kmem_cache *pgd_cache`.

## Control Flow
`pgd_alloc()` selects `__pgd_alloc(mm, 0)` for page-sized directories and `kmem_cache_alloc(pgd_cache, GFP_PGTABLE_USER)` otherwise. `pgd_free()` mirrors that choice. `pgtable_cache_init()` returns early for page-sized directories, validates 64-byte alignment under 52-bit physical addressing, and creates `pgd_cache` with object size and alignment equal to `PGD_SIZE`.

## State and Persistence
The slab cache persists after initialization when needed. Individual PGDs persist as part of `mm_struct` address-space state and are freed through the matching allocator path.

## Dependencies and Integration Points
This file integrates with generic MM PGD allocation hooks, ARM64 runtime page-table folding (`pgtable_l4_enabled()`, `pgtable_l5_enabled()`), slab allocation, and architecture alignment requirements for 52-bit physical addressing.

## Risks
Allocator mismatch between folded and non-folded cases would corrupt memory. Alignment is architecturally required for top-level tables, so the cache alignment must match `PGD_SIZE`. Runtime folding decisions must remain consistent between allocation and free.

## Test Signals
Process creation/destruction under different VA-level configurations exercises these hooks. Booting 4-level and 5-level kernels on hardware with and without the corresponding runtime support validates folding. Slab diagnostics or page-table allocation failures would expose allocator issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/pgd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/physaddr.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/physaddr.c

## Purpose
This file provides debug-checked ARM64 virtual-to-physical conversion helpers. It warns when generic code uses `virt_to_phys()` on a non-linear-map address and validates that `__pa_symbol()` is used only for kernel image symbols.

## Important APIs, Types, and Functions
The exported functions are `__virt_to_phys()` and `__phys_addr_symbol()`. They wrap lower-level unchecked helpers `__virt_to_phys_nodebug()` and `__pa_symbol_nodebug()` with validation.

## Control Flow
`__virt_to_phys()` resets address tags with `__tag_reset()`, warns if the address is not in the linear map via `__is_lm_address()`, then returns the unchecked physical address. `__phys_addr_symbol()` uses `VIRTUAL_BUG_ON()` to assert the address falls between `KERNEL_START` and `KERNEL_END`, then returns the unchecked kernel-symbol physical address.

## State and Persistence
There is no persistent state. The functions provide runtime diagnostics and exported conversion behavior.

## Dependencies and Integration Points
The file integrates with generic callers of `virt_to_phys()` and `__pa_symbol()`, ARM64 memory-layout macros, MM debug infrastructure, and tag-reset helpers used on tagged architectures.

## Risks
The primary risk is caller misuse. `virt_to_phys()` on vmalloc/module/fixmap addresses is invalid and this wrapper warns to catch that. `__pa_symbol()` outside the kernel image is a bug and triggers a virtual-address bounds assertion.

## Test Signals
Debug builds should warn on intentional misuse tests. Normal boot and driver operation should not produce `virt_to_phys used for non-linear address` warnings. Symbol conversion users are indirectly tested by early page-table and memblock setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/physaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/proc.S -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/proc.S

## Purpose
This assembly file contains low-level ARM64 MMU and CPU context routines. It saves/restores CPU suspend state, replaces TTBR1 through an idmap trampoline, rewrites kernel mappings to non-global for KPTI, coordinates secondary CPUs while the linear map is split to PTEs, and initializes EL1 memory-control registers before turning on the MMU.

## Important APIs, Types, and Functions
Important symbols include `cpu_do_suspend`, `cpu_do_resume`, `idmap_cpu_replace_ttbr1`, `idmap_kpti_install_ng_mappings`, `wait_linear_map_split_to_ptes`, and `__cpu_setup`. It defines TCR/MAIR flag macros for page granule, KASLR, KASAN software tags, MTE, cacheability, shareability, and initial memory attributes. `MAIR_EL1_SET` initializes device, normal non-cacheable, normal, and normal-tagged attribute slots.

## Control Flow
`cpu_do_suspend` stores per-CPU architectural state into `struct cpu_suspend_ctx`, including thread pointer registers, context ID, debug lock state, CPACR, TCR, VBAR, MDSCR, SCTLR, per-CPU offset, SP_EL0, x18, and optionally TCR2. `cpu_do_resume` restores those registers, preserves current T0SZ while restoring TCR, reinstalls pointer-auth keys, disables user PMU/AMU access, clears RAS deferred status if supported, and returns after an ISB.

`idmap_cpu_replace_ttbr1` runs from `.idmap.text`: it first points TTBR1 at `reserved_pg_dir`, invalidates TLBs, then installs the requested TTBR1. This prevents conflicting TLB entries during kernel page-table replacement.

Under KPTI, `idmap_kpti_install_ng_mappings` runs in stop-machine context. Secondary CPUs switch to reserved TTBR1 and wait on `idmap_kpti_bbml2_flag`; CPU0 switches to a temporary PGD, walks `swapper_pg_dir`, marks valid global entries non-global, handles folded or LPA2 levels, restores TTBR1, and clears the flag. `wait_linear_map_split_to_ptes` uses the same wait protocol when CPU0 splits the linear map while secondaries remain on the idmap.

`__cpu_setup` invalidates local TLBs, resets control/debug access registers, builds MAIR/TCR/TCR2 values based on configured granule and detected features, computes physical address size, optionally enables hardware AF and HAFT, configures permission indirection registers when supported, writes MAIR/TCR/TCR2, and returns `INIT_SCTLR_EL1_MMU_ON` to the boot path.

## State and Persistence
Persistent effects include CPU system registers (`MAIR_EL1`, `TCR_EL1`, `TCR2_EL1`, `SCTLR_EL1`, `TTBR1_EL1`), rewritten `swapper_pg_dir` entries for KPTI non-global mappings, and saved suspend context memory. The idmap wait flag coordinates temporary stop-machine state.

## Dependencies and Integration Points
This file is tightly coupled to `mmu.c`, `head.S`, suspend code, pointer authentication, CPU feature alternatives, KPTI, idmap text placement, and system register definitions. The KPTI and BBML2 routines are invoked from C through physical idmap function pointers.

## Risks
Ordering and exception masking are critical. TTBR replacement must avoid exceptions while TTBR1 is transient. KPTI page-table surgery must use break-before-make when remapping temporary fixmap slots and must keep secondaries away from `swapper_pg_dir`. `cpu_do_resume` must stay in sync with `struct cpu_suspend_ctx`. Incorrect TCR/MAIR setup can prevent the MMU from booting or misclassify memory attributes.

## Test Signals
Signals include successful boot on all supported page sizes and VA/PA widths, suspend/resume stress, KPTI-enabled syscall/exception tests, CPU hotplug and stop-machine paths, MTE/KASAN tagged-address boot, LPA2/VA52 boot, and hibernate/kexec paths that replace TTBR1. Failures are typically early boot hangs, synchronous exceptions during MMU enable, suspend resume crashes, or KPTI mapping warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/proc.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/ptdump.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/ptdump.c

## Purpose
This file implements ARM64 kernel page-table dumping and W+X/non-UXN validation. It formats page-table ranges by protection attributes, registers a debugfs dump for kernel page tables, and provides `ptdump_check_wx()` to detect insecure writable-executable or executable kernel mappings.

## Important APIs, Types, and Functions
Important data includes `pte_bits[]`, `kernel_pg_levels[]`, and `kernel_ptdump_info`. Main functions are `dump_prot()`, `note_prot_uxn()`, `note_prot_wx()`, `note_page()` and its level wrappers, `note_page_flush()`, `ptdump_walk()`, `ptdump_check_wx()`, and initcall `ptdump_init()`.

## Control Flow
`ptdump_init()` builds address markers for the linear map, optional KASAN shadow, modules, vmalloc, vmemmap, PCI I/O, and fixmap ranges; initializes per-level masks from `pte_bits[]`; and registers `kernel_page_tables` through `ptdump_debugfs_register()`.

`ptdump_walk()` builds a `ptdump_pg_state` and delegates to `arm64_ptdump_walk_pgd()`, which increments `arm64_ptdump_lock_key` while walking. `note_page()` coalesces consecutive ranges with the same level and protection bits, emits marker headers, formats range size units, and invokes W+X/non-UXN checks when enabled. `ptdump_check_wx()` performs a non-printing walk over the kernel range and returns false if insecure pages are found.

## State and Persistence
The debugfs info and address markers persist after device init. During a walk, state is local in `ptdump_pg_state`. The static key `arm64_ptdump_lock_key` coordinates with page-table freeing code in `mmu.c` so freed tables are not raced by a dump.

## Dependencies and Integration Points
This file integrates with generic `ptdump_walk_pgd()`, debugfs registration, ARM64 page-table bit definitions, KASAN layout, virtual memory layout constants, and `mmu.c` page-table free synchronization.

## Risks
Incorrect bit masks can misreport page protections or miss W+X mappings. Walk synchronization is important because debugfs can dump while kernel page tables are being freed. Marker ordering must match the virtual layout, especially with variable `vabits_actual` and optional KASAN.

## Test Signals
Reading debugfs `kernel_page_tables` should produce coherent ranges and markers. `ptdump_check_wx()` should pass after rodata protections are applied. Tests should include KASAN and non-KASAN layouts, memory hotplug/table-free activity while dumping, and configurations with folded page-table levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/ptdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/ptdump_debugfs.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/ptdump_debugfs.c

## Purpose
This small file exposes ARM64 page-table dumps through debugfs. It bridges a `seq_file` show callback to the generic ARM64 `ptdump_walk()` implementation.

## Important APIs, Types, and Functions
The important functions are `ptdump_show()` and `ptdump_debugfs_register()`. `DEFINE_SHOW_ATTRIBUTE(ptdump)` creates the debugfs file operations.

## Control Flow
`ptdump_debugfs_register()` creates a read-only debugfs file with mode `0400`, stores the supplied `struct ptdump_info *` as private data, and uses `ptdump_fops`. When read, `ptdump_show()` retrieves that private info and calls `ptdump_walk()`.

## State and Persistence
The debugfs dentry is not stored in this file, but the file persists in debugfs after registration. Runtime state is passed through `seq_file->private`.

## Dependencies and Integration Points
It depends on debugfs, seq_file helpers, and the ARM64 ptdump interface. `ptdump.c` calls `ptdump_debugfs_register()` during device init.

## Risks
This file intentionally has minimal policy. Risks are mostly from debugfs availability and from trusting the lifetime of the supplied `ptdump_info`. Permission `0400` restricts access but does not hide mapping layout from privileged readers.

## Test Signals
With debugfs mounted and ptdump initialized, the registered file should exist and reading it should invoke `ptdump_walk()` without errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/ptdump_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/trans_pgd-asm.S -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/trans_pgd-asm.S

## Purpose
This assembly file defines a temporary EL2 vector table used by transitional page-table flows for hibernate and kexec. It provides just enough hypervisor-stub behavior to set EL2 vectors or perform a soft restart while other unexpected vectors loop or return an error.

## Important APIs, Types, and Functions
The exported symbol is `trans_pgd_stub_vectors`, with end label `__trans_pgd_stub_vectors_end`. Helper macros `invalid_vector` and `el1_sync_vector` generate vector slots. It handles `HVC_SET_VECTORS`, `HVC_SOFT_RESTART`, and returns `HVC_STUB_ERR` for unexpected EL1 synchronous calls.

## Control Flow
Most vector slots branch to themselves forever via `invalid_vector`, making unexpected exceptions obvious and non-returning. The EL1 synchronous vector compares `x0` with `HVC_SET_VECTORS`; on match it writes `x1` to `vbar_el2`, clears `x0`, and `eret`s. It next checks `HVC_SOFT_RESTART`; on match it rearranges arguments and branches to the restart target. Otherwise it places `HVC_STUB_ERR` in `x0` and returns.

## State and Persistence
The vector table is code/data copied by `trans_pgd_copy_el2_vectors()` in `trans_pgd.c`. Its persistent effect is limited to setting `vbar_el2` or transferring control for restart.

## Dependencies and Integration Points
It integrates with kexec and hibernate transitional PGD code and constants from `<asm/kvm_asm.h>`. The table size is checked with an `.org` assertion to fit within `SZ_2K`, matching ARM64 vector table layout.

## Risks
The argument shuffle for soft restart must match callers' ABI. Any vector overflow would corrupt adjacent code, hence the size check. Unexpected exceptions intentionally do not recover, which is appropriate for transitional contexts but makes debugging dependent on where the CPU stalls.

## Test Signals
Hibernate restore and kexec soft restart paths exercise this table. `trans_pgd_copy_el2_vectors()` should copy exactly `ARM64_VECTOR_TABLE_LEN` and cache-maintain it. Failures appear as failed HVC_SET_VECTORS, restart hangs, or vector-size build issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/trans_pgd-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/trans_pgd.c -->
# sources/distributed-fs/ceph-client/arch/arm64/mm/trans_pgd.c

## Purpose
This file builds transitional page tables for hibernate restore and kexec. These tables are used when the normal kernel page tables may be overwritten during a world transition, so the code can keep executing and access required mappings safely.

## Important APIs, Types, and Functions
Main public APIs are `trans_pgd_create_copy()`, `trans_pgd_idmap_page()`, and `trans_pgd_copy_el2_vectors()`. Internal recursive copy helpers are `copy_page_tables()`, `copy_p4d()`, `copy_pud()`, `copy_pmd()`, and `copy_pte()`. Allocation is abstracted through `struct trans_pgd_info` and `trans_alloc()`.

## Control Flow
`trans_pgd_create_copy()` allocates a new top-level table, then calls `copy_page_tables()` for the requested virtual range. The copy walk follows the current kernel page tables from PGD down. Missing entries are skipped. Table entries allocate destination tables as needed. Leaf entries are copied after making them valid kernel mappings and writable with `pte_mkvalid_k()`/`pmd_mkvalid_k()`/`pud_mkvalid_k()` and `*_mkwrite_novma()` so the transitional context can access them.

`trans_pgd_idmap_page()` constructs a TTBR0 page table bottom-up for one physical page that may be outside the VA range normally handled by kernel populate helpers. It computes whether 48-bit or 52-bit physical coverage is needed, allocates levels from leaf upward, fills the index for the destination physical address, and returns `trans_ttbr0` plus the matching `TCR_T0SZ`.

`trans_pgd_copy_el2_vectors()` allocates a page, copies `trans_pgd_stub_vectors`, and cleans/invalidates caches to the point of unification and coherency before returning the physical vector address.

## State and Persistence
All page tables and copied vectors are allocated through the caller-provided allocator and persist only for the transition. The file does not own global state. Output state is returned through `dst_pgdp`, `trans_ttbr0`, `t0sz`, and `el2_vectors`.

## Dependencies and Integration Points
The file integrates with hibernate, kexec, ARM64 page-table primitives, cache maintenance, and the assembly vector table in `trans_pgd-asm.S`. It depends on `trans_pgd_info` callers to provide zeroed, suitably aligned pages and lifetime management.

## Risks
Copying invalid or overly permissive attributes could break the transition; this file intentionally forces valid writable kernel mappings for accessibility. Allocation failure must abort cleanly. The bottom-up idmap assumes a single-page mapping and maximum T0SZ calculation; errors there can make restart/restore code unreachable. Cache maintenance is required after copying EL2 vectors.

## Test Signals
Hibernate resume and kexec reboot are the main integration tests. Tests should cover high physical addresses requiring 52-bit handling, allocation failure injection, and EL2 vector copy paths. Failures show as transition hangs, faults after page-table switch, or failed soft restart/vector setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/mm/trans_pgd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/net/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/net/Makefile

## Purpose
This Makefile selects ARM64 networking code for the kernel build. It conditionally builds the ARM64 BPF JIT compiler objects when `CONFIG_BPF_JIT` is enabled.

## Important APIs, Types, and Functions
The only build rule is `obj-$(CONFIG_BPF_JIT) += bpf_jit_comp.o bpf_timed_may_goto.o`.

## Control Flow
Kbuild expands `obj-y` or `obj-m` according to the value of `CONFIG_BPF_JIT`. When enabled, the two object files are compiled and linked into the architecture networking subtree; when disabled, they are omitted.

## State and Persistence
There is no runtime state. The persistent effect is build graph inclusion of BPF JIT support objects.

## Dependencies and Integration Points
This integrates with the kernel Kbuild system, ARM64 BPF JIT implementation files, and the global `CONFIG_BPF_JIT` option.

## Risks
The risk is build coverage: if a new ARM64 BPF JIT object is added but not listed, it will not link; if an object is listed without its config dependency, disabled builds can fail.

## Test Signals
Build ARM64 kernels with `CONFIG_BPF_JIT=y` and `CONFIG_BPF_JIT=n`. The enabled build should include `bpf_jit_comp.o` and `bpf_timed_may_goto.o`; the disabled build should not compile them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/net/bpf_jit.h -->
# sources/distributed-fs/ceph-client/arch/arm64/net/bpf_jit.h

## Purpose
This header provides compact ARM64 instruction-emission macros for the ARM64 BPF JIT compiler. It wraps generic `aarch64_insn_gen_*()` helpers with BPF-JIT-friendly names for branches, load/store forms, atomics, arithmetic, bitfield operations, logical operations, hints, system register reads, and barriers.

## Important APIs, Types, and Functions
The file defines register aliases such as `A64_R()`, `A64_FP`, `A64_LR`, `A64_ZR`, and `A64_SP`; variant helpers like `A64_VARIANT()` and `A64_SIZE()`; branch macros `A64_CBZ`, `A64_CBNZ`, `A64_B_`, `A64_B`, `A64_BL`, `A64_BR`, `A64_BLR`, and `A64_RET`; load/store macros for register and immediate offsets; pair push/pop macros; exclusive and acquire/release load/store macros; LSE atomic macros; arithmetic and comparison macros; move-wide and bitfield macros; data-processing macros; logical macros; hint macros for PAC, BTI, and NOP; and barrier/system-register macros.

## Control Flow
There is no runtime control flow in the header. Each macro expands to a generated 32-bit ARM64 instruction value, generally by passing the requested registers, sizes, variants, immediates, and operation enum to `<asm/insn.h>` generator functions. Some macros encode ARM64 aliases, such as `MOV` as an ADD or register move depending on SP use, `CMP`/`CMN`/`TST` using zero-register destinations, `MUL` using `MADD` with zero accumulator, and store-only LSE operations using `XZR` as the destination.

## State and Persistence
The header has no state. Its outputs become persistent only when the BPF JIT writes generated instruction words into executable JIT images.

## Dependencies and Integration Points
It depends on `<asm/insn.h>` and its instruction generator API. It is consumed by ARM64 BPF JIT implementation files selected by the adjacent Makefile. The macros encode ARM64 ABI assumptions about register operands, instruction variants, and immediate scaling; branch immediate macros shift BPF-style instruction counts into byte offsets.

## Risks
Incorrect scaling or size variants can generate invalid code or branch to wrong offsets. Atomic memory order macros must match BPF memory semantics. Aliases involving SP and zero register need care because ARM64 encodes SP specially in some instruction classes. If `<asm/insn.h>` generator behavior changes, wrappers may need adjustment.

## Test Signals
BPF JIT selftests, verifier/JIT comparison tests, atomic operation tests, tail-call/branch tests, BTI/PAC-enabled JIT tests, and disassembly inspection of generated programs are useful signals. Build tests with `CONFIG_BPF_JIT=y` ensure all macros used by the compiler still type-check against the instruction generator API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/net/bpf_jit.h -->
