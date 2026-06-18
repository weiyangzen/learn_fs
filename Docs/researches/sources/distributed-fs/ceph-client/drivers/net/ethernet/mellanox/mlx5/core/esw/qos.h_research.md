# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/qos.h

## Purpose
Declares the mlx5 E-Switch QoS interface used by core eswitch lifecycle code, vport configuration paths, and devlink rate operations. The header is active only under `CONFIG_MLX5_ESWITCH` and exposes the scheduling-domain and vport/node rate APIs implemented elsewhere.

## Important APIs, Types, and Functions
The lifecycle entry points are `mlx5_esw_qos_init()` and `mlx5_esw_qos_cleanup()`, paired with `mlx5_esw_qos_vport_disable()` and `mlx5_esw_qos_vport_qos_free()` for vport teardown and configuration reset. Per-vport rate control is exposed through `mlx5_esw_qos_set_vport_rate()`, `mlx5_esw_qos_get_vport_rate()`, `mlx5_esw_qos_vport_get_sched_elem_ix()`, `mlx5_esw_qos_vport_get_parent()`, and `mlx5_esw_qos_vport_update_parent()` as declared in `eswitch.h`. Devlink rate integration is represented by leaf and node setters for `tx_share`, `tx_max`, TC bandwidth arrays, parent changes, and node create/delete callbacks.

## Control Flow and State
This header has no executable control flow. Its prototypes describe the QoS state model stored in `struct mlx5_eswitch` and `struct mlx5_vport`: the eswitch owns a QoS domain with a refcount and root TSAR index, while each vport may own a scheduling node and optional per-TC scheduling nodes. Callers must honor the QoS domain lock noted in `eswitch.h`; state is persistent in firmware scheduling elements and mirrored by vport pointers.

## Dependencies and Integration Points
Depends on `struct mlx5_eswitch`, `struct mlx5_vport`, `struct mlx5_esw_sched_node`, `struct devlink_rate`, and `struct netlink_ext_ack` declarations from the eswitch, devlink, and QoS implementation layers. It is included by `eswitch.c` for init/cleanup and vport disable, by vport configuration code for VF rate APIs, and by devlink rate registration code for hierarchical rate tree operations.

## Risks and Test Signals
The main risks are lock-order mistakes around QoS domain state, leaked scheduling nodes when vports are disabled or VF info is cleared, inconsistent `min_rate`/`max_rate` reporting, and devlink parent changes leaving firmware and software hierarchy out of sync. Useful signals include devlink rate node/leaf create-delete tests, repeated SR-IOV enable/disable with configured rates, TC bandwidth validation, vport reset/clear paths, and lockdep coverage around QoS mutations.
