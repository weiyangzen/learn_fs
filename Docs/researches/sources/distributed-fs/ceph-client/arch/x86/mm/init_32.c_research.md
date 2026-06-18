# sources/distributed-fs/ceph-client/arch/x86/mm/init_32.c

## Purpose
This file implements 32-bit x86 kernel memory initialization: early page-table construction, lowmem/highmem sizing, fixed-map/kmap setup, boot-time paging finalization, write-protect testing, and late kernel text/rodata hardening. It is the 32-bit counterpart to `init_64.c`, with extra handling for highmem and PAE/non-PAE page-table folding.

## Important APIs, Types, and Functions
- `populate_extra_pmd()` and `populate_extra_pte()` allocate or locate kernel page-table levels for early extra mappings, using `one_md_table_init()` and `one_page_table_init()`.
- `kernel_physical_mapping_init()` builds the direct mapping from physical RAM to `PAGE_OFFSET`, optionally using PSE 2 MiB pages and falling back to 4 KiB PTEs.
- `early_ioremap_page_table_range_init()` pre-creates fixmap page tables for early ioremap users, then calls `early_ioremap_reset()`.
- `find_low_pfn_range()`, `lowmem_pfn_init()`, `highmem_pfn_init()`, and `initmem_init()` decide the low/high memory split and initialize `high_memory`, `highstart_pfn`, `highend_pfn`, and memblock node ownership.
- `paging_init()`, `native_pagetable_init()`, `arch_mm_preinit()`, and `mem_init()` sequence boot memory and page-table readiness.
- `mark_rodata_ro()` and `mark_nxdata_nx()` apply final page attributes to kernel text, rodata, and data.

## Control Flow and State
Boot code starts with provisional mappings from assembly, then `kernel_physical_mapping_init()` runs in two passes: first preserving initial identity attributes while deciding page sizes, then flushing TLBs and rewriting the desired NX/global/executable attributes. `native_pagetable_init()` removes boot-time mappings above `max_low_pfn` and calls `paging_init()`. Highmem-aware paths allocate contiguous low pages for kmap PTEs and can relocate early fixmap PTE pages to maintain linearity. Memory sizing state is held in global PFN variables and in `high_memory`; `__vmalloc_start_set` marks vmalloc layout readiness.

## Dependencies and Integration Points
The file depends on x86 page-table helpers, memblock, e820-derived PFN bounds, highmem, fixmap, early ioremap, PCI IOMMU allocation, OLPC device tree setup, and CPA/set-memory APIs. Its exports of `__supported_pte_mask` and `__default_kernel_pte_mask` feed page-protection construction used across the architecture and by modules.

## Risks
The direct-map construction must obey Intel's rule against changing page size and attributes in one write; the two-pass algorithm is critical. Highmem/fixmap PTE relocation has BUG_ON checks because nonlinear early allocations would corrupt kmap/fixmap layout. Incorrect low/high PFN trimming can hide RAM, expose unmapped memory, or break vmalloc/highmem boundaries. `mark_rodata_ro()` and NX setup depend on precise section alignment.

## Test Signals
Boot logs report LOWMEM/HIGHMEM, mapped low RAM, WP-bit validation, and rodata write protection. CPA debug can temporarily revert and reapply rodata permissions. Useful validation includes 32-bit boot with PAE/non-PAE, `highmem=` variants, CONFIG_HIGHMEM on/off, early ioremap users, and page-table dumps confirming kernel text executable while data is NX/read-only as expected.
