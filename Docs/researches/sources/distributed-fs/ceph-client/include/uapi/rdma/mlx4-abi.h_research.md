<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx4-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mlx4-abi.h

## Purpose
Defines Mellanox mlx4 userspace ABI versions 3 and 4 for context, PD, CQ, SRQ, QP, WQ, RSS, TSO, and extended query-device data.

## Important APIs, Types, and Functions
Read coverage: 191 lines and 5117 bytes. Visible type families include struct mlx4_ib_alloc_ucontext_resp_v3, struct mlx4_ib_alloc_ucontext_resp, struct mlx4_ib_alloc_pd_resp, struct mlx4_ib_create_cq, struct mlx4_ib_create_cq_resp, struct mlx4_ib_resize_cq, struct mlx4_ib_create_srq, struct mlx4_ib_create_srq_resp, struct mlx4_ib_create_qp_rss, struct mlx4_ib_create_qp, struct mlx4_ib_create_wq, struct mlx4_ib_modify_wq, struct mlx4_ib_create_rwq_ind_tbl_resp, enum mlx4_ib_rx_hash_function_flags, enum mlx4_ib_rx_hash_fields, struct mlx4_ib_rss_caps, enum query_device_resp_mask, struct mlx4_ib_tso_caps, struct mlx4_uverbs_ex_query_device_resp. Important macros/constants include MLX4_ABI_USER_H, MLX4_IB_UVERBS_NO_DEV_CAPS_ABI_VERSION, MLX4_IB_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
Userspace allocates context and PD resources, creates CQs/SRQs/QPs/WQs with private queue buffers, queries RSS/TSO/device capability responses, and uses response fields for BlueFlame, UAR, and queue programming.

## State and Persistence Behavior
State includes UAR/BlueFlame mappings, queue numbers, CQ/SRQ/QP/WQ IDs, RSS indirection table handles, TSO capabilities, and device capability masks.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with mlx4_ib, older ConnectX devices, and rdma-core mlx4 provider. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
The header explicitly forbids native pointer types to keep 32/64-bit layouts compatible. ABI v3/v4 response differences, RSS hash flags, and query-device masks must remain stable.

## Test Signals
Run mlx4 provider lifecycle tests, v3 no-dev-caps compatibility, 32-bit layout checks, CQ/QP/SRQ/WQ/RSS creation, TSO capability query, and invalid hash field rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx4-abi.h -->
