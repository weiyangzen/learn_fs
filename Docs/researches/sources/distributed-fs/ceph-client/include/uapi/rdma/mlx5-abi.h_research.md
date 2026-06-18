<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5-abi.h

## Purpose
Defines Mellanox/NVIDIA mlx5 legacy uverbs private ABI for context allocation, device capability queries, CQ/SRQ/QP/WQ/MW/AH/flow creation, packet pacing, CQE compression, RSS, striding RQ, DCI streams, mmap commands, and clock info.

## Important APIs, Types, and Functions
Read coverage: 530 lines and 14059 bytes. Visible type families include struct mlx5_ib_alloc_ucontext_req, enum mlx5_lib_caps, enum mlx5_ib_alloc_uctx_v2_flags, struct mlx5_ib_alloc_ucontext_req_v2, enum mlx5_ib_alloc_ucontext_resp_mask, enum mlx5_user_cmds_supp_uhw, enum mlx5_user_inline_mode, struct mlx5_ib_alloc_ucontext_resp, struct mlx5_ib_alloc_pd_resp, struct mlx5_ib_tso_caps, struct mlx5_ib_rss_caps, enum mlx5_ib_cqe_comp_res_format, struct mlx5_ib_cqe_comp_caps, enum mlx5_ib_packet_pacing_cap_flags, struct mlx5_packet_pacing_caps, enum mlx5_ib_mpw_caps, enum mlx5_ib_sw_parsing_offloads, struct mlx5_ib_sw_parsing_caps, struct mlx5_ib_striding_rq_caps, struct mlx5_ib_dci_streams_caps, enum mlx5_ib_query_dev_resp_flags, enum mlx5_ib_tunnel_offloads, struct mlx5_ib_query_device_resp, struct mlx5_ib_uapi_reg, enum mlx5_ib_create_cq_flags, struct mlx5_ib_create_cq, struct mlx5_ib_create_cq_resp, struct mlx5_ib_resize_cq, ... (+25 more). Important macros/constants include MLX5_ABI_USER_H, MLX5_IB_UVERBS_ABI_VERSION. Explicit ioctl-style command names include none.

## Control Flow
The provider allocates a context, negotiates command support and capability masks, creates PD/CQ/SRQ/QP/WQ and related objects with private payloads, maps UAR/doorbell/clock pages using mmap command IDs, and consumes rich query-device responses for offloads and packet processing features.

## State and Persistence Behavior
State spans hardware context, UARs, doorbells, queue buffers, object IDs, flow counters, clock synchronization data, offload capability bitmaps, and provider command support masks.

## Dependencies and Integration Points
It depends on Linux integer types and generic uverbs. It integrates with mlx5_ib, ConnectX/NVIDIA hardware, rdma-core mlx5 provider, flow steering, DevX-adjacent capabilities, and timestamp/clock mapping. Direct includes are #include <linux/types.h>, #include <linux/if_ether.h>	/* For ETH_ALEN. */, #include <rdma/ib_user_ioctl_verbs.h>, #include <rdma/mlx5_user_ioctl_verbs.h>.

## Risks and Edge Cases
Large capability structures are compatibility-sensitive; masks must gate every optional field. Mmap command IDs expose hardware pages, CQE compression and packet pacing values must match firmware, and clock-info layout affects timestamp accuracy.

## Test Signals
Run mlx5 rdma-core tests for context negotiation, query-device flags, CQ/QP/SRQ/WQ creation, RSS/TSO/packet pacing/CQE compression, mmap command coverage, clock-info validation, and 32-bit layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5-abi.h -->
