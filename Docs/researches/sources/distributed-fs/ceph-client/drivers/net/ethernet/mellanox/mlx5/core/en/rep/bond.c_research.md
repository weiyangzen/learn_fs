# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bond.c

Purpose: handles bonding of mlx5 eswitch representors by assigning shared metadata and programming ingress/egress ACL behavior for active-slave failover.

Important APIs/functions: `mlx5e_rep_bond_init`, `mlx5e_rep_bond_cleanup`, `mlx5e_rep_bond_enslave`, and `mlx5e_rep_bond_unslave`. Internal notifier handlers process `NETDEV_CHANGEUPPER` and `NETDEV_CHANGELOWERSTATE`.

Control flow: init registers a per-netdev notifier when egress forward-to-vport ACLs are supported. Enslave creates or reuses metadata for the LAG master, allocates a slave entry, and programs ingress vport metadata. Unslave clears ingress metadata, removes egress bond ACLs, updates representor bond RX rules, and frees metadata when the last slave leaves. On lower-state changes, the active TX-enabled slave becomes the forwarding vport for passive representors; the active representor gets the unique metadata RX rule.

State and persistence: `struct mlx5e_rep_bond` owns a notifier and metadata list. Each LAG metadata object tracks eswitch, LAG netdev, metadata register value, slave list, and count. Hardware ACL programming persists until updated or unslaved.

Dependencies and integration: uses netdevice LAG events, representor private data, eswitch ACL helpers, match metadata allocation, and `mlx5e_rep_bond_update`.

Risks: all enslave/unslave paths require RTNL. Cleanup unregisters the notifier but does not explicitly walk metadata, relying on netdev unlink events. Incorrect active-slave handling can misdirect representor traffic.

Test signals: representor bond create/delete, active slave failover, metadata allocation exhaustion, mixed non-representor lower devices, and notifier unregister during teardown.
