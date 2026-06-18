# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/umr.h

## Purpose
`umr.h` declares the mlx5 RDMA UMR interface used to create, revoke, reregister, and update memory keys and their translation tables through send-queue UMR WQEs. It is the capability gate between generic mlx5 MR code and hardware-specific UMR quirks.

## Important APIs, types, and functions
Key constants define UMR translation limits and alignment: `MLX5_MAX_UMR_PAGES`, `MLX5_MAX_UMR_EXTENDED_SHIFT`, `MLX5_IB_UMR_OCTOWORD`, and `MLX5_IB_UMR_XLT_ALIGNMENT`. `mlx5r_umr_can_load_pas()` rejects PAS-list UMR when firmware cannot modify page size or lacks extended offsets for large MRs. `mlx5r_umr_can_reconfig()` decides whether access-flag changes can be issued by UMR, especially remote atomic and relaxed-ordering changes. `mlx5r_umr_get_xlt_octo()` converts byte counts to aligned octoword counts. `mlx5r_umr_context` stores completion status for synchronous UMR waits, and `mlx5r_umr_wqe` describes the common control/mkey/data WQE layout. Exported functions cover resource init/cleanup, MR revoke, PD/access reregistration, PAS updates, XLT range updates, page-shift changes, and dmabuf page-size updates.

## Control flow
Callers in MR registration/reregistration paths first check capability helpers, build UMR WQEs using the declared layouts, post them through mlx5 send-queue helpers, and wait for completion through `mlx5r_umr_context`. Range APIs allow partial translation refreshes while full helpers update the whole MR.

## State and persistence
The header itself owns no persistent state. It defines contracts for in-memory completion objects and WQE layout, while the actual persistent effects are firmware-owned mkey state, access flags, translation-table pages, page size, and free/enabled mkey status.

## Dependencies and integration points
It depends on `mlx5_ib.h`, mlx5 core capability macros, RDMA access flags, mkey descriptors, completions, and the send path in `wr.c`. It is consumed by mlx5 MR, ODP, dmabuf, and fast-reg code that needs UMR updates.

## Risks
Capability checks encode hardware quirks rather than simple feature bits. If they are relaxed incorrectly, the driver can post UMRs that firmware rejects or, worse, enable an mkey with an invalid translation. Alignment and octoword sizing must match firmware ABI. Access reconfiguration must stay synchronized with implementation-side mkey masks.

## Test signals
Useful tests include MR registration/reregistration on devices with and without `umr_modify_entity_size_disabled`, large MR updates above 64K pages without extended offsets, remote atomic access changes, relaxed-ordering access changes, dmabuf page-size changes, revoke paths, and UMR completion error propagation.
