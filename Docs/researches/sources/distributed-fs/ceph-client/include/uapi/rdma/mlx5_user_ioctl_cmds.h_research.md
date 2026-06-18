<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_cmds.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_cmds.h

## Purpose
Defines mlx5 provider-specific uverbs ioctl object, method, and attribute IDs for DevX, device memory, UAR/VAR, flow matcher/flow/action, steering anchors, PD query, port query, DMA-BUF MR registration, and Data Direct sysfs path queries.

## Important APIs, Types, and Functions
Read coverage: 365 lines and 11234 bytes. Visible type families include enum mlx5_ib_create_flow_action_attrs, enum mlx5_ib_dm_methods, enum mlx5_ib_dm_map_op_addr_attrs, enum mlx5_ib_query_dm_attrs, enum mlx5_ib_alloc_dm_attrs, enum mlx5_ib_devx_methods, enum mlx5_ib_devx_other_attrs, enum mlx5_ib_devx_obj_create_attrs, enum mlx5_ib_devx_query_uar_attrs, enum mlx5_ib_devx_obj_destroy_attrs, enum mlx5_ib_devx_obj_modify_attrs, enum mlx5_ib_devx_obj_query_attrs, enum mlx5_ib_devx_obj_query_async_attrs, enum mlx5_ib_devx_subscribe_event_attrs, enum mlx5_ib_devx_query_eqn_attrs, enum mlx5_ib_devx_obj_methods, enum mlx5_ib_var_alloc_attrs, enum mlx5_ib_var_obj_destroy_attrs, enum mlx5_ib_var_obj_methods, enum mlx5_ib_uar_alloc_attrs, enum mlx5_ib_uar_obj_destroy_attrs, enum mlx5_ib_uar_obj_methods, enum mlx5_ib_devx_umem_reg_attrs, enum mlx5_ib_devx_umem_dereg_attrs, enum mlx5_ib_pp_obj_methods, enum mlx5_ib_pp_alloc_attrs, enum mlx5_ib_pp_obj_destroy_attrs, enum mlx5_ib_devx_umem_methods, ... (+28 more). Important macros/constants include MLX5_USER_IOCTL_CMDS_H, MLX5_IB_DW_MATCH_PARAM. Explicit ioctl-style command names include MLX5_USER_IOCTL_CMDS_H.

## Control Flow
Userspace issues generic uverbs ioctl commands using these IDs to allocate/query/destroy mlx5-specific objects, submit DevX commands, subscribe to async events, register UMEM, create flow matchers and flows, allocate packet pacing and UAR resources, query PD/port/device context, and create flow actions.

## State and Persistence Behavior
Persistent state is in mlx5 uverbs objects: DevX objects, UMEM registrations, async command/event fds, VAR/UAR/page-pacing handles, flow matchers, steering anchors, flow handles, and flow actions.

## Dependencies and Integration Points
It depends on Linux integer types and `ib_user_ioctl_cmds.h`. It integrates with mlx5_ib's ioctl uAPI, rdma-core mlx5 provider, DevX low-level command access, flow steering, DMA-BUF MR registration, and sysfs Data Direct support. Direct includes are #include <linux/types.h>, #include <rdma/ib_user_ioctl_cmds.h>.

## Risks and Edge Cases
ID stability and mandatory attribute validation are critical. DevX exposes low-level firmware commands, so input/output buffer sizes, object lifetimes, event subscription IDs, and flow match parameter sizes must be tightly checked.

## Test Signals
Run mlx5 DevX and flow steering tests, UMEM/VAR/UAR/page-pacing lifecycle tests, async event fd tests, DMA-BUF MR registration, bad attribute fuzzing, and flow matcher/action create/destroy coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/mlx5_user_ioctl_cmds.h -->
