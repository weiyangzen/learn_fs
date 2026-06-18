<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_verbs.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_verbs.h

## Purpose
Defines mlx5 ioctl payload enums and small structures shared by the mlx5 provider-specific ioctl command IDs, including flow action flags, flow table types, packet reformat types, DMA-BUF registration flags, DevX async headers, device-memory types, UAR allocation types, query-port flags, VAR flags, and query responses.

## Important APIs, Types, and Functions
Read coverage: 124 lines and 3907 bytes. Visible type families include enum mlx5_ib_uapi_flow_action_flags, enum mlx5_ib_uapi_flow_table_type, enum mlx5_ib_uapi_flow_action_packet_reformat_type, enum mlx5_ib_uapi_reg_dmabuf_flags, struct mlx5_ib_uapi_devx_async_cmd_hdr, enum mlx5_ib_uapi_dm_type, enum mlx5_ib_uapi_devx_create_event_channel_flags, struct mlx5_ib_uapi_devx_async_event_hdr, enum mlx5_ib_uapi_pp_alloc_flags, enum mlx5_ib_uapi_uar_alloc_type, enum mlx5_ib_uapi_query_port_flags, enum mlx5_ib_uapi_var_alloc_flags, struct mlx5_ib_uapi_reg, struct mlx5_ib_uapi_query_port. Important macros/constants include MLX5_USER_IOCTL_VERBS_H. Explicit ioctl-style command names include MLX5_USER_IOCTL_VERBS_H.

## Control Flow
These payloads are carried in mlx5 ioctl attributes. Userspace reads async command/event headers from fds, describes packet reformat/flow actions, selects DM/UAR/VAR allocation modes, supplies DMA-BUF flags, and receives register or port-query responses.

## State and Persistence Behavior
State is held by the corresponding mlx5 ioctl objects and async fds: event cookies, command output sizes, DM object type, UAR/VAR handles, and queried hardware register/port values.

## Dependencies and Integration Points
It depends on Linux integer types and is paired with `mlx5_user_ioctl_cmds.h`. It integrates with DevX, flow action offload, DMA-BUF memory registration, UAR allocation, and port query paths. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Async headers must be stable for fd read ABI. Packet reformat and flow table enums must match firmware expectations, and DMA-BUF flags alter memory pinning/import behavior.

## Test Signals
Validate DevX async command/event reads, flow action packet reformat creation, DM/UAR/VAR allocation variants, query-port flags, DMA-BUF MR flag handling, and size/alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_verbs.h -->
