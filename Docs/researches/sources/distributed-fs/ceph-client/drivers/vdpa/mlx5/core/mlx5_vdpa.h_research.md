# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/core/mlx5_vdpa.h

Purpose: shared mlx5 vDPA core declarations for resource ownership, memory registration, control virtqueue state, async commands, and logging.

Important APIs/types/functions: defines `mlx5_vdpa_direct_mr`, `mlx5_vdpa_mr`, `mlx5_vdpa_resources`, `mlx5_control_vq`, `mlx5_vdpa_mr_resources`, `mlx5_vdpa_dev`, and `mlx5_vdpa_async_cmd`. Enumerates vq groups/asids. Declares resource commands, MR lifecycle/update APIs, CVQ IOTLB update, DMA MR creation/reset, and async command executor.

Control flow: no executable flow; it defines cross-file contracts used by `resources.c`, `mr.c`, and `mlx5_vnet.c`.

State and persistence: central in-memory state includes hardware resources (`pdn`, UAR, kick BAR mapping, uid, null mkey), feature/status/generation, MR arrays/refcounts/deferred-GC lists, CVQ vringh/IOTLB state, workqueues, and async command context.

Dependencies and integration: depends on mlx5 core, vDPA, vringh, vhost IOTLB, and Ethernet constants. Logging macros include function, line, and pid for kernel diagnostics.

Risks: group-to-ASID mapping and MR refcounting must stay synchronized with vnet operations. Header is broad, so structure layout changes affect all mlx5 vDPA files.

Test signals: compile all mlx5 vDPA objects, validate every declared function has implementation, and exercise MR/CVQ/resource lifetimes through vDPA add/reset/remove.
