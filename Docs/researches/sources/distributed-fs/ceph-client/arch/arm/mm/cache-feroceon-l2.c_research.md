# sources/distributed-fs/ceph-client/arch/arm/mm/cache-feroceon-l2.c

Purpose: initializes and services the Marvell Feroceon L2 cache controller, including physical-address range maintenance, optional write-through override, prefetch disablement, and L2 enable sequencing.

Important APIs/types/functions: important helpers are `l2_get_va`, `l2_put_va`, `l2_clean_pa`, `l2_clean_pa_range`, `l2_clean_inv_pa`, `l2_inv_pa`, `l2_inv_pa_range`, `l2_inv_all`, `calc_range_end`, `feroceon_l2_inv_range`, `feroceon_l2_clean_range`, `feroceon_l2_flush_range`, `flush_and_disable_dcache`, `invalidate_and_disable_icache`, `disable_l2_prefetch`, `enable_l2`, `feroceon_l2_init`, and `feroceon_of_init`.

Control flow: initialization optionally reads DT for `marvell,kirkwood-cache`/`marvell,feroceon-cache`, applies write-through override, disables L2 prefetch, installs `outer_cache` range callbacks, and enables L2. Enabling L2 temporarily disables L1 D-cache and I-cache as required, invalidates L2, sets the extra-features L2 enable bit, then restores L1 caches.

State and persistence: `l2_wt_override` persists as runtime policy. The `outer_cache` function table is updated globally. CPU extra-feature register bits persist until reset or later firmware/kernel changes.

Dependencies and integration points: depends on Marvell Feroceon CP15 private registers, highmem temporary mappings for physical range ops, device tree, `outer_cache`, and ARM cache flush helpers.

Risks: hardware range operations require start and end within the same page because only the start address is translated. Range operations stall the pipeline, so `MAX_RANGE_SIZE` chunking is performance-critical. Enabling/disabling L1 caches during init is delicate and must run early with IRQ protection.

Test signals: boot on Feroceon/Kirkwood platforms, validate DT write-through bit behavior, run DMA/outer-cache range tests crossing page boundaries, test highmem mappings, and verify L2 enable/disable messages and coherency after suspend or bootloader state variations.
