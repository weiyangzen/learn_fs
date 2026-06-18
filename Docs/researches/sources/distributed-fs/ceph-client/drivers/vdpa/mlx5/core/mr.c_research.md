# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/mr.c

Purpose: mlx5 vDPA memory registration layer. It converts vhost IOTLB maps or DMA passthrough into mlx5 memory keys used by firmware virtqueues and control VQ translation.

Important APIs/types/functions: direct-MR helpers populate MTTs and create/destroy MTT mkeys asynchronously. `create_user_mr()` merges contiguous IOTLB ranges by permission, creates direct keys capped by KLM size, inserts null-key gaps, and creates an indirect KLM mkey. `create_dma_mr()` builds a physical-address mkey. `mlx5_vdpa_create_mr()`, `mlx5_vdpa_update_mr()`, `mlx5_vdpa_get_mr()`, and `mlx5_vdpa_put_mr()` manage lifetime. `mlx5_vdpa_update_cvq_iotlb()` mirrors maps into `vringh` IOTLB. `mlx5_vdpa_init_mr_resources()` and destroy set up delayed GC.

Control flow: set-map callers create a new MR, then update the ASID slot. Old MRs are refcount-dropped and moved to a GC list when no virtqueue references remain. GC runs after a delay to avoid blocking rapid `.set_map()` calls. Reset clears ASID slots and optionally recreates DMA MR for devices supporting `umem_uid_0`.

State and persistence: `mlx5_vdpa_mr` tracks mkey, direct children, IOTLB copy, user/DMA mode, refcount, and list membership. Direct children hold SG tables and DMA mappings. `mres` owns current ASID MRs, group mapping, active list, GC list, lock, workqueue, and shutdown flag.

Dependencies and integration: used by `mlx5_vnet.c` for `.set_map`, `.reset_map`, vq mkey updates, and CVQ vringh translation. Depends on mlx5 mkey commands, DMA mapping, scatterlists, vhost IOTLB, GCD/page sizing, and async command batching from `resources.c`.

Risks: physical addresses are converted with `pfn_to_page(__phys_to_pfn(pa))`, so IOTLB maps must represent normal memory. Error cleanup in `add_direct_chain()` walks `mr->head`, while newly built entries are first stored in a temporary list; cleanup of partially built temp entries is a point to audit. Delayed destruction means resource removal must flush GC and expose leaks.

Test signals: empty map, DMA MR fallback, multi-range IOTLB with holes and permission changes, rapid map replacement while queues hold references, CVQ ASID remap, reset with `VDPA_RESET_F_CLEAN_MAP`, and injected mkey/DMA-map failures.
