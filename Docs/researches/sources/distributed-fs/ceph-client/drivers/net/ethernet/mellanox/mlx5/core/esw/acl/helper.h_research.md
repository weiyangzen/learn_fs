# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/helper.h

Purpose: Declares shared E-Switch ACL helper entry points used by legacy and offload ingress/egress ACL implementations. The header centralizes flow-table creation/destruction helpers and common ingress allow-rule destruction so mode-specific files can share the same vport ACL storage in `struct mlx5_vport`.

Important APIs/types/functions: `esw_acl_table_create()` creates an ingress or egress ACL flow table for a vport and namespace. Egress helpers expose VLAN ACL setup/teardown and group management. Ingress helpers expose table and allow-rule cleanup. The only direct type dependency is `struct mlx5_eswitch`, `struct mlx5_vport`, and `struct mlx5_flow_destination` from `eswitch.h` and mlx5 flow steering.

Control flow and integration: This header is included by `ingress_lgcy.c`, `ingress_ofld.c`, and corresponding egress ACL sources. Callers create tables, groups, and rules in mode-specific order, but cleanup is funneled through these declarations to avoid duplicated manipulation of `vport->ingress.acl`, `vport->egress`, and common allow rules.

State and persistence: No state is stored in the header. The declared helpers mutate per-vport ACL handles, flow groups, flow rules, and counters held under mlx5 vport structures. Those resources are hardware steering objects and must be destroyed before vport teardown.

Dependencies and risks: Correctness depends on callers matching create and destroy paths and not leaving stale `struct mlx5_flow_handle` or `struct mlx5_flow_group` pointers. Header staleness would cause mode-specific ACL files to diverge. Test signals include successful SR-IOV enable/disable, VLAN/spoof-check toggles, and no leaked flow tables on error unwinds.
