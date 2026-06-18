# Research: subset-b-000769

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-8xx.h

## Purpose
This header describes the Motorola/Freescale MPC8xx nohash MMU register interface and the Linux-side page-size/context contract for 8xx software-assisted TLB handling.

## Important APIs, Types, And Functions
It defines `SPRN_MI_*`, `SPRN_MD_*`, `SPRN_M_*`, `MI_*`, and `MD_*` masks for instruction/data TLB control, AP groups, EPN/TWC/RPN tablewalk state, CASID, and boot TLB setup. It exports `mm_context_t`, `struct mmu_psize_def`, `mmu_psize_defs[]`, `mmu_pin_tlb()`, `shift_to_mmu_psize()`, `mmu_psize_to_shift()`, vmap sizing hooks, and TLB-miss patch symbols.

## Control Flow
Runtime flow lives in assembly TLB miss handlers and MM setup code. This header supplies the register numbers and bit encodings used when handlers read miss state, compute page-table entries, write RPN registers to instantiate TLB entries, or patch optimized miss exits.

## State And Persistence Behavior
Persistent state includes per-mm context id/activity/vDSO/PTE fragment pointers and processor MMU SPR contents. Pinned TLB entries remain active until explicitly replaced or invalidated. `PHYS_IMMR_BASE` derives the internal memory map register base from `SPRN_IMMR`.

## Dependencies And Integration Points
It depends on page-size Kconfig, `linux/mmdebug.h`, `linux/sizes.h`, and common PowerPC MMU definitions. It integrates with 8xx TLB miss code, vmap/ioremap mapping size selection, KUAP/KUEP AP group policy, and boot-time TLB pinning.

## Risks And Edge Cases
AP group encodings are subtle and security-relevant. 16K page mode changes PTE fragmentation. Large vmap mappings require address, PFN, and maximum-shift alignment. Incorrect MI/MD bit definitions can produce silent memory permission, cacheability, or tablewalk corruption.

## Test Signals
Build and boot `CONFIG_PPC_8xx` with 4K and 16K pages, exercise vmalloc/ioremap mappings including 16K and 512K candidates, run user/kernel access permission tests, and stress TLB miss/refill and pinned kernel mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgalloc.h

## Purpose
This header supplies 32-bit nohash page-table allocation glue for the effectively two-level PowerPC layout, where PMD allocation is folded away and PMD entries point at PTE storage.

## Important APIs, Types, And Functions
`pmd_free()` and `__pmd_free_tlb()` are no-ops because no real separately allocated PMD pages exist. `pmd_populate_kernel()` and `pmd_populate()` encode a PTE table pointer into the PMD, using a kernel virtual address on BookE and a physical address on non-BookE, with `_PMD_PRESENT` and optionally `_PMD_USER`.

## Control Flow
Generic memory-management code calls these helpers while constructing page tables. The only branch is the BookE/non-BookE address encoding decision.

## State And Persistence Behavior
No state is owned here. The helpers persist encoded PTE-table addresses in the caller's PMD/PGD slot until the mapping is cleared or the containing page table is freed by upper-layer code.

## Dependencies And Integration Points
It depends on `linux/threads.h`, `linux/slab.h`, `__pa()`, and platform `_PMD_*` masks from the selected nohash PTE header. It is included through `asm/nohash/pgalloc.h`.

## Risks And Edge Cases
Using physical addresses on BookE or virtual addresses on non-BookE would break TLB-miss tablewalks. `_PMD_USER` matters for user PTE pages on non-BookE. The no-op free helpers rely on the folded layout remaining true.

## Test Signals
Cross-build 32-bit nohash BookE and non-BookE configs, fault user and kernel pages, unmap ranges under TLB gather, and validate PMD contents with debug page-table checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgtable.h

## Purpose
This header defines the 32-bit nohash page-table geometry, virtual-memory layout, selected processor-specific PTE bit header, PMD accessors, and swap PTE encoding.

## Important APIs, Types, And Functions
It defines PTE/PMD/PUD/PGD index sizes, table sizes, `PGDIR_SHIFT`, `PTRS_PER_*`, `USER_PTRS_PER_PGD`, `FIXADDR_TOP`, `IOREMAP_*`, and `VMALLOC_*`. It selects `pte-44x.h`, `pte-e500.h`, or `pte-8xx.h`, sets `PTE_RPN_SHIFT`, `PTE_RPN_MASK`, and `MAX_POSSIBLE_PHYSMEM_BITS`, and provides `pmd_none()`, `pmd_bad()`, `pmd_present()`, `pmd_clear()`, `pmd_pfn()`, `pmd_page()`, and swap conversion macros.

## Control Flow
There is little runtime control flow beyond inline accessors. Page fault, mmap, swap, and ioremap code consume the geometry and accessors while walking or modifying page tables.

## State And Persistence Behavior
The file owns no mutable state. It defines how state is stored in page-table entries, including whether PMDs carry physical addresses or BookE kernel virtual addresses and how swap type/offset/exclusive bits are encoded.

## Dependencies And Integration Points
It depends on `asm-generic/pgtable-nopmd.h`, scheduler/thread constants, `asm/mmu.h`, highmem/KASAN options, and the selected nohash PTE format. It integrates with generic MM, swap, fixmap, vmalloc, and ioremap code.

## Risks And Edge Cases
The VM layout is constrained by highmem, KASAN, early ioremap growth, and `ioremap_bot`. PTEs may be 64-bit on 32-bit systems with extended physical addressing. BookE PMD virtual-address encoding is a common portability trap.

## Test Signals
Build 44x, 85xx, and 8xx variants, enable swap, highmem, KASAN where supported, run page-table debug checks, and exercise vmalloc/ioremap overlap boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-44x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-44x.h

## Purpose
This header defines the PPC44x nohash PTE bit layout, mapping Linux permission/cache flags into 44x TLB fields that support 36-bit addressing.

## Important APIs, Types, And Functions
It defines `_PAGE_PRESENT`, `_PAGE_WRITE`, `_PAGE_EXEC`, `_PAGE_READ`, `_PAGE_DIRTY`, `_PAGE_SPECIAL`, `_PAGE_ACCESSED`, endian/guarded/coherent/cache/write-through bits, `_PMD_*` masks, `_PTE_NONE_MASK`, `_PAGE_BASE_NC`, and `_PAGE_BASE`, then includes `pgtable-masks.h` for standard Linux protections.

## Control Flow
No executable flow is present. TLB miss handlers and page-table operations interpret these bits when loading TLB words and when generic MM helpers test permissions.

## State And Persistence Behavior
The persistent state is the encoded PTE value stored in page tables and later reflected into hardware TLB entries. `_PTE_NONE_MASK` preserves ERPN bits while testing for none entries.

## Dependencies And Integration Points
It is selected by `CONFIG_44x` from the 32-bit nohash pgtable header. It integrates with 44x TLB refill assembly, I-cache flushing policy through executable PTE changes, and SMP coherency policy via `_PAGE_COHERENT`.

## Risks And Edge Cases
Low PTE bits overlap swap-entry discrimination, so bit changes can break swap. Large-page PMD support is explicitly not implemented. Coherency bits differ across original 440 and later 460-class parts.

## Test Signals
Build 44x kernels with and without SMP, run swap and executable mmap tests, validate no stale instruction-cache behavior after modifying executable user mappings, and exercise DMA mappings on coherent variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-44x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-8xx.h

## Purpose
This header defines the MPC8xx PTE and PMD bit layout plus specialized PTE update helpers for the 8xx hardware-assisted software tablewalk model.

## Important APIs, Types, And Functions
It defines 8xx `_PAGE_*` permission/cache/huge/SPS bits, `_PMD_*` page-size and access bits, kernel/user protection combinations, `pte_wrprotect()`, `pte_read()`, `pte_write()`, `pte_mkwrite_novma()`, `pte_mkhuge()`, `ptep_set_wrprotect()`, `__ptep_set_access_flags()`, `__pte_leaf_size()`, `ptep_is_8m_pmdp()`, `number_of_cells_per_pte()`, `__pte_update()`, `pte_update()`, and 16K `ptep_get()`.

## Control Flow
Permission changes flow through `pte_update()`. For huge 8M PMD mappings it updates two PMD-backed PTE ranges; otherwise it updates replicated PTE cells. `__ptep_set_access_flags()` updates accessed/dirty/exec/protection bits and flushes the affected TLB page.

## State And Persistence Behavior
8xx page-table state is unusual: 16K pages duplicate four cells, 512K pages duplicate 128 cells, and 8M mappings duplicate 1024 cells per 4M half. Dirty and access state are software-maintained and reflected into APG/TWC fields during refill.

## Dependencies And Integration Points
It depends on 8xx MMU page-size definitions, `pmd_off()`, `pte_offset_kernel()`, TLB flushing, and `pgtable-masks.h`. It is consumed by generic nohash pgtable operations and 8xx TLB miss handling.

## Risks And Edge Cases
The write-protect encoding is inverted relative to common PTE formats. Replication counts are page-size sensitive and easy to corrupt. 8M PMD-backed mappings alias PMD and PTE pointers, so pointer tests must stay exact.

