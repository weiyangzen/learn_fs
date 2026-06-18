# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/rep/bridge.c

Purpose: bridges Linux switchdev bridge events to mlx5 eswitch bridge offload operations for representor ports, peer eswitches, LAGs, VLANs, MDBs, FDBs, and bridge attributes.

Important APIs/functions: `mlx5e_rep_bridge_init` and `mlx5e_rep_bridge_cleanup`. Internal notifier callbacks handle netdev upper changes, switchdev blocking object/attribute changes, async FDB events, and periodic FDB aging/update work.

Control flow: init creates eswitch bridge offload state under RTNL, allocates an ordered workqueue, registers switchdev, blocking switchdev, and netdevice notifiers, then starts periodic update work. Netdev upper changes link/unlink local or peer vports to bridge masters after validating LAG shared-FDB constraints. Blocking switchdev callbacks add/delete VLANs and MDBs and set bridge attrs such as ageing time, VLAN filtering/protocol, multicast, and supported flags. Nonblocking FDB events are copied to heap work items, processed under RTNL, and then cleaned up.

State and persistence: state lives in `struct mlx5_esw_bridge_offloads`, including workqueue, notifiers, delayed update work, and eswitch bridge tables. Individual FDB work owns a dev reference and copied MAC address.

Dependencies and integration: uses Linux bridge/switchdev/netdevice notifiers, mlx5 eswitch bridge helpers, LAG shared-FDB checks, and representor vport/vhca-id discovery.

Risks: notifier contexts require careful allocation flags and async work. LAG and peer-eswitch paths depend on identifying the correct representor and hardware owner. Cleanup ordering must cancel delayed work and unregister all notifiers before destroying bridge state.

Test signals: bridge enslave/unenslave, VLAN/MDB add/delete, FDB add/delete to bridge/device, LAG master validation, peer representor offload, and teardown with queued FDB work.
