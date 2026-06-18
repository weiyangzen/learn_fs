# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/lgcy.h

Purpose: Declares external ACL APIs used when the E-Switch is in legacy mode. It gives legacy mode code a narrow interface for ingress and egress ACL setup/cleanup without exposing group or rule internals.

Important APIs/types/functions: The header declares `esw_acl_egress_lgcy_setup()`, `esw_acl_egress_lgcy_cleanup()`, `esw_acl_ingress_lgcy_setup()`, and `esw_acl_ingress_lgcy_cleanup()`. It depends on `eswitch.h` for `struct mlx5_eswitch` and `struct mlx5_vport`.

Control flow and integration: `legacy.c` calls the ingress then egress setup functions for non-manager vports, and unwinds ingress if egress setup fails. Cleanup is ordered egress then ingress. This header is the contract between generic legacy vport handling and ACL implementation files.

State and persistence: The header stores no state. Its declared functions manage vport ACL tables, groups, rules, and counters owned by `struct mlx5_vport`.

Risks and test signals: The main risk is API drift between legacy ACL implementation and vport lifecycle. Test signals are successful compile under legacy eswitch support, clean SR-IOV legacy enable/disable, and correct ACL recreation after VLAN/spoof-check changes.
