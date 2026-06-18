# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge.h

Purpose: Public bridge-offload interface and top-level offload state definition for mlx5 eswitch bridge acceleration.

Important APIs/types/functions: `struct mlx5_esw_bridge_offloads` stores the owning eswitch, bridge list, port xarray, debugfs root, notifier/workqueue fields, global ingress/skip tables, ingress groups, and multicast protocol handles. Declarations expose lifecycle, port link/unlink, peer link/unlink, FDB update/create/remove, ageing and VLAN controls, multicast toggle, per-port VLAN add/delete, and MDB add/delete.

Control flow and integration: Switchdev and representor code call this API to map Linux bridge events to eswitch hardware objects. `bridge.c` owns most definitions; `bridge_mcast.c` extends multicast/MDB behavior. The notifier/workqueue fields show this object is designed to integrate with netdev/switchdev/blocking notifier paths even though this file only declares the state.

State and persistence: The structure is persistent for the life of eswitch bridge offloads and is attached to `esw->br_offloads`. It caches hardware table/group/flow handles that must be cleaned before the eswitch is dismantled.

Risks and test signals: The risk is mismatched lifecycle ownership between external notifier users and internal bridge cleanup. Test signals include successful compile against all bridge users, offloads init/cleanup under RTNL, and bridge event flows correctly finding the right `mlx5_esw_bridge_offloads` instance.
