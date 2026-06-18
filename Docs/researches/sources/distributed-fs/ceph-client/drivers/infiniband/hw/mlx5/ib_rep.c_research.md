# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ib_rep.c

## Purpose
`ib_rep.c` implements RDMA representor support for mlx5 eswitch offloads. It registers an auxiliary `rdma-rep` driver, loads/unloads IB representors for eswitch vports, creates a raw Ethernet RDMA device for uplink representors, binds non-uplink vports as ports on that device, and integrates with LAG/shared-FDB topologies.

## Important APIs, Types, And Functions
The key exported functions are `mlx5r_rep_init()`, `mlx5r_rep_cleanup()`, `mlx5_ib_get_rep_netdev()`, and `create_flow_rule_vport_sq()`. `mlx5_ib_vport_rep_load()` and `mlx5_ib_vport_rep_unload()` are registered as `struct mlx5_eswitch_rep_ops`. `mlx5_ib_set_vport_rep()` attaches a loaded eswitch rep to an existing `mlx5_ib_dev` port and sets the RDMA port netdev. `mlx5_ib_take_transport()` and `mlx5_ib_release_transport()` transfer RDMA transport flow-table root ownership across peer devices when shared-FDB LAG requires a common owner.

## Control Flow
Probe registers `rep_ops` with the eswitch for `REP_IB`. Loading an uplink representor usually allocates a new `mlx5_ib_dev` with `raw_eth_profile`, sets `is_rep`, sizes `ibdev->port` from local and peer vport counts, maps the RDMA port to the representor netdev, and calls `__mlx5_ib_add()`. Non-uplink vports are then represented by setting `dev->port[vport_index].rep`, setting `rep->rep_data[REP_IB].priv`, mapping the netdev with `ib_device_set_netdev()`, and adding a LAG demux rule when the vport is not native to the owner eswitch.

In shared-FDB LAG, non-master devices calculate an adjusted `vport_index` based on peer device sequence and MPESW/non-MPESW rules. The master can register peer vport reps after the uplink RDMA device exists. Unload reverses the netdev mapping and private pointers, deletes demux rules, unregisters peer reps for shared-FDB uplink teardown, releases transport ownership, and removes the RDMA device through `__mlx5_ib_remove()`.

## State And Persistence Behavior
Representor state is in memory: `rep->rep_data[REP_IB].priv` points at the owning `mlx5_ib_dev`, and `dev->port[i].rep` points back to the eswitch rep. LAG demux and RDMA transport flow-table root ownership are hardware/firmware-managed state changed during load/unload. There is no persistent disk state.

## Dependencies And Integration Points
This file integrates mlx5 eswitch representors, LAG APIs, flow steering root-device ownership, RDMA device registration through `main.c` profiles, and raw packet SQ steering. `create_flow_rule_vport_sq()` is used by raw packet QP setup to send a representor SQ to its vport via `mlx5_eswitch_add_send_to_vport_rule()`.

## Risks
Index accounting across shared-FDB, MPESW, and peer device sequence ordering is error-prone; a wrong `vport_index` maps netdevs and demux rules to the wrong RDMA port. Load/unload must be symmetric, especially transport root ownership rollback and peer representor unregister. `create_flow_rule_vport_sq()` returns `NULL` for non-reps or port zero and `ERR_PTR(-EINVAL)` when a rep is missing, so callers must distinguish no-op from hard failure.

## Test Signals
Exercise switchdev representor creation/removal, shared-FDB LAG master and non-master load order, MPESW uplinks, non-uplink vport demux rules, raw packet QP traffic through representor SQ steering, and cleanup while peer vports are still registered.
