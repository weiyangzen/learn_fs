# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hmc.c

## Purpose
`hmc.c` implements Host Memory Cache backing-store management for IRDMA resources. It calculates segment descriptor (SD) and page descriptor (PD) ranges for HMC object types, allocates DMA-coherent backing pages, publishes SD entries through the CQP path, invalidates hardware PD caches, and tears objects down with use-count checks.

## Important APIs, types, and functions
The exported control points are `irdma_sc_create_hmc_obj`, `irdma_sc_del_hmc_obj`, `irdma_hmc_sd_one`, `irdma_add_sd_table_entry`, `irdma_add_pd_table_entry`, `irdma_remove_pd_bp`, `irdma_prep_remove_sd_bp`, and `irdma_prep_remove_pd_page`. Internal helpers `irdma_find_sd_index_limit` and `irdma_find_pd_index_limit` translate an object range into SD/PD limits using object `base`, `size`, and count. `irdma_set_sd_entry` and `irdma_clr_sd_entry` encode the hardware SD update payload.

## Control flow, state, and persistence
Creation validates object bounds, skips Gen3+ local-memory objects, derives SD and PD ranges, allocates any missing SD table entries, optionally allocates PD backing pages, records SD indexes to program, marks SDs valid, and commits the additions with `process_cqp_sds`. Deletion first removes valid paged backing pages, then prepares SD invalidation for direct or paged SDs, optionally frees PBLE PD metadata for VF/PBLE HMC info, sends SD clear commands when privileged and not resetting, and finally frees DMA memory. Runtime state persists only in kernel memory: `hmc_info->sd_table`, `sd_entry->valid`, PD table use counts, and DMA addresses. Hardware persistence is the programmed SD/PD view until cleared or reset.

## Dependencies and integration points
The file depends on HMC types from `hmc.h`, register bit definitions from `irdma.h`/`defs.h`, CQP methods through `struct irdma_sc_dev`, coherent DMA allocation, and privileged PF register writes for PD invalidation. PBLE setup in `pble.c` reuses `irdma_add_sd_table_entry`, `irdma_add_pd_table_entry`, and `irdma_hmc_sd_one`.

## Risks and test signals
Key risks are off-by-one range math, SD index overflow, stale valid bits after partial allocation failure, unbalanced `use_cnt`, and invalidation index mistakes. Useful tests are fault injection in DMA/kzalloc paths, create/delete of ranges spanning SD boundaries, paged versus direct SD cases, PBLE-specific HMC info deletion, Gen3 local-memory skip behavior, and reset teardown where CQP SD clear is intentionally bypassed.
