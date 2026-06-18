# sources/distributed-fs/ceph-client/arch/xtensa/mm/highmem.c

Purpose: Initializes highmem/kmap support and cache-color-aware local kmap fixmap indices for aliasing D-caches.

Important APIs, types, and functions: `last_pkmap_nr_arr`, `pkmap_map_wait_arr`, `kmap_waitqueues_init()`, `kmap_local_map_idx()`, `kmap_local_unmap_idx()`, and `kmap_init()`.

Control flow: For aliasing D-caches, initializes per-color wait queues and maps kmap types/CPU/color to reversed fixmap indices because fixmap grows top-down. `kmap_init()` verifies PKMAP does not overlap temporary TLB mapping space and initializes wait queues.

State and persistence: Global per-color pkmap cursor/waitqueue arrays persist for highmem mapping management.

Dependencies and integration: Depends on `DCACHE_WAY_SIZE`, `DCACHE_N_COLORS`, `DCACHE_ALIAS`, highmem/fixmap constants, and `mmu.c` fixedrange initialization.

Risks: Wrong color-to-index mapping can create D-cache aliases; layout overlap with `TLBTEMP_BASE_1` is fatal at build time; CPU/type indexing must match generic kmap local expectations.

Test signals: HIGHMEM builds, kmap/kunmap local stress with different PFN colors, page cache highmem I/O, and build-time overlap checks.
