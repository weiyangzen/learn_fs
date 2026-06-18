# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/csum.c

Purpose: Validates TC checksum recalculation offload constraints for mlx5e.

Important API: `mlx5e_tc_act_csum` exposes `can_offload` and a no-op parse action. `csum_offload_supported()` requires an existing modify-header action and restricts update flags to IPv4/TCP/UDP.

Control flow and state: No persistent state. Validation observes `attr->action` to ensure a previous pedit/mangle action requested `MLX5_FLOW_CONTEXT_ACTION_MOD_HDR`.

Dependencies and integration: Uses kernel TC csum flags, netlink extack, and netdev warnings. Integrated through the TC action dispatch table.

Risks and tests: Action order matters: csum before pedit should fail. Unsupported checksum flags must return a clear extack. Tests should cover pedit+csum success, csum-only failure, and unsupported flags.
