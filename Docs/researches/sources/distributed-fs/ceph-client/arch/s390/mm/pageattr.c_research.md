## sources/distributed-fs/ceph-client/arch/s390/mm/pageattr.c

Purpose: changes kernel direct-map and vmalloc page attributes on s390: RO/RW, NX/X, invalid/default, and 4K splitting. It also initializes storage keys, reports direct-map page sizes, checks page presence, and supports debug page allocation/KFENCE map toggling.

Important APIs, types, and functions: exported/shared APIs include `__storage_key_init_range()`, `arch_report_meminfo()`, `split_pud_page()`, `__set_memory()`, `set_direct_map_invalid_noflush()`, `set_direct_map_default_noflush()`, `set_direct_map_valid_noflush()`, `kernel_page_present()`, and `__kernel_map_pages()`. Internal walkers `walk_p4d_level()`, `walk_pud_level()`, `walk_pmd_level()`, and `walk_pte_level()` update tables. `cpa_mutex` serializes changes and is also used by ptdump.

Control flow: `__set_memory()` masks NX operations on non-NX CPUs, normalizes the range, locks `cpa_mutex`, changes the target mapping, then applies RO/RW aliases for vmalloc-backed pages to the direct map. Large PUD/PMD entries are split when 4K pages are requested or a range does not cover a full large entry. Updates use `pgt_set()`, which chooses CRDTE on EDAT2 or CSPG otherwise. Debug map toggling invalidates PTEs with IPTE range support when available.

State and persistence: mutates kernel page tables and direct-map page counters `direct_pages_count[]` under `CONFIG_PROC_FS`. Storage key initialization writes hardware storage keys. No persistent disk state.

Dependencies and integration points: depends on s390 CRDTE/CSPG/IPTE instructions, vmem allocation helpers, direct-map accounting, vmalloc metadata, CPU feature checks, `set_memory` API, KFENCE, and debug_pagealloc.

Risks: splitting large direct-map entries increases page-table memory and must update direct-map counters accurately. Alias propagation intentionally excludes execute permissions; incorrectly propagating X would weaken direct-map NX policy. Page invalid/default changes are noflush APIs, so callers must manage required flushing semantics. Invalid input ranges return `-EINVAL` on missing page-table entries.

Test signals: `set_memory_ro/rw/nx/x/4k` tests on aligned and partial large-page ranges, `/proc/meminfo` DirectMap counters, vmalloc alias permission changes, debug_pagealloc/KFENCE page poisoning, and `kernel_page_present()` around invalidated direct-map pages.
