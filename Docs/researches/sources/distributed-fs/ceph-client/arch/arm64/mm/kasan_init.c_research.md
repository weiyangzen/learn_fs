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