## Test Signals
Exercise 4K, 16K, 512K, and 8M mappings; run mprotect, COW, hugepage, vmalloc, and TLB flush tests; validate PTE replication under page-table debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgalloc.h

## Purpose
This header provides 64-bit nohash page-table allocation and population helpers for P4D/PUD/PMD levels and declares vmemmap backing metadata.

## Important APIs, Types, And Functions
`struct vmemmap_backing` tracks physical and virtual backing chunks for the vmemmap. Helpers include `p4d_populate()`, `pud_alloc_one()`, `pud_free()`, `pud_populate()`, `pmd_populate_kernel()`, `pmd_populate()`, `pmd_alloc_one()`, `pmd_free()`, `__pmd_free_tlb()`, and `__pud_free_tlb()`.

## Control Flow
Generic MM allocates page-table pages from `PGT_CACHE()` slabs with `pgtable_gfp_flags()`, stores child table addresses with `*_set()`, and frees them either immediately or via TLB-gather callbacks.

## State And Persistence Behavior
Persistent state consists of allocated PUD/PMD pages and encoded parent entries. `vmemmap_list` records sparse vmemmap backing mappings that survive across memory hotplug operations until removed.

## Dependencies And Integration Points
It depends on slab, cpumask, percpu, `PGT_CACHE`, and nohash 64 pgtable setters. It integrates with vmemmap mapping creation/removal and generic page-table teardown.

## Risks And Edge Cases
The cache index must match table geometry or slab object sizes become wrong. Freeing through TLB gather must preserve the encoded shift. vmemmap backing needs hotplug-safe lifetime management.

## Test Signals
Run 64-bit Book3E/nohash builds with sparsemem/vmemmap, memory hotplug where available, mmap/unmap stress, and page-table allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable-4k.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable-4k.h

## Purpose
This header defines 4K-page 64-bit nohash page-table geometry, folded P4D behavior, and P4D accessors.

## Important APIs, Types, And Functions
It includes `asm-generic/pgtable-nop4d.h`, defines PTE/PMD/PUD/PGD index sizes, table sizes, `PTRS_PER_*`, `PMD_SHIFT`, `PUD_SHIFT`, `PGDIR_SHIFT`, masks, `p4d_none()`, `p4d_bad()`, `p4d_present()`, `p4d_pgtable()`, `p4d_clear()`, `p4d_pte()`, `pte_p4d()`, `p4d_page()`, `pud_ERROR()`, and `remap_4k_pfn()`.

## Control Flow
There is no independent runtime flow. Page-table walking and mapping code use the accessors to traverse from folded P4D to PUD and to remap individual 4K PFNs through generic `remap_pfn_range()`.

## State And Persistence Behavior
The header defines how P4D entries store child table addresses. It does not own state, but its geometry determines all 64-bit nohash page-table allocation sizes and address coverage.

## Dependencies And Integration Points
It is included by `nohash/64/pgtable.h` and depends on generic folded-level definitions and the page-table type definitions selected earlier.

## Risks And Edge Cases
Index-size changes alter the virtual address range and slab cache sizes. `p4d_bad()` treats zero as bad, consistent with folded semantics, but callers must not use it as a generic corruption detector for non-present entries.

## Test Signals
Build 64-bit nohash 4K page configs, run mmap/remap tests, inspect folded P4D walks, and validate page-table debug output for PUD/P4D transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable-4k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable.h

## Purpose
This header defines the 64-bit nohash Book3E page-table layout, kernel virtual address regions, PMD/PUD/P4D accessors, hugepage helpers, swap encoding, vmemmap mapping hooks, and exception patching hook.

## Important APIs, Types, And Functions
Key definitions include `PGTABLE_EADDR_SIZE`, `PGTABLE_RANGE`, `KERN_VIRT_START`, `VMALLOC_*`, `KERN_IO_*`, `IOREMAP_*`, `VMEMMAP_*`, `PTE_RPN_MASK`, `pmd_set()/clear()`, `pud_set()/clear()`, `pmd_page_vaddr()`, `pmd_page()`, `pud_pgtable()`, `pud_page()`, `pud_write()`, `p4d_set()`, `huge_ptep_set_wrprotect()`, swap conversion macros, `vmemmap_create_mapping()`, `vmemmap_remove_mapping()`, and `patch_exception()`.

## Control Flow
Generic MM uses the inline accessors for page-table walks and modifications. Hugepage write-protect calls `pte_update()` with the huge flag. Memory hotplug invokes vmemmap map/remove hooks. Exception setup can patch handler addresses through `patch_exception()`.

## State And Persistence Behavior
Persistent state lives in page tables, swap PTE encodings, vmemmap mappings, and patched exception vectors. The kernel virtual space is partitioned into vmalloc, vmemmap, IO, ioremap, and fixmap regions.

## Dependencies And Integration Points
It depends on 4K nohash geometry, barriers, `asm-const`, e500 PTE bits, and generic nohash pgtable code. It integrates with Book3E MMU setup, hugeTLB, sparse vmemmap, IO mapping, and low-level exception code.

## Risks And Edge Cases
Address-region constants are ABI-like for the architecture. `pmd_bad()`/`pud_bad()` require kernel virtual child table addresses. Swap encoding borrows bit 7 for exclusivity. Exception patching must target valid text symbols.

## Test Signals
Run 64-bit Book3E page-table debug, swap, hugepage mprotect/COW, vmalloc/ioremap/fixmap tests, sparsemem hotplug validation, and boot-time exception path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/64/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/hugetlb-e500.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/hugetlb-e500.h

## Purpose
This header provides e500/Book3E-specific hugeTLB hooks for checking supported hugepage sizes, encoding huge PTE page-size fields, and flushing hugeTLB entries.

## Important APIs, Types, And Functions
It declares `flush_hugetlb_page()`, defines `check_and_get_huge_psize()`, and overrides `arch_make_huge_pte()`. The helper rejects shifts that are not powers of four in Book3E encoding terms and maps valid shifts through `shift_to_mmu_psize()`.

## Control Flow
HugeTLB setup calls the check helper before accepting a page size, then `arch_make_huge_pte()` clears and rewrites `_PAGE_PSIZE_MSK` in the PTE. Runtime invalidation goes through `flush_hugetlb_page()`.

## State And Persistence Behavior
The only persistent state is the hugepage size encoded in the PTE. No global state is owned by this header.

## Dependencies And Integration Points
It depends on e500 PTE size bit definitions and `shift_to_mmu_psize()` from the MMU header. It integrates with generic hugeTLB PTE construction and nohash TLB flushing.

## Risks And Edge Cases
The `shift & 1` test enforces the Book3E page-size sequence and can reject otherwise plausible Linux hugepage sizes. Incorrect `_PAGE_PSIZE_SHIFT_OFFSET` math produces wrong hardware TLB sizes.

## Test Signals
Configure e500 hugeTLB sizes, allocate and fault hugepages, test mprotect/unmap on huge mappings, and validate TLB invalidation for each accepted page size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/hugetlb-e500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/kup-booke.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/kup-booke.h

## Purpose
This header implements BookE KUAP user-access protection primitives by controlling the PID SPR used for address-space matching.

## Important APIs, Types, And Functions
Under `CONFIG_PPC_KUAP`, it defines `__kuap_lock()`, `__kuap_save_and_lock()`, `kuap_user_restore()`, `__kuap_kernel_restore()`, optional `__kuap_get_and_assert_locked()`, `uaccess_begin_booke()`, `uaccess_end_booke()`, `allow_user_access()`, `prevent_user_access()`, `prevent_user_access_return()`, `restore_user_access()`, and `__bad_kuap_fault()`.

## Control Flow
Entry paths save the current PID and set PID to zero to block user access. User-copy windows temporarily restore `current->thread.pid` with an `isync`, then close by writing zero again. Return from interrupt supplies context synchronization for restore paths.

## State And Persistence Behavior
The protected state is the PID SPR and `regs->kuap`. Access windows persist only until `prevent_user_access()` or exception return. Debug mode verifies the locked state by reading the SPR.

## Dependencies And Integration Points
It depends on `asm/reg.h`, `asm/mmu.h`, current task thread PID, exception register state, and MMU feature patching. It integrates with uaccess, exception return, and KUAP fault detection.

## Risks And Edge Cases
Missing `isync` after PID changes can leave stale access permissions. Saving/restoring the wrong PID can either fault valid user copies or permit unintended kernel access to user mappings. Disabled KUAP paths must remain harmless.

## Test Signals
Run powerpc uaccess/KUAP selftests, fault injection around copy_to/from_user, interrupt during user-access windows, and debug KUAP assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/kup-booke.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu-e500.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu-e500.h

## Purpose
This header defines Freescale BookE/Book3E MMU constants, MAS/MMUCFG/TLBnCFG encodings, page-size support, and context data for nohash e500-style processors.

