# sources/distributed-fs/ceph-client/arch/x86/mm/kasan_init_64.c

## Purpose
This file initializes KASAN shadow memory on x86_64, from the earliest shared shadow mappings through the final per-region shadow population used after paging is fully initialized. It handles both 4-level and 5-level paging and supports optional vmalloc shadow population on demand.

## Important APIs, Types, and Functions
- `kasan_early_init()` builds early shadow page-table chains and maps the shadow range in `early_top_pgt` and `init_top_pgt`.
- `kasan_init()` replaces temporary shadow coverage with real shadow mappings for direct map, CPU entry area shared portions, kernel image, vmalloc/modules gaps, and remaining KASAN shadow bounds.
- `kasan_populate_shadow_for_vaddr()` maps shadow for a caller-provided virtual range.
- Internal helpers `kasan_populate_pgd/p4d/pud/pmd()`, `kasan_populate_shadow()`, and `map_range()` allocate shadow backing, trying huge mappings at PUD/PMD levels when aligned.
- `clear_pgds()`, `kasan_map_early_shadow()`, and shallow-population helpers manage top-level entries safely around 5-level layout collisions.

## Control Flow and State
Early initialization fills all early shadow PTE/PMD/PUD/P4D entries with `kasan_early_shadow_page`, masking unsupported page bits and including encryption. Final initialization copies the top-level table, temporarily switches CR3 to `early_top_pgt`, clears the KASAN shadow range, maps early shadows for holes, maps real shadow for every `pfn_mapped[]` range, populates CPU entry area shared shadow, handles vmalloc either shallowly or with early shadow, maps kernel text/data shadow, then switches back to `init_top_pgt`. It finally zeroes and write-protects the shared early shadow page and calls generic KASAN init.

## Dependencies and Integration Points
The file depends on memblock allocation, `pfn_mapped[]` from e820/direct-map setup, CPU entry area layout, x86 page-table allocation, KASAN generic helpers, section symbols, and TLB/CR3 operations. It coordinates with KASLR because shadow bounds and virtual bases differ under 5-level paging.

## Risks
KASAN shadow overlaps with kernel, module, EFI, and CPU entry regions near `KASAN_SHADOW_END`; the 5-level temporary P4D copy avoids clobbering unrelated mappings. Missing shadow for CPU entry or direct-map ranges can cause early faults. Using huge shadow pages requires exact alignment and allocation success fallback. TLB flushes around CR3 switches and write-protecting early shadow are correctness-critical.

## Test Signals
Booting with KASAN should produce no shadow faults during early init, CPU entry area use, vmalloc allocation, module loading, or kernel image accesses. Useful scenarios include 4-level and 5-level paging, `CONFIG_KASAN_VMALLOC`, NUMA node allocation, large-memory direct maps, and memory encryption where `_PAGE_ENC` must be preserved.
