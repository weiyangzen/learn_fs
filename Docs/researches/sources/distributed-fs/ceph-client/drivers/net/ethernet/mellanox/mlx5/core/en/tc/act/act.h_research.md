# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/act.h

Purpose: Defines the mlx5e TC action parser interface, shared parse state, action operation callbacks, and extern parser instances.

Important types: `struct mlx5e_tc_act_parse_state` tracks flow, extack, accumulated actions, tunnel/MPLS/VLAN state, output ifindexes, CT private data, and branch flags. `struct mlx5e_tc_act` is a vtable for validation, parsing, post-parse, multi-table decisions, standalone action offload/destroy/stats, branch control, and termination metadata.

Control flow and state: Parser code initializes one parse state per flow and passes it through all action vtables, allowing earlier actions to affect later validation, such as `ptype` before redirect-ingress or tunnel encap before mirred.

Dependencies and integration: Includes flow offload, netlink extack, eswitch, and pedit declarations. Consumed by every file under `tc/act` and by higher-level TC flow parser code.

Risks and tests: The shared mutable parse state is easy to misuse when action order changes. Tests should exercise action combinations that rely on transient flags: tunnel+mirred, mpls+vlan eth push/pop, ptype+redirect_ingress, ct+post_parse, and police branch controls.