## Important APIs, Types, And Functions
It provides `BOOK3E_PAGESZ_*`, MAS0-MAS8 bit helpers, MMUCFG/MMUCSR0/TLBnCFG/TLBnPS masks, `TLBILX_T_*`, `MAS2_M_IF_NEEDED`, `tlbcam_index`, `mm_context_t`, `struct mmu_psize_def`, `shift_to_mmu_psize()`, `mmu_psize_to_shift()`, `mmu_virtual_psize`, `mmu_linear_psize`, `mmu_vmemmap_psize`, `struct tlb_core_data`, `linear_map_top`, `book3e_htw_mode`, `HUGETLB_NEED_PRELOAD`, and per-CPU `next_tlbcam_idx`.

## Control Flow
Low-level TLB management code uses these constants to program MAS registers, invalidate by TID/address/class, choose TLB entries, and decide page sizes. The inline page-size functions translate Linux shifts to MMU page-size indexes.

## State And Persistence Behavior
Persistent state includes per-mm ids, active flags, vDSO pointer, global and per-CPU TLB CAM indexes, software way-selection data, and 64-bit Book3E linear/vmemmap page-size choices.

## Dependencies And Integration Points
It depends on BookE CPU features, `asm/bug.h`, `asm/percpu.h`, and page-size Kconfig. It integrates with TLB miss handling, hugeTLB preload, SMP/coherent DMA policy, and 64-bit Book3E hardware tablewalk mode.

## Risks And Edge Cases
MAS bit definitions are hardware ABI. Coherency differs for SMP and e500mc DMA. Page-size support flags distinguish direct and indirect sizes. Per-core TLB locks must match e6500 handler expectations.

## Test Signals
Boot e500/e5500/e6500 variants, stress TLB invalidation and hugepage preloading, validate coherent DMA, inspect MAS programming through debug traces, and run SMP page-fault stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu-e500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu.h

## Purpose
This is the nohash MMU selector header. It includes the processor-family-specific MMU contract for 44x, e500/Book3E, or 8xx builds.

## Important APIs, Types, And Functions
The file has no direct APIs beyond conditional includes: `asm/nohash/32/mmu-44x.h` for `CONFIG_44x`, `asm/nohash/mmu-e500.h` for `CONFIG_PPC_E500`, and `asm/nohash/32/mmu-8xx.h` for `CONFIG_PPC_8xx`.

## Control Flow
There is no runtime control flow. Compile-time Kconfig selection determines which register definitions, context type, and page-size helpers are visible to the rest of the architecture.

## State And Persistence Behavior
It owns no state. The included header defines the MMU state model for the selected platform.

## Dependencies And Integration Points
It is included by architecture page/MMU code that wants a uniform nohash include path without knowing the selected embedded MMU family.

## Risks And Edge Cases
Misconfigured Kconfig combinations can leave no MMU family included or expose incompatible definitions. Adding a new nohash family requires updating this selector and downstream page-table selectors consistently.

## Test Signals
Cross-build 44x, e500, and 8xx configs and verify `asm/mmu.h` consumers see exactly one compatible nohash backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgalloc.h

## Purpose
This header provides common nohash page-table allocation and deferred-free helpers, then includes the 32-bit or 64-bit nohash allocation backend.

## Important APIs, Types, And Functions
It declares `tlb_remove_table()` and `tlb_flush_pgtable()`, defines `pgd_alloc()`, `pgd_free()`, `pgtable_free()`, `pgtable_free_tlb()`, `__tlb_remove_table()`, and `__pte_free_tlb()`. On 8xx, `pgd_alloc()` copies kernel PGD entries from `swapper_pg_dir` into new PGDs.

## Control Flow
PGD allocation pulls from `PGT_CACHE(PGD_INDEX_SIZE)`. Teardown encodes the page-table cache shift into the low bits of the pointer passed to `tlb_remove_table()`, then `__tlb_remove_table()` decodes and frees it later.

## State And Persistence Behavior
The header manages lifetime of allocated page-table pages and deferred TLB-gather free records. It does not maintain its own global state.

## Dependencies And Integration Points
It depends on generic MM, slab, `PGT_CACHE`, PTE fragment allocators, TLB gather, and architecture-specific 32/64 pgalloc headers.

## Risks And Edge Cases
The pointer low-bit shift encoding assumes alignment and `MAX_PGTABLE_INDEX_SIZE`. Forgetting `tlb_flush_pgtable()` before deferred PTE free can leave hardware walkers seeing freed tables. 8xx kernel PGD copying is required for kernel mappings.

## Test Signals
Run mmap/unmap stress, page-table debug, TLB gather teardown tests, 8xx process creation, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgtable.h

## Purpose
This header is the common nohash page-table operation layer shared by 32-bit and 64-bit backends. It defines kernel protections, generic PTE mutation, access-bit helpers, and permission predicates.

## Important APIs, Types, And Functions
It selects the 32-bit or 64-bit pgtable header, defines `_PAGE_CHG_MASK`, `PAGE_KERNEL*`, and helpers including `pte_update()`, `ptep_test_and_clear_young()`, `ptep_set_wrprotect()`, `ptep_get_and_clear()`, `pte_clear()`, `__ptep_set_access_flags()`, `pte_mkwrite_novma()`, `pte_mkdirty()`, `pte_mkyoung()`, `pte_wrprotect()`, `pte_mkexec()`, `pte_write()`, `pte_dirty()`, `pte_special()`, `pte_none()`, `pte_present()`, `pte_hw_valid()`, `pte_young()`, `pte_read()`, `pte_access_permitted()`, and `pte_user_accessible_page()`.

## Control Flow
Existing valid PTE modifications flow through `pte_update()`, which may update multiple entries for huge mappings, mark 44x executable I-cache flush state, and assert PTE locking for non-huge updates. Access-flag changes flush the corresponding TLB page.

## State And Persistence Behavior
PTE state persists in page tables. `icache_44x_need_flush` is set when executable user mappings change on 44x. Page-table check hooks observe clear operations.

## Dependencies And Integration Points
It depends on the selected backend, `linux/page_table_check.h`, nohash TLB flushing, and generic MM expectations for arch PTE operations.

## Risks And Edge Cases
Huge mapping updates advance PFNs across page-directory-sized chunks. Lock assertions differ for huge and normal mappings. Permission helpers must respect backend-specific `_PAGE_READ` semantics, especially Book3E BAP bits.

## Test Signals
Run mprotect, COW, page aging, reclaim, hugepage, 44x executable mapping, page-table-check, and TLB shootdown tests across nohash backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pte-e500.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pte-e500.h

## Purpose
This header defines Book3E/e500 PTE bits and helper predicates for PTE, PMD, and PUD leaf mappings.

## Important APIs, Types, And Functions
It defines `_PAGE_PRESENT`, BookE BAP read/write/execute bits, `_PAGE_PSIZE_MSK`, `_PAGE_TSIZE_4K`, dirty/accessed/cache/endian/guarded bits, `_PAGE_EXEC`, `_PAGE_READ`, `_PAGE_WRITE`, kernel/user protection masks, `_PAGE_SPECIAL`, `PTE_RPN_SHIFT`, `PTE_WIMGE_SHIFT`, `PTE_BAP_SHIFT`, `_PTE_NONE_MASK`, `_PAGE_BASE*`, `pte_mkexec()`, `pte_huge_size()`, `pmd_leaf()`, `pmd_leaf_size()`, and 64-bit `pud_leaf()`/`pud_leaf_size()`.

## Control Flow
Generic PTE helpers call these inline functions when constructing executable mappings or detecting huge PMD/PUD leaves. `pte_huge_size()` decodes the hardware page-size field into a byte size.

## State And Persistence Behavior
The PTE stores software presence plus hardware permission, page-size, cacheability, and RPN fields. On 32-bit, `_PTE_NONE_MASK` preserves upper PTE bits when testing none entries.

## Dependencies And Integration Points
It is selected for 32-bit 85xx and 64-bit nohash Book3E. It integrates with hugeTLB, nohash pgtable mutation, TLB refill, and `pgtable-masks.h`.

## Risks And Edge Cases
`pte_mkexec()` deliberately clears supervisor execute while setting user execute, matching nohash semantics. Leaf detection on 64-bit treats positive entry values as leaves. Incorrect page-size decode breaks hugepage TLB programming.

## Test Signals
Exercise executable user mappings, huge PMD/PUD mappings, mprotect write-protect paths, swap/none detection, and cache-inhibited IO mappings on e500/Book3E hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pte-e500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/tlbflush.h

## Purpose
This header declares and, for 8xx, implements nohash TLB flush operations for mm, page, range, kernel range, and page-size-specific invalidation.

## Important APIs, Types, And Functions
It defines `MMU_NO_CONTEXT`, declares `flush_tlb_range()`, `flush_tlb_kernel_range()`, `local_flush_tlb_mm()`, `local_flush_tlb_page()`, `local_flush_tlb_page_psize()`, `__local_flush_tlb_page()`, and SMP `flush_tlb_mm()`, `flush_tlb_page()`, `__flush_tlb_page()`. On UP, global names alias local helpers.

## Control Flow
On 8xx, `local_flush_tlb_mm()` checks the mm context id before issuing `tlbia`; page flushes issue `tlbie`; kernel-range flush chooses single-page `tlbie` or full `tlbia` based on range size. Other nohash CPUs use out-of-line implementations.

