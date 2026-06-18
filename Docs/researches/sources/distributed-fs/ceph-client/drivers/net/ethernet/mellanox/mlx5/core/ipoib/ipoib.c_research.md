# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ipoib.c

## Purpose
`ipoib/ipoib.c` implements mlx5 enhanced IPoIB netdevice support. It builds IPoIB-specific mlx5e parameters, creates and transitions underlay UD QPs, creates TIS objects tied to underlay QPNs, sets up flow steering/RX resources, defines netdev/RDMA callbacks, and exposes RDMA netdev allocation parameters.

## Important APIs, Types, And Functions
- Public entry points include `mlx5i_init`, `mlx5i_cleanup`, `mlx5i_create_underlay_qp`, `mlx5i_destroy_underlay_qp`, `mlx5i_init_underlay_qp`, `mlx5i_uninit_underlay_qp`, `mlx5i_create_tis`, `mlx5i_get_tisn`, `mlx5i_update_nic_rx`, `mlx5i_dev_init`, `mlx5i_dev_cleanup`, `mlx5i_get_stats`, parent get/put helpers, and `mlx5_rdma_rn_get_params`.
- `mlx5i_nic_profile` supplies mlx5e profile callbacks for parent IPoIB devices.
- RDMA netdev callbacks attach/detach multicast groups, transmit via `mlx5i_sq_xmit`, and update pkey index.

## Control Flow And State
`mlx5_rdma_rn_get_params` verifies IB port type and enhanced IPoIB capability, then returns private size, TX/RX queue counts, device parameter, and setup callback. Setup initializes parent resources and QPN hash table for primary devices, initializes mlx5e private state/profile, attaches the netdev, installs RDMA send/mcast callbacks, and sets destructor behavior.

TX initialization creates an underlay UD QP and TIS. RX initialization creates mlx5e flow steering, queue counters, drop RQ, RX resources, aRFS tables, TTC table, and ethtool steering. Opening a netdev transitions the underlay QP through RST2INIT/INIT2RTR/RTR2RTS, adds the underlay QPN to RX flow steering, opens channels, refreshes TIRs, and activates channels. Close removes QPN steering, deactivates/closes channels, and resets the QP.

## State And Persistence Behavior
Per-netdev state lives in `struct mlx5i_priv` plus embedded `mlx5e_priv`: underlay QPN, TISN, qkey, pkey index, parent/child flags, QPN hash table, and mlx5e channels/RX resources. Hardware state includes QP state, TIS object, multicast group attachments, and flow-steering underlay QPN entries.

## Dependencies And Integration Points
The file depends on RDMA netdev APIs, IB verbs address handles, mlx5e channels/params/RX resources/flow steering/timestamps, firmware QP/TIS commands, and IPoIB TX WQE layout from `ipoib.h`. It integrates with `ipoib_vlan.c` for pkey child profiles and QPN lookup.

## Risks And Edge Cases
Open failure paths must unwind QP state, flow steering, and channels in reverse order. QPN can be derived from netdev address when `mkey_by_name` is supported, coupling address layout to QP creation. Parent refcounts and `num_sub_interfaces` must stay under RTNL. IPoIB supports only one TC and linked-list RQs here; enabling unsupported mlx5e features would break assumptions.

## Test Signals
Validate RDMA netdev allocation on IB-capable devices, parent open/close, multicast attach/detach, TX/RX traffic, MTU changes through safe parameter switch, QP state transitions, TIS create/destroy, underlay QPN steering, stats aggregation, and cleanup on setup/open failures.
