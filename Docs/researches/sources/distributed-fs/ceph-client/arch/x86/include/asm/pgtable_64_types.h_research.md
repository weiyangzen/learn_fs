# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_64_types.h

Purpose: defines x86-64 page-table value types, runtime 5-level paging controls, table geometry, and the canonical kernel virtual address layout for direct map, vmalloc, vmemmap, modules, fixmap-adjacent areas, EFI, CPU entry area, and KMSAN metadata.

Important APIs, types, and functions: typedefs PTE/PMD/PUD/P4D/PGD/protection value types as `unsigned long`, defines `pte_t` and `pmd_t`, declares `__pgtable_l5_enabled`, `pgtable_l5_enabled()`, `pgdir_shift`, and `ptrs_per_p4d`. Geometry macros include `PGDIR_SHIFT`, `PTRS_PER_PGD`, `P4D_SHIFT`, `PTRS_PER_P4D`, `PUD_SHIFT`, `PMD_SHIFT`, sizes/masks, and `MAX_POSSIBLE_PHYSMEM_BITS`. Layout macros include `MAXMEM`, guard hole, LDT, VMALLOC/VMEMMAP bases, KMSAN shadow/origin ranges, modules, ESPFIX, CPU entry area, EFI VA range, `EARLY_DYNAMIC_PAGE_TABLES`, `PGD_KERNEL_START`, and `_PAGE_SWP_EXCLUSIVE`.

Control flow: `pgtable_l5_enabled()` either reads early boot state or CPU feature state. Many address macros select L4 versus L5 layout at runtime through base globals.

State and persistence: runtime state is limited to 5-level enable and geometry/base globals initialized during boot/KASLR.

Dependencies and integration points: depends on sparsemem, KASLR, CPU feature detection, KMSAN, PTI/LDT, modules, EFI runtime mapping, and CPU entry area setup.

Risks: layout overlaps are fatal and security-sensitive. KASLR ranges must not collide with fixed regions. KMSAN shrinks usable vmalloc and reserves shadow/origin quarters. `PGDIR_SHIFT` is runtime on x86-64, so code must not assume it is constant.

Test signals: 4-level and 5-level boot, KASLR memory randomization, KMSAN builds, module loading, vmalloc/vmemmap stress, EFI runtime calls, CPU entry area mapping, and address sanitizer/debug page-table layout checks.
