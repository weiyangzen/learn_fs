## sources/distributed-fs/ceph-client/arch/arm/mm/kasan_init.c

### Purpose
Initializes ARM KASAN shadow mappings, first with a shared early shadow page and later with real lowmem/module/pkmap shadow pages.

### Important APIs, Types, And Functions
Important state is `tmp_pgd_table` and LPAE `tmp_pmd_table`. Main routines are `kasan_early_init`, `kasan_init`, `kasan_pgd_populate`, `kasan_pmd_populate`, `kasan_pte_populate`, `clear_pgds`, and local `create_mapping`.

### Control Flow
Early init locates processor operations, verifies shadow layout, and maps the whole KASAN shadow range to `kasan_early_shadow_page`. Full init copies current page tables to temporary tables so instrumented code can run while early shadow is removed, switches MMU to the temporary PGD, clears shadow PMDs, populates real shadow for lowmem ranges under `arm_lowmem_limit`, optionally modules and pkmap, makes early shadow PTEs read-only, switches back to `swapper_pg_dir`, clears the early shadow page, and starts generic KASAN.

### State, Dependencies, And Integration
State is boot-only page-table scratch storage and allocated shadow pages from memblock. Depends on memblock allocation below `MAX_DMA_ADDRESS`, ARM page-table helpers, CPU proc lookup, `arm_lowmem_limit`, module/vmalloc config, and generic KASAN. Integrates with early MMU setup and vmalloc KASAN handling.

### Risks And Test Signals
Risks include executing instrumented code with missing shadow, mapping highmem shadow incorrectly, LPAE PGD/PMD layout assumptions, and stale TLBs across PGD switches. Test KASAN boot, lowmem/highmem split, module load with/without KASAN_VMALLOC, LPAE and non-LPAE builds, and deliberate KASAN fault detection.
