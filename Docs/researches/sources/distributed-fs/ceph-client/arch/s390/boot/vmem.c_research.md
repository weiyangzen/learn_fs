<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/vmem.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/vmem.c

Purpose: Constructs the initial s390 kernel address space during decompression, including identity/direct mappings, kernel image mapping, lowcore mappings, invalid user ASCE, direct-map page counters, and optional KASAN shadow mappings.

Important APIs/types/functions: Defines bootdata-preserved `s390_invalid_asce` and optionally `direct_pages_count[]`. Key API is `setup_vmem(kernel_start, kernel_end, asce_limit)`. Internal machinery includes `enum populate_mode`, `pgtable_populate()`, `pgtable_p4d/pud/pmd/pte_populate()`, `boot_crst_alloc()`, `boot_pte_alloc()`, `resolve_pa_may_alloc()`, large-page helpers, and KASAN shadow helpers.

Control flow: `setup_vmem()` marks all online pages no-DAT before allocating page tables, temporarily switches `init_mm.pgd` to the physical `swapper_pg_dir`, chooses region-table type from `asce_limit`, initializes swapper and invalid page directories, maps lowcore first with 4K pages, then usable identity ranges, kernel text/data excluding the `TEXT_OFFSET` hole, amode31 direct region, absolute lowcore, and a deliberately invalid memcpy-real page. KASAN builds additionally populate mapped, zero, and shallow shadow ranges. Finally it loads kernel/user ASCEs into lowcore and control registers and restores `init_mm.pgd`.

State and persistence: Produces persistent page tables in physical memory allocated as `RR_VMEM`, updates page DAT attributes, direct-map counters, `memcpy_real_ptep`, lowcore ASCE fields, `s390_invalid_asce`, and `init_mm.context.asce`.

Dependencies and integration points: Called from `startup_kernel()` after relocations. Depends on `physmem_info`, `vmlinux` metadata offsets, s390 page-table macros, EDAT1/EDAT2 facilities, KASAN metadata, lowcore relocation, identity-base selection, and absolute lowcore helpers.

Risks: Page-table construction is architecture-critical. Large-page eligibility must match CPUID facilities and alignment; mapping lowcore after identity mapping could accidentally create a large page at zero; invalid `POPULATE_NONE` mapping is intentional for memcpy-real setup. KASAN zero-shadow sharing must not be overwritten by later population. Any mismatch between physical and virtual vmlinux offsets corrupts kernel entry.

Test signals: Boots with 3-level and 4-level paging, EDAT1/EDAT2 on/off, KASAN enabled, memory holes, relocated lowcore, randomized identity base, and direct-map page count validation. Page-table dumps and early fault injection around unmapped memcpy-real area are useful.

Source read size: 556 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/vmem.c -->
