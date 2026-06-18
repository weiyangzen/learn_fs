# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ofld.h

Purpose: Declares ACL APIs for switchdev/offload mode and supplies no-op or success stubs for selected ingress drop helpers when `CONFIG_MLX5_ESWITCH` is disabled.

Important APIs/types/functions: Egress declarations cover setup/cleanup, bounce-rule destruction, bond/unbond, and `mlx5_esw_acl_egress_fwd2vport_supported()`. Ingress declarations cover offload setup/cleanup, vport metadata update, and source-port drop rule create/destroy. The inline support helper requires offloads mode, metadata matching, and `egress_acl_forward_to_vport`.

Control flow and integration: Offloads and LAG code call these functions while configuring vport ACLs and representor behavior. The preprocessor split keeps callers compilable without eswitch support for drop-rule helpers, while most offload ACL APIs only exist when the feature is enabled.

State and persistence: The header has no storage. It defines the contract for mutating per-vport ingress/egress offloads ACL state, metadata rules, bounce rules, and bonding-related forwarding.

Dependencies and risks: It depends on mode and capability checks being accurate. A false positive from `mlx5_esw_acl_egress_fwd2vport_supported()` could route traffic to unsupported ACL actions. Test signals include build coverage with and without `CONFIG_MLX5_ESWITCH`, offloads mode ACL setup, egress fwd-to-vport paths, and LAG bond/unbond ACL behavior.