## State And Persistence Behavior
The affected state is hardware TLB contents. The header does not store state, but it depends on `mm->context.id` to avoid unnecessary 8xx full invalidation for inactive contexts.

## Dependencies And Integration Points
It integrates with generic MM invalidation, nohash PTE update helpers, SMP shootdown code, and architecture TLB assembly.

## Risks And Edge Cases
Missing `sync`/`isync` ordering can expose stale translations. The 8xx full-flush fallback is coarse. SMP builds must route global flushes through shootdown implementations rather than local aliases.

## Test Signals
Run mmap/unmap, mprotect, fork/exit, TLB shootdown, hugepage invalidation, and 8xx kernel-range flush tests under SMP and UP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nvram.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nvram.h

## Purpose
This header declares PowerPC NVRAM partition metadata and access APIs, including persistent OS error/oops log support and PowerMac XPRAM access.

## Important APIs, Types, And Functions
It defines `OOPS_HDR_VERSION`, `struct err_log_info`, `struct nvram_os_partition`, packed `struct oops_log_info`, `oops_log_partition`, pseries `rtas_log_partition`, error-log read/write/clear APIs, `pSeries_nvram_init()`, `mmio_nvram_init()`, partition scan/create/remove/find/size APIs, PowerMac `pmac_get_partition()`, `pmac_xpram_read()`, `pmac_xpram_write()`, `nvram_init_os_partition()`, `nvram_init_oops_partition()`, `nvram_read_partition()`, and `nvram_write_os_partition()`.

## Control Flow
Platform initialization scans partitions, creates or initializes OS partitions, and later error/oops paths read or write partition payloads with error type and sequence metadata.

## State And Persistence Behavior
NVRAM contents persist across reboot. `nvram_os_partition` records desired and actual partition sizes and offsets. Oops headers include version, report length, and timestamp to distinguish formats.

## Dependencies And Integration Points
It depends on Linux types, errno/list support, UAPI NVRAM definitions, pseries RTAS, MMIO NVRAM, and PowerMac partition/XPRAM code.

## Risks And Edge Cases
Persistent storage is small and partition sizes may be below requested sizes. Endianness and packed oops headers must match readers across boots. Removing partitions must honor exception lists.

## Test Signals
Validate pseries and MMIO NVRAM init, create/find/remove partitions, write/read oops and RTAS logs across reboot, and test PowerMac XPRAM byte access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nvram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ohare.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ohare.h

## Purpose
This header defines register offsets and feature-control bits for Apple's O'Hare I/O controller used in older PowerMac systems.

## Important APIs, Types, And Functions
It defines `OHARE_MBCR`, `OHARE_FCR`, feature bits such as `OH_SCC_RESET`, media-bay power/PCI/IDE/floppy enables, IDE reset/enables, SCC/MESH/floppy/VIA bits, `PBOOK_FEATURES`, and `STARMAX_FEATURES`.

## Control Flow
There are no functions. Platform feature code reads or writes O'Hare feature-control registers using these masks to enable, reset, or power hardware blocks.

## State And Persistence Behavior
State resides in O'Hare hardware registers. Writes persist until reset or later feature-management calls and directly affect device availability.

## Dependencies And Integration Points
It integrates with PowerMac feature management, media bay, IDE, serial SCC, MESH SCSI, floppy, and board-specific initialization.

## Risks And Edge Cases
Several bits are documented as guesses or experimentally derived. Incorrect masks can power off devices, hold reset lines, or break media-bay detection on specific machines.

## Test Signals
Boot affected PowerBook/Starmax/O'Hare systems, test IDE CD, media bay, serial, MESH SCSI, floppy, and suspend/resume feature restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ohare.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal-api.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal-api.h

## Purpose
This header is the Linux copy of the OPAL firmware ABI for PowerNV systems. It defines return codes, call tokens, event masks, message formats, PCI/EEH diagnostics, HMI data, PRD/OCC messages, I2C requests, dump/MPIPL records, and sensor/system policy enums.

## Important APIs, Types, And Functions
It exports OPAL status codes, console/event/interrupt/PCI/flash/sensor/security/MPIPL token numbers, quiesce and power-management flags, many enums for PCI freeze/reset/reinit/slot/LPC/message/system states, and ABI structs including `opal_msg`, `opal_ipmi_msg`, `OpalMemoryErrorData`, `OpalHMIEvent`, PHB error data variants, `oppanel_line_t`, PRD/OCC messages, `opal_sg_entry`, `opal_sg_list`, `opal_i2c_request`, and MPIPL structures.

## Control Flow
No C control flow is implemented. OPAL call wrappers and drivers use these constants to marshal firmware calls, interpret asynchronous messages, decode diagnostic payloads, and expose firmware state to kernel subsystems.

## State And Persistence Behavior
The file describes firmware-owned persistent or asynchronous state: event queues, error logs, PCI freeze state, sensors, flash/dump state, secure variables, and MPIPL/FADump metadata. Struct layouts and big-endian fields are ABI contracts.

## Dependencies And Integration Points
It is included by `opal.h`, PowerNV PCI, console, RTC, NVRAM, IPMI, I2C, dump, HMI, PRD/OCC, sensor, and power-control code.

## Risks And Edge Cases
Changing token values or structure layout breaks firmware ABI. Many fields are endian-specific. Diagnostic structs are versioned and hardware-generation-specific. Async calls require token lifecycle discipline.

## Test Signals
Build PowerNV, boot under OPAL firmware, exercise console, RTC, NVRAM, PCI config/EEH, sensors, flash/dump, IPMI/I2C, HMI handling, PRD/OCC paths, and MPIPL/FADump registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal-api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal.h

## Purpose
This header declares Linux OPAL firmware call wrappers and higher-level PowerNV OPAL subsystem initialization, async, notifier, console, sensor, dump, HMI, PCI, flash, secure variable, and MPIPL helpers.

## Important APIs, Types, And Functions
It defines `SG_ENTRIES_PER_NODE`, `OPAL_BUSY_DELAY_MS`, `opal_kobj`, `opal_node`, dozens of `opal_*` firmware call prototypes, initialization hooks such as `opal_elog_init()`, `opal_platform_dump_init()`, `opal_sys_param_init()`, `opal_msglog_init()`, `opal_async_comp_init()`, `opal_sensor_init()`, `opal_hmi_handler_init()`, console helpers, notifier registration, async token wait/release helpers, SG-list helpers, `opal_error_code()`, `opal_get_async_rc()`, and subsystem init helpers for powercap/PSR/sensor groups.

## Control Flow
Kernel subsystems call wrappers to enter OPAL, often looping on `OPAL_BUSY`/`OPAL_BUSY_EVENT` with the default delay or waiting for async completion messages. Init code discovers `/ibm,opal`, configures cores, and initializes service subsystems.

## State And Persistence Behavior
State spans firmware and kernel: OPAL device-tree node, sysfs kobject, async token ownership, pending logs, message queues, sensors, flash/dump state, secure variables, and firmware-maintained platform configuration.

## Dependencies And Integration Points
It depends on `opal-api.h`, notifier support, device tree, HVC console, PowerNV PCI/interrupts, RTC/NVRAM, sensors, HMI/MCE handlers, flash, sysfs, and dump infrastructure.

## Risks And Edge Cases
Async token leaks can stall firmware calls. Big-endian output buffers must be converted by callers. Busy-event loops must wake the OPAL poller. Machine-check/HMI handlers run in fragile contexts.

## Test Signals
Boot PowerNV, validate `/sys/firmware/opal`, HVC console, async completion, OPAL event polling, PCI/EEH, sensors, RTC/NVRAM, secure variables, dump/flash workflows, and HMI/MCE recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paca.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paca.h

## Purpose
This header defines the per-CPU PACA structure for 64-bit PowerPC, a low-level control block accessed through register `r13` for current task, exception, MMU, idle, accounting, KVM, and platform state.

## Important APIs, Types, And Functions
It declares `local_paca`, `get_paca()`, `get_slb_shadow()`, `struct paca_struct`, `copy_mm_to_paca()`, `paca_ptrs`, `initialise_paca()`, `setup_paca()`, `allocate_paca_ptrs()`, `allocate_paca()`, and `free_unused_pacas()`. The structure includes lppaca pointers, lock token/index, TOC/kernelbase/MSR, emergency stacks, per-CPU data offset, exception save areas, SLB and Book3E TLB data, current task, stack saves, soft IRQ mask state, idle state, accounting, KVM host state, speculation flush state, MCE/HMI state, stack canary, and MMIO write-barrier state.

## Control Flow
Early CPU setup allocates and installs PACA records. Exception entry/exit, scheduling, RTAS, idle, KVM, and low-level locking paths read and update PACA fields directly, often before normal per-CPU access is available.

## State And Persistence Behavior
PACA is long-lived per logical CPU kernel state. Some fields are read-mostly after boot; many are hot exception-path mutable state. Alignment and cacheline placement are part of the performance and correctness contract.

