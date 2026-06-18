## sources/distributed-fs/ceph-client/mm/kasan/init.c

Purpose: builds and tears down zero shadow mappings used by Generic and software tag-based KASAN before full shadow memory is available and for large accessible-but-uninstrumented ranges.

Important APIs and data: defines `kasan_early_shadow_page` and early page-table arrays for P4D/PUD/PMD/PTE levels. Main exported helpers are `kasan_populate_early_shadow()`, `kasan_remove_zero_shadow()`, and `kasan_add_zero_shadow()`.

Control flow: population walks kernel page tables from PGD down, installing shared early shadow tables for aligned large ranges and allocating lower-level tables via memblock before slab or page-table allocators after slab availability. All PTEs map the write-protected `kasan_early_shadow_page`. Removal walks the shadow page-table hierarchy, clears mappings only when they point to the early shadow page/tables, and frees now-empty page-table pages. Add-zero-shadow computes shadow bounds and rolls back on failure.

State and persistence: state is in global early shadow page-table arrays and kernel page tables under `init_mm`. The early shadow page later acts as reusable zero shadow for valid ranges not backed by real KASAN shadow.

Dependencies and integration: depends on memblock, `init_mm`, architecture page-table levels, `kasan_mem_to_shadow()`, slab availability, and kernel page-table allocation/free APIs.

Risks and test signals: risks include incorrect alignment to `KASAN_MEMORY_PER_SHADOW_PAGE`, clearing real shadow mappings by mistake, leaking page-table pages, and using allocation APIs before they are initialized. Tests include early boot with multiple page-table levels, memory hotplug or vmalloc shadow add/remove paths, and debug page-table validation.
