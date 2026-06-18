# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/lag.c

## Purpose
`lag/lag.c` implements mlx5 multi-port LAG orchestration. It pairs mlx5 PFs through devcom, tracks netdev bonding state, activates/modifies/deactivates firmware LAG, supports RoCE/SR-IOV/shared-FDB/multipath/MPESW modes, manages port-selection mappings, exposes demux flow-table helpers, and exports LAG query helpers to other mlx5 subsystems.

## Important APIs, Types, And Functions
- Firmware command wrappers create/modify/destroy LAG and vport LAG.
- Device management functions include `mlx5_lag_add_mdev`, `mlx5_lag_remove_mdev`, `mlx5_lag_add_netdev`, and `mlx5_lag_remove_netdev`.
- Activation paths include `mlx5_activate_lag`, `mlx5_deactivate_lag`, `mlx5_disable_lag`, `mlx5_modify_lag`, `mlx5_lag_check_prereq`, and `mlx5_lag_shared_fdb_supported`.
- Demux APIs `mlx5_lag_demux_init`, cleanup, rule add, and rule delete manage LAG demux flow tables/rules.
- Exported query helpers report RoCE/active/hash/master/SR-IOV/shared-FDB state, slave port, number of ports, peer devices, device sequence, bond speed, and congestion counters.

## Control Flow And State
On mdev add, the driver registers a devcom component keyed by system image GUID and net namespace, joins or allocates a shared `mlx5_lag`, registers netdev and port-change notifiers, marks the lowest device index as master once all ports pair, and creates debugfs. Netdev add records the netdev and sets readiness when all ports have netdevs.

Netdev notifier events snapshot bond membership, TX type/hash type, lower-state link/tx flags, inactive slaves, and bond speed into `lag_tracker`, then queue bond work. Bond work obtains devcom lock, serializes on `ldev->lock`, and calls `mlx5_do_bond`. Activation removes/reshuffles auxiliary devices when needed, computes queue-affinity or hash mappings, creates optional port-selection flow tables, sends firmware create LAG, optionally enables shared FDB, restores IB devices/reps, sends active-backup notifications, and sets aggregate vport speeds. Modify updates mapping or active-port bits. Disable resets vport speeds, removes drop rules/single-FDB state, destroys firmware LAG, and restores devices.

## State And Persistence Behavior
State lives in `struct mlx5_lag`: mode, mode flags, readiness flags, number of ports/buckets, mode-change counter, virtual-to-physical map, kref, PF xarray with master mark, tracker, workqueue, devcom/netdev notifiers, MP/MPESW/port-select state, demux table/group/rules, and per-PF netdev/drop-rule state. Hardware state includes firmware LAG context, port-selection resources, eswitch single-FDB links, ingress drop rules, demux flow tables, and vport speed limits.

## Dependencies And Integration Points
The file depends on bonding netdev APIs, devcom, eswitch/offloads, port-selection flow steering, multipath and MPESW helpers, mlx5 command interface, debugfs, EQ notifiers, SR-IOV/RoCE state, auxiliary-device rescans, and devlink-adjacent reload behavior. It is a central integration point for RDMA, eswitch, representors, congestion counters, and LAG-aware consumers.

## Risks And Edge Cases
This code has complex concurrency: global spinlock for short queries, per-LAG mutex for state transitions, devcom lock for cross-device coordination, workqueue retries, and mode-change suppression. Activation must unwind port-selection, shared FDB, drop rules, and device rescans correctly on failures. Bond membership logic assumes all LAG ports and only those ports are enslaved to the same master. Shared FDB support requires exact eswitch capability/peer readiness. Removing a device waits for mode changes and must tear down debugfs early.

## Test Signals
Test two-port and multi-port pairing, bond enslave/release, active-backup and hash modes, lower-state changes, hash-based port selection, shared-FDB switchdev activation, RoCE LAG activation, VF/SR-IOV rejection cases, mdev/netdev removal while active, demux table/rule lifecycle, vport speed aggregation/reset, exported state helpers, and congestion counter aggregation.