## Dependencies And Integration Points
It depends on PPC64, exception layout headers, MMU/page definitions, accounting, HMI/MCE, KVM, lppaca, and generic mmiowb types. It integrates with almost every low-level 64-bit PowerPC path.

## Risks And Edge Cases
Field layout is assembly-sensitive. `lock_token` and `paca_index` must stay paired. Preemption around `local_paca` access is debug-checked. Cacheline sharing can hurt interrupt and lock paths.

## Test Signals
Boot SMP PPC64, CPU hotplug, KVM, RTAS, idle, NMI/MCE/HMI handling, lock primitives, stack protector, and debug-preempt PACA access checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page.h

## Purpose
This central PowerPC page header defines page/hugepage policy, kernel physical/virtual address relationships, `__va()`/`__pa()` translations, PFN helpers, and data/stack VMA defaults.

## Important APIs, Types, And Functions
It includes VDSO page definitions, defines `HPAGE_SHIFT/SIZE/MASK`, `HUGETLB_PAGE_ORDER`, `HUGE_MAX_HSTATE`, `KERNELBASE`, `PAGE_OFFSET`, `LOAD_OFFSET`, `PHYSICAL_START`, `MEMORY_START`, optional `memstart_addr`, `kernstart_addr`, `virt_phys_offset`, `VIRT_PHYS_OFFSET`, `ARCH_PFN_OFFSET`, `__va()`, `__pa()`, `virt_to_pfn()`, `pfn_to_kaddr()`, `virt_to_page()`, `virt_addr_valid()`, VMA data defaults, and architecture `is_kernel_addr()` policy.

## Control Flow
The important runtime logic is inline address translation. BookE relocatable 32-bit kernels use `virt_phys_offset`; PPC64 uses bitwise mappings to avoid compiler codegen issues; other 32-bit builds use `PAGE_OFFSET - MEMORY_START`.

## State And Persistence Behavior
Non-static kernels expose runtime physical and virtual base variables. The translation macros define persistent assumptions for the linear map, kdump, relocation, and memory model.

## Dependencies And Integration Points
It depends on Kconfig address constants, VDSO page definitions, memory model, hugeTLB, BookE relocation, and includes `page_32.h` or `page_64.h`.

## Risks And Edge Cases
Confusing `KERNELBASE` with `PAGE_OFFSET` breaks kdump and relocatable kernels. Debug virtual checks can warn on invalid PPC64 translation. 32-bit ELF default executable data is intentional ABI behavior.

## Test Signals
Boot static, relocatable, kdump, BookE, and PPC64 configs; run virt/phys translation selftests, hugeTLB tests, `virt_addr_valid()` checks, and memory hotplug where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_32.h

## Purpose
This header supplies 32-bit PowerPC page-type details, PTE size calculation, and cacheline-based page clear/copy primitives.

## Important APIs, Types, And Functions
It validates `CONFIG_PHYSICAL_START` alignment, defines `VMA_DATA_DEFAULT_FLAGS`, `PTE_SHIFT`, `pte_basic_t`, `clear_page()`, `copy_page()`, `PGD_T_LOG2`, and `PTE_T_LOG2`. `pte_basic_t` is 64-bit when `CONFIG_PTE_64BIT` is enabled.

## Control Flow
`clear_page()` loops over cache lines and issues `dcbz` for each line, warning if the address is not L1-cacheline aligned. `copy_page()` is implemented out of line.

## State And Persistence Behavior
No independent persistent state. The PTE geometry determines page-table storage size, including quarter-page PTE tables for 256K pages and 8xx 16K-page mode.

## Dependencies And Integration Points
It depends on `asm/cache.h`, `asm/bug.h`, and generic getorder. It integrates with MM page allocation, zeroing, copying, and pgtable type definitions.

## Risks And Edge Cases
`dcbz` is valid only for cacheable memory. Miscomputed `PTE_SHIFT` corrupts page-table layout. Physical start alignment is enforced at compile time.

## Test Signals
Cross-build 32-bit page-size variants, run page allocation zeroing/copying tests, boot with `CONFIG_PTE_64BIT`, and validate page-table sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_64.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_64.h

## Purpose
This header supplies 64-bit PowerPC hardware page constants, segment-id helpers, page clear/copy primitives, page-table-size state, and VMA default flags.

## Important APIs, Types, And Functions
It defines `HW_PAGE_SHIFT/SIZE/MASK`, `PAGE_FACTOR`, segment masks and `GET_ESID()` helpers for 256M and 1T segments, `pte_basic_t`, `clear_page()`, `copy_page()`, `ppc64_pft_size`, and 32/64-bit task-aware data and stack default VMA flags.

## Control Flow
`clear_page()` computes cache block strides from `ppc64_caches.l1d` and unrolls eight `dcbz` operations per loop iteration in inline assembly. VMA flag macros branch on `is_32bit_task()`.

## State And Persistence Behavior
`ppc64_pft_size` is exported page-hash-table size state. Page clearing mutates the target page only; VMA defaults persist in new mappings as policy.

## Dependencies And Integration Points
It depends on `asm-const`, cache metadata, task bitness helpers, and generic getorder. It integrates with allocator zeroing, copy-on-write, ELF stack/data permissions, and segment management.

## Risks And Edge Cases
Firmware and IOMMU interfaces still use 4K hardware page numbering even when Linux uses larger pages. Cache metadata must be initialized before `clear_page()` use. ABI defaults differ for 32-bit and 64-bit tasks.

## Test Signals
Boot 4K and 64K PPC64 page configs, run page zero/copy tests, 32-bit compat task stack/data permission checks, and segment-id mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/papr-sysparm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/papr-sysparm.h

## Purpose
This header defines the in-kernel PAPR system-parameter token type and RTAS buffer layout for `ibm,get-system-parameter` and `ibm,set-system-parameter`.

## Important APIs, Types, And Functions
It defines `papr_sysparm_t`, `mk_papr_sysparm()`, named parameters such as shared processor LPAR attributes, processor module info, cooperative memory overcommit attributes, TLB block invalidate attributes, LPAR name, and HVPIPE enable. `struct papr_sysparm_buf` contains a big-endian length and value buffer. It declares allocation/free plus `papr_sysparm_set()` and `papr_sysparm_get()`.

## Control Flow
Callers allocate a buffer, fill or receive the length-prefixed payload, and call RTAS-backed get/set helpers with a typed token.

## State And Persistence Behavior
The buffer is transient kernel memory. Actual parameter state is owned by firmware/hypervisor and may persist according to PAPR semantics.

## Dependencies And Integration Points
It depends on UAPI PAPR sysparm constants and RTAS pseries infrastructure. Consumers include pseries feature discovery and configuration code.

## Risks And Edge Cases
The RTAS work area layout differs from the user/kernel IO block. Length is big-endian and bounded by `PAPR_SYSPARM_MAX_OUTPUT`. Tokens must match PAPR-defined numbers.

## Test Signals
On pseries, query LPAR name and attributes, set supported writable parameters if available, test oversized buffers, and validate UAPI IO translation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/papr-sysparm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paravirt.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paravirt.h

## Purpose
This header provides PowerPC paravirtualization helpers for shared-processor detection, steal-time accounting, virtual CPU yield/prod operations, idle/preempt state checks, and paravirtual spin unlock selection.

## Important APIs, Types, And Functions
It declares the `shared_processor` static key and defines `is_shared_processor()`, `paravirt_steal_clock()`, `yield_count_of()`, `yield_to_preempted()`, `prod_cpu()`, `yield_to_any()`, `is_vcpu_idle()`, `vcpu_is_dispatched()`, `vcpu_is_preempted()`, and `pv_is_native_spin_unlock()`, with SPLPAR, KVM guest, and fallback variants.

## Control Flow
On shared SPLPAR systems, helpers read lppaca dispatch/yield fields and issue hypervisor calls to yield to or prod target CPUs. Fallback paths either return native defaults or reference bad-call stubs to catch impossible calls.

## State And Persistence Behavior
State is hypervisor-owned dispatch/yield accounting plus per-CPU lppaca/PACA fields. Static keys determine whether shared-processor fast paths are active.

## Dependencies And Integration Points
It depends on jump labels, SMP, PPC64 PACA/lppaca/hvcall, KVM guest detection, and cputhreads. It integrates with scheduler accounting and spinlock slow paths.

## Risks And Edge Cases
Calling yield/prod helpers on unsupported configs should fail at build/link time via bad stubs. CPU numbering must map to the correct hardware thread/lppaca. Steal-time reads need stable dispatch data.

## Test Signals
Run pseries SPLPAR under shared and dedicated modes, verify steal accounting, lock contention benchmarks, KVM guest behavior, and static-key transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/paravirt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/parport.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/parport.h

## Purpose
This small header adapts generic parallel-port probing to PowerPC Open Firmware interrupt mapping.

## Important APIs, Types, And Functions
It includes `linux/of_irq.h` under `__KERNEL__`; the header otherwise acts as the architecture-specific parport include point expected by generic parport code.

## Control Flow
No runtime functions are defined here. Consumer code can use OF IRQ helpers made visible through this architecture header while probing parallel ports.

## State And Persistence Behavior
No state is stored. Device-tree interrupt mappings persist in OF data structures managed elsewhere.

## Dependencies And Integration Points
It integrates with generic parport drivers and PowerPC device-tree interrupt parsing.

## Risks And Edge Cases
The header is intentionally minimal. Removing the include can break platforms whose parport probing expects OF IRQ declarations via the arch header.

## Test Signals
Build PowerPC configs with parallel-port support, probe device-tree-described parport devices, and validate IRQ assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/parport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pasemi_dma.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pasemi_dma.h

## Purpose
This header defines the PA Semi DMA engine register and descriptor bitfield interface used by network, copy, and platform DMA code.

## Important APIs, Types, And Functions
It defines `struct pasdma_status`, channel/interface enum values, capability masks, common TX/RX command/status bits, RX interface registers, TX/RX channel register offsets, descriptor ring base/size/increment fields, status/control fields, descriptor flags, and bitfield constructor macros for packet length, interface, channel, checksum, LRO, and buffer metadata.

## Control Flow
Drivers program capability-derived channel counts, configure rings and interfaces by writing the offset macros, enable channels, then poll or interrupt on command/status and descriptor completion bits.

## State And Persistence Behavior
State lives in memory-mapped DMA registers and descriptor rings. Ring base, size, counters, active/stop bits, drop counters, and descriptor ownership persist until driver reset or device reset.

## Dependencies And Integration Points
It integrates with PA Semi Ethernet and DMA drivers, PCI/platform device setup, DMA mapping, and interrupt handling.

## Risks And Edge Cases
This is raw hardware ABI. Incorrect bit shifts can corrupt DMA rings or packet metadata. Ring base alignment and size encodings are constrained. Register status bits may be clear-on-write or hardware-updated.

## Test Signals
Run PA Semi network transmit/receive, checksum offload, interrupt moderation, ring wrap, stop/start, drop counter, and DMA mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pasemi_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci-bridge.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci-bridge.h

## Purpose
This header defines PowerPC PCI host bridge state, controller operation hooks, indirect config access helpers, device-tree PCI metadata, and hotplug/resource mapping entry points.

## Important APIs, Types, And Functions
It defines `struct pci_controller_ops`, `struct pci_controller`, indirect config flags, early config read/write helpers, `early_find_capability()`, `setup_indirect_pci()`, indirect read/write helpers, `pci_bus_to_host()`, PowerMac OF lookup, 64-bit `struct pci_dn`, `PCI_DN()`, pci_dn lookup/add/remove APIs, SR-IOV helpers, `pdn_to_eeh_dev()`, bus-node lookup, hotplug add/remove, IO-space map/unmap, PHB node assignment, controller lookup, OF range processing, and controller allocation/free.

## Control Flow
Platform PCI setup allocates a controller, processes OF ranges, installs config ops, scans buses, and uses controller hooks for DMA, probing, MSI, bridge setup, device enable/disable, and shutdown. Hotplug paths add/remove devices and pci_dn records.

## State And Persistence Behavior
`pci_controller` persists per PHB and records bus ranges, IO/memory windows, DMA window, device-tree node, config registers, resources, IOMMU, IRQ domain, and private data. `pci_dn` persists per OF PCI node and tracks PE/IOMMU/SR-IOV/EEH metadata.

## Dependencies And Integration Points
It depends on PCI core, resources, NUMA, IOMMU, device tree, IRQ domains, MSI, EEH, and SR-IOV. It is central to pseries, powernv, embedded, and PowerMac PCI support.

## Risks And Edge Cases
Indirect config quirks avoid real hardware hangs. Dynamic PHB removal must not leave stale pci_dn or IOMMU data. SR-IOV PE/M64 metadata is platform-sensitive. Resource window alignment affects reassignment.

## Test Signals
Run PCI enumeration, early config access, MSI, EEH, SR-IOV, PHB hotplug, IO/memory mmap, OF bus map creation, and dynamic PHB add/remove tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci-bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci.h

## Purpose
This header provides the PowerPC architecture-facing PCI API for probing policy, legacy IO, DMA ops, OF scanning, resource setup, and PCI mmap support.

## Important APIs, Types, And Functions
It defines `PCI_PROBE_NONE/NORMAL/DEVTREE`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `IOBASE_*`, `pcibios_assign_all_busses()`, `pci_get_legacy_ide_irq()`, `set_pci_dma_ops()`, `PCI_DISABLE_MWI` on PPC64, `pci_domain_nr()`, `pci_proc_domain()`, mmap capability macros, legacy read/write/mmap/attribute helpers, bus/resource survey helpers, dynamic PHB init/remove, OF PCI device/bus scan/rescan helpers, `pci_parse_of_flags()`, `pci_phys_mem_access_prot()`, IO-space offset/setup, and `pcibios_scan_phb()`.

## Control Flow
PCI core calls these hooks during bus discovery, resource assignment, device enabling, legacy IO access, mmap setup, and dynamic host bridge changes. Legacy IDE IRQ falls back to 14/15 unless `ppc_md` overrides.

## State And Persistence Behavior
The header owns no state. It exposes persistent PCI domain, PHB, DMA ops, and OF-derived device state owned by PCI architecture code.

## Dependencies And Integration Points
It depends on PCI bridge definitions, machdep hooks, DMA mapping ops, OF scanning, and generic PCI core.

## Risks And Edge Cases
PPC64 disables MWI/cacheline touching because firmware and hardware semantics differ. Reassign-all-bus policy is architecture flagged. Legacy mmap must preserve caching/protection rules.

## Test Signals
Run PCI probe from OF and normal scanning, domain display, legacy IO syscalls, PCI mmap, DMA ops selection, dynamic PHB add/remove, and legacy IDE IRQ routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/percpu.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/percpu.h

## Purpose
This header defines PowerPC percpu access plumbing, especially the PPC64 fast path using PACA `data_offset`, and first-chunk paged detection.

## Important APIs, Types, And Functions
On PPC64 SMP it defines `__my_cpu_offset` as `local_paca->data_offset`. With `CONFIG_NEED_PER_CPU_PAGE_FIRST_CHUNK` and SMP it declares `__percpu_first_chunk_is_paged` and defines `percpu_first_chunk_is_paged` through a static key; otherwise it is false. It includes generic percpu support and PACA as needed.

## Control Flow
Per-CPU access code reads the current CPU offset from PACA. Static-key logic lets callers branch cheaply on whether the first percpu chunk is paged.

## State And Persistence Behavior
Per-CPU offsets are persistent per CPU in PACA. The first-chunk static key reflects allocator setup state after boot.

## Dependencies And Integration Points
It depends on PPC64 PACA, generic percpu, SMP, and jump labels. It integrates with all per-CPU variable access and percpu allocator setup.

## Risks And Edge Cases
`local_paca` must be valid before percpu fast paths execute. Incorrect `data_offset` corrupts per-CPU storage. Static-key state must match the actual first-chunk mapping.

## Test Signals
Boot PPC64 SMP and UP, run CPU hotplug, percpu allocator tests, and debug per-CPU access checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event.h

## Purpose
This is the top-level PowerPC perf-event architecture header. It selects server or Freescale embedded PMU definitions and supplies generic register-capture helpers for perf.

## Important APIs, Types, And Functions
It conditionally includes `perf_event_server.h` for `CONFIG_PPC_PERF_CTRS` or provides stub `is_sier_available()` and `get_pmcs_ext_regs()`. It includes `perf_event_fsl_emb.h` for embedded PMU support. Under `CONFIG_PERF_EVENTS`, it defines `perf_arch_bpf_user_pt_regs()`, `perf_arch_fetch_caller_regs()`, declares `is_sier_available()`, `get_pmcs_ext_regs()`, and `PERF_REG_EXTENDED_MASK`.

## Control Flow
Perf sampling uses the fetch macro to populate caller registers with instruction pointer, stack pointer, MSR, and current task. PMU-specific code comes from the selected backend.

## State And Persistence Behavior
The header owns no state. `PERF_REG_EXTENDED_MASK` and backend PMU registration state are defined elsewhere.

## Dependencies And Integration Points
It integrates with Linux perf, BPF perf register access, ptrace register layout, and server/embedded PMU drivers.

## Risks And Edge Cases
Stub SIER functions must match unavailable hardware behavior. Caller register capture must produce valid pt_regs enough for perf unwinding. Backend selection depends on mutually correct Kconfig.

## Test Signals
Run `perf stat`, `perf record`, BPF perf programs, extended-register sampling on supported POWER CPUs, and embedded PMU builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_fsl_emb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_fsl_emb.h

## Purpose
This header describes Freescale embedded PMU capabilities and registration for PowerPC perf events.

## Important APIs, Types, And Functions
It defines `MAX_HWEVENTS`, event attribute bits `FSL_EMB_EVENT_VALID` and `FSL_EMB_EVENT_RESTRICTED`, threshold masks `FSL_EMB_EVENT_THRESHMUL` and `FSL_EMB_EVENT_THRESH`, `struct fsl_emb_pmu`, and `register_fsl_emb_pmu()`. The PMU struct carries name, counter count, supported event table, cache event map, and callbacks for constraints, event config, event disabling, interrupt handling, and overflow behavior.

## Control Flow
Platform PMU code fills `struct fsl_emb_pmu` and registers it. Perf core calls the callbacks to validate events, program counters, handle interrupts, and disable counters.

## State And Persistence Behavior
The PMU instance persists after registration and describes hardware event state. Per-event counter state is owned by perf core and PMU implementation.

## Dependencies And Integration Points
It depends on Linux types and hardware interrupt helpers. It integrates with Freescale embedded PMU drivers and generic perf.

## Risks And Edge Cases
Event validity/restriction bits must match hardware tables. Counter count is small. Threshold fields in event IDs must be decoded consistently by implementation callbacks.

## Test Signals
Run perf on FSL embedded CPUs, validate event rejection, restricted events, thresholds, overflow interrupts, and cache event aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_fsl_emb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_server.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_server.h

## Purpose
This header defines classic/server POWER PMU registration data, MMCR programming state, constraint semantics, BHRB support, and sysfs event attribute helpers.

## Important APIs, Types, And Functions
It defines `MAX_HWEVENTS`, `MAX_EVENT_ALTERNATIVES`, `MAX_LIMITED_HWCOUNTERS`, `struct mmcr_regs`, `struct power_pmu`, `PPMU_*` feature flags, alternative flags, `register_power_pmu()`, perf arch helpers, `read_bhrb()`, `power_events_sysfs_show()`, and macros `EVENT_ATTR`, `GENERIC_EVENT_ATTR`, `CACHE_EVENT_ATTR`, and `POWER_EVENT_ATTR`.

## Control Flow
PMU drivers register a `power_pmu`. Perf scheduling asks callbacks to compute MMCR registers, constraints, alternatives, memory data source/weight, BHRB filters, limited counter rules, and reserved event validation.

## State And Persistence Behavior
The registered PMU descriptor persists for the CPU family. `mmcr_regs` instances are transient computed programming state for event groups. Sysfs attribute groups expose persistent event aliases.

## Dependencies And Integration Points
It depends on perf UAPI, hardware IRQ helpers, device attributes, and POWER PMU implementations. It integrates with perf event scheduling, sampling, BHRB, memory profiling, and sysfs event discovery.

## Risks And Edge Cases
Constraint encoding is dense and easy to get wrong; limited PMCs and NAND/select/add fields determine whether event groups are schedulable. POWER10 and architecture-version flags alter extended register availability.

## Test Signals
Run perf event group scheduling, generic/cache/raw events, BHRB branch sampling, memory data source sampling, extended register sampling, sysfs alias inspection, and limited counter conflict tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/perf_event_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgalloc.h

## Purpose
This top-level page-table allocation header supplies shared PTE page allocation/free helpers, cache indexes, and selects Book3S or nohash allocation backends.

## Important APIs, Types, And Functions
It defines `pgtable_t`, `pte_alloc_one_kernel()`, `pte_alloc_one()`, `pte_free_kernel()`, `pte_free()`, optional `pte_free_defer()`, `MAX_PGTABLE_INDEX_SIZE`, `pgtable_cache[]`, `PGT_CACHE(shift)`, then includes either `asm/book3s/pgalloc.h` or `asm/nohash/pgalloc.h`.

## Control Flow
PTE pages are allocated through PTE fragment helpers. Free paths release fragments immediately or through deferred freeing when configured. Higher-level page-table frees are delegated to the selected backend.

## State And Persistence Behavior
Allocated PTE fragments become persistent page-table state until unmapped and freed. `pgtable_cache[]` stores slab caches for different table sizes.

## Dependencies And Integration Points
It depends on generic MM, PTE fragment allocation, and PowerPC MMU family selection. It integrates with all generic page-table allocation paths.

## Risks And Edge Cases
Backend selection must match Book3S/nohash page-table layout. Deferred PTE free is required for configurations that cannot immediately release tables. Cache index bounds are enforced by backends.

## Test Signals
Run page-table allocation stress, fork/exit, mmap/unmap, memory pressure, deferred-free configurations, and Book3S/nohash cross-builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-be-types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-be-types.h

## Purpose
This header defines big-endian PowerPC page-table C types and raw/value conversion helpers for PTE, PMD, PUD, PGD, pgprot, and real PTE records.

## Important APIs, Types, And Functions
It defines big-endian `pte_t`, `pmd_t`, `pud_t`, `pgd_t`, `pgprot_t`, `real_pte_t`, constructors `__pte()`, `__pmd()`, `__pud()`, `__pgd()`, raw constructors, value/raw accessors, and atomic compare-exchange helpers `pte_xchg()` and `pmd_xchg()`.

## Control Flow
Inline accessors convert between CPU-endian unsigned long values and stored big-endian table entries. Exchange helpers use `__cmpxchg_u64()` on raw table storage.

## State And Persistence Behavior
Persistent page-table state is stored in big-endian fields. For 64K hash configurations, `real_pte_t` carries an additional hash index.

## Dependencies And Integration Points
It depends on `asm/cmpxchg.h` and endian conversion helpers. It integrates with page-table walkers and atomic PTE/PMD update paths on big-endian builds.

## Risks And Edge Cases
Mixing raw and converted values can corrupt page tables. Atomic exchange compares raw big-endian storage. Type layout must match assembly and MMU expectations.

## Test Signals
Build big-endian PPC64/Book3S configs, run page-table atomic update stress, huge/64K page tests, and endian-sensitive swap/mmap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-be-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-masks.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-masks.h

## Purpose
This header supplies common Linux protection-mask combinations for PowerPC page tables when the platform-specific PTE header has not overridden them.

## Important APIs, Types, And Functions
It conditionally defines `_PAGE_NA`, `_PAGE_NAX`, `_PAGE_RO`, `_PAGE_ROX`, `_PAGE_RW`, `_PAGE_RWX`, kernel permission masks `_PAGE_KERNEL_RO/ROX/RW/RWX`, and user protection macros `PAGE_NONE`, `PAGE_EXECONLY_X`, `PAGE_SHARED`, `PAGE_SHARED_X`, `PAGE_COPY`, `PAGE_COPY_X`, `PAGE_READONLY`, and `PAGE_READONLY_X`.

## Control Flow
No runtime flow is present. The macros are consumed at compile time by pgprot construction and generic mmap permission tables.

## State And Persistence Behavior
The resulting `pgprot_t` values persist in VMAs and PTEs created from those protections.

## Dependencies And Integration Points
It depends on platform `_PAGE_BASE`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_EXEC`, and `_PAGE_DIRTY` definitions. It is included by PTE layout headers.

## Risks And Edge Cases
Some backends override permission semantics, so these defaults must remain guarded. Incorrect combinations can grant execute/write permissions or break COW protections.

## Test Signals
Run mmap protection matrix tests, mprotect, COW, execute-only/read-only mapping checks, and backend cross-builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-types.h

## Purpose
This header defines native-endian PowerPC page-table C types and constructors for non-big-endian-specialized builds, with strict type checking where needed.

## Important APIs, Types, And Functions
It controls `STRICT_MM_TYPECHECKS`, defines `pte_t` including the special 8xx 16K four-cell form, `__pte()`, `pte_val()`, 64-bit `pmd_t`/`pud_t` and accessors, `pgd_t` including 85xx 64-bit PGDs, `__pgd()`, `pgprot_t`, `real_pte_t`, and Book3S64 `pte_xchg()`.

## Control Flow
Inline constructors/accessors wrap or unwrap primitive values. `pte_xchg()` performs atomic PTE compare-exchange on Book3S64.

## State And Persistence Behavior
The type definitions determine the in-memory layout of page tables. 8xx 16K PTEs persist four replicated basic values inside one logical `pte_t`.

## Dependencies And Integration Points
It depends on `pte_basic_t`, Kconfig MMU/page options, optional `asm/cmpxchg.h`, and is consumed by all page-table code.

## Risks And Edge Cases
Strict type checking differs by 32/64-bit and sparse checker builds. 85xx PGD width and 8xx multi-cell PTEs are special cases that generic code must respect.

## Test Signals
Cross-build sparse/normal, PPC32/PPC64, 8xx 16K, 85xx, and Book3S64 configs; run page-table access and atomic update tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable.h

## Purpose
This top-level PowerPC pgtable header selects MMU-family page-table definitions and exposes generic architecture hooks for page protections, PTE access, and memory-management integration.

## Important APIs, Types, And Functions
It includes page and type headers, selects Book3S or nohash pgtable backends, and supplies common wrappers/macros used by generic MM such as page protection transforms, PTE/PFN conversions, pgd/p4d/pud/pmd walking helpers, cacheability helpers, and architecture feature declarations. The exact exported surface depends heavily on Book3S vs nohash and 32-bit vs 64-bit configuration.

## Control Flow
Most behavior is inline and configuration-selected. Generic MM code enters this header's helpers during page faults, mmap/mprotect, swap, unmap, IO remapping, and TLB/cache maintenance.

## State And Persistence Behavior
It owns little direct state but defines how VMAs and page tables encode persistent protections, PFNs, swap entries, and hardware-specific status bits.

## Dependencies And Integration Points
It integrates the PowerPC MMU family headers with Linux generic MM. It depends on page geometry, pgtable type definitions, cache/TLB helpers, and backend-specific Book3S/nohash files.

## Risks And Edge Cases
Because it is a selector and aggregation point, Kconfig combinations can expose conflicting helpers. Backend-specific permission, hugepage, and endian semantics must remain isolated behind common generic-MM names.

## Test Signals
Cross-build representative Book3S hash/radix and nohash configs, run MM selftests, page-table debug, swap, hugeTLB, mprotect, IO remap, and cache/TLB coherency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pkeys.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pkeys.h

## Purpose
This header declares PowerPC memory protection key support, including key allocation policy, execute-only pkey handling, AMR/IAMR/UAMOR helpers, and VMA permission integration.

## Important APIs, Types, And Functions
It defines pkey limits and special key values when supported, helpers for checking pkey availability, converting key/protection into PTE bits, initializing thread/user AMR/IAMR state, reserving/freeing pkeys, assigning execute-only pkeys, and arch hooks used by `mprotect_pkey()` and fault handling. Unsupported configurations provide no-op or default stubs.

## Control Flow
On supported CPUs, process setup initializes pkey registers and allocation bitmaps. VMA creation and mprotect paths assign pkeys and encode access rights. Fault paths and context switch code restore AMR/IAMR/UAMOR-derived state.

## State And Persistence Behavior
Pkey state persists per mm/thread in allocation maps and access-control registers. Execute-only mappings may reserve a dedicated key until released.

## Dependencies And Integration Points
It integrates with generic Linux pkeys, PowerPC radix/Book3S support, thread context, page-table protection bits, and signal/fault paths.

## Risks And Edge Cases
Unsupported configurations must preserve generic API expectations. Register state must be context-switched correctly. Execute-only pkey reuse can accidentally widen access if allocation state is mishandled.

## Test Signals
Run Linux pkeys selftests on supported POWER systems, mprotect_pkey permutations, fork/exec/context-switch tests, signal delivery, and unsupported-config build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pkeys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpar_wrappers.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpar_wrappers.h

## Purpose
This header provides pseries logical-partition hypervisor wrapper helpers around low-level `plpar_hcall*` interfaces for TCE/IOMMU, virtual processor management, dispatch accounting, memory, interrupt, and platform services.

## Important APIs, Types, And Functions
It defines many static inline wrappers for H_PUT_TCE, H_STUFF_TCE, H_PUT_TCE_INDIRECT, H_GET_TCE, H_REGISTER_VPA and related VPA/SLB/shadow buffer registration, H_CONFER, H_PROD, H_CEDE, H_JOIN, H_GET_TERM_CHAR/H_PUT_TERM_CHAR, H_RANDOM, H_HOME_NODE_ASSOCIATIVITY, H_BEST_ENERGY, H_TLB_INVALIDATE, and related pseries hypercalls, translating arguments and return registers into C helpers.

## Control Flow
Callers invoke wrappers, which marshal arguments to `plpar_hcall_norets()` or return-value variants. Some helpers loop or choose flags for bulk TCE operations and virtual CPU state registration.

## State And Persistence Behavior
Persistent state is hypervisor-owned: TCE tables, VPA registration, dispatch/yield state, CPU cede/prod state, terminal buffers, and platform attributes. Wrappers themselves store no state.

## Dependencies And Integration Points
It depends on pseries hypercall numbers and calling conventions from `hvcall.h`, endian/CPU utilities, and partition firmware. It integrates with IOMMU, virtual console, scheduler idle/yield, CPU hotplug, and pseries platform setup.

## Risks And Edge Cases
Hypercall return codes must be propagated exactly. TCE operations must match table index/page size semantics. VPA registration addresses must be real addresses and aligned. Some calls are only valid under specific firmware capabilities.

## Test Signals
Boot pseries LPARs, exercise IOMMU DMA, virtual console, CPU cede/prod/yield, VPA registration during CPU hotplug, random-number calls, and TLB block invalidate capability paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpar_wrappers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpks.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpks.h

## Purpose
This header declares the pseries Platform KeyStore (PLPKS) API for persistent secure variables, policy flags, signed updates, wrapping features, and device-tree/sysfs integration.

## Important APIs, Types, And Functions
When `CONFIG_PSERIES_PLPKS` is enabled it defines policy flags such as secure-boot audit/enforce, password-required, world-readable, immutable, transient, signed-update, wrapping-key, and hypervisor-provisioned; signature algorithms; owner/label limits; `struct plpks_var`, name/list structs; read/write/remove/signed-update APIs; availability and capability getters; early device-tree/FDT/sysfs hooks; and wrapping key/object functions. Disabled builds provide minimal stubs.

## Control Flow
Callers check availability, query capabilities and limits, then read/write/remove variables or perform signed/wrapped updates through pseries firmware-backed implementations.

## State And Persistence Behavior
Most variables persist in the platform keystore across reboot unless `PLPKS_TRANSIENT` is set. Capability values describe hypervisor-owned keystore state, used/total space, password length, and supported policies.

## Dependencies And Integration Points
It depends on pseries firmware, kobjects, device-tree/FDT population, secure boot, and key/wrapping consumers.

## Risks And Edge Cases
Maximum name/data/label sizes are strict. Policy flags are security-sensitive and may make objects immutable or inaccessible. Disabled stubs intentionally `BUILD_BUG()` for unsupported capability use.

## Test Signals
On PLPKS-capable pseries, test capability queries, variable write/read/remove, signed update, immutable/transient/world-readable policies, wrapping key generation/wrap/unwrap, reboot persistence, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_feature.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_feature.h

## Purpose
This header defines the legacy PowerMac feature-control API, model/type flags, feature call selectors, MacIO chip metadata, and helper macros for manipulating MacIO feature-control registers.

## Important APIs, Types, And Functions
It enumerates many `PMAC_TYPE_*` machine IDs and motherboard flags, defines `pmac_call_feature()`, feature selectors for SCC, modem, SWIM3, MESH, IDE, BMAC/GMAC, sound, Airport, CPU reset, USB, FireWire, sleep, motherboard info, GPIO, MPIC, AACK delay, and wake capability, plus `pmac_do_feature_call()`, `pmac_feature_init()`, early video resume hooks, AGP power-management hooks, `struct macio_chip`, `macio_chips[]`, MacIO flags, `macio_find()`, and register access macros.

## Control Flow
Drivers call `pmac_call_feature()` or AGP/MacIO helpers to enable, reset, suspend, resume, or query platform devices. Feature dispatch goes through `ppc_md.feature_call`.

## State And Persistence Behavior
Power/reset bits persist in MacIO/feature-control registers. `macio_chips[]` stores discovered controller state, base mappings, flags, and OF nodes. Early video resume callback state is stored for sleep recovery.

## Dependencies And Integration Points
It depends on MacIO, machdep feature call hooks, PCI, device tree, and old PowerMac platform code. It integrates with serial, storage, network, USB/FireWire, sound, sleep, GPIO, MPIC, and AGP drivers.

## Risks And Edge Cases
Machine type values overlap across generations and are historical. Feature calls mutate hardware power/reset lines. MacIO register macros assume little-endian IO access and a local `macio` variable.

## Test Signals
Boot representative PowerMac models, test device enable/reset, sleep/resume, AGP suspend/resume, GPIO reads/writes, MacIO discovery, and all affected onboard devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_feature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_low_i2c.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_low_i2c.h

## Purpose
This header declares the low-level PowerMac I2C bus API used by platform functions and drivers that need direct access to Mac I2C controllers.

## Important APIs, Types, And Functions
It defines bus type, mode, flags, and transfer direction enums; forward declares `struct pmac_i2c_bus` and `struct i2c_adapter`; and declares initialization, bus lookup, address extraction, controller/bus node/type/flag/channel accessors, adapter conversion/matching helpers, open/close, mode setting, transfer, and platform-function suspend/resume APIs.

## Control Flow
Callers find a bus from device-tree or adapter, open it optionally in polled mode, set a transfer mode, execute `pmac_i2c_xfer()` with address direction, subaddress size, buffer and length, then close the bus. Suspend/resume hooks coordinate platform-function users.

## State And Persistence Behavior
Bus state is owned by the implementation: open/closed state, mode, controller node, channel, flags, and adapter linkage. Hardware I2C controller state persists until closed or reprogrammed.

## Dependencies And Integration Points
It integrates with PowerMac device tree, Linux I2C adapters, platform functions, thermal/PMU/SMU-related devices, and suspend/resume.

## Risks And Edge Cases
Polled mode is needed in early or atomic contexts. Address direction and subaddress size must match device protocol. Failing to close or restore mode can block shared bus users.

## Test Signals
Probe PowerMac I2C devices, test adapter matching, reads/writes with all supported modes, polled transfers, suspend/resume, and bus sharing across clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pmac_low_i2c.h -->
