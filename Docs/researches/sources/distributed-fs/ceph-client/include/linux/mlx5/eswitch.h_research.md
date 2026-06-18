# `sources/distributed-fs/ceph-client/include/linux/mlx5/eswitch.h`

## Purpose

`eswitch.h` defines the public embedded-switch interface used by mlx5 Ethernet, RDMA, and offload code. It describes eswitch modes, representor registration state, representor operations, metadata encodings in registers C0/C1, send-to-vport rule creation, and compatibility stubs when `CONFIG_MLX5_ESWITCH` is disabled.

## Important APIs, Types, and Constants

- `MLX5_ESWITCH_MANAGER(mdev)` wraps the generic eswitch-manager capability bit.
- Mode constants distinguish `MLX5_ESWITCH_LEGACY` from `MLX5_ESWITCH_OFFLOADS`. Representor type constants include `REP_ETH`, `REP_IB`, and `NUM_REP_TYPES`; registration state constants include `REP_UNREGISTERED`, `REP_REGISTERED`, and `REP_LOADED`.
- `enum mlx5_switchdev_event` defines pair/unpair events for representor coordination.
- `struct mlx5_eswitch_rep_ops` supplies callbacks to load/unload a representor, retrieve protocol-specific device state, and receive switchdev events.
- `struct mlx5_eswitch_rep_data` stores protocol-private data and an atomic state; `struct mlx5_eswitch_rep` records vport, VLAN, IB vport index, VLAN refcount, backpointer to `mlx5_eswitch`, and per-representor-type data.
- Public representor APIs include `mlx5_eswitch_register_vport_reps()`, `mlx5_eswitch_unregister_vport_reps()`, `mlx5_eswitch_get_proto_dev()`, `mlx5_eswitch_vport_rep()`, `mlx5_eswitch_uplink_get_proto_dev()`, and `mlx5_eswitch_add_send_to_vport_rule()`.
- Metadata macros define Reg C0 source-port encoding with PF number, vport bits, and user-data bits; helpers expose masks and per-vport metadata for match/set. Reg C1 macros encode reserved bit, tunnel ID, tunnel options, zone ID, slow-table goto-vport marks, bridge ingress push VLAN marks, and IPsec mapped ID masks.
- `mlx5_eswitch_mode()`, `mlx5_eswitch_get_encap_mode()`, `mlx5_eswitch_reg_c1_loopback_enabled()`, `mlx5_eswitch_vport_match_metadata_enabled()`, `mlx5_eswitch_get_total_vports()`, and `mlx5_eswitch_get_core_dev()` expose eswitch state to callers.
- Inline helpers `is_mdev_legacy_mode()`, `is_mdev_switchdev_mode()`, and `mlx5_eswitch_manager_vport()` provide common mode/vport decisions.

## Control Flow and Lifetimes

Representor consumers register operations for a representor type, after which eswitch code can load per-vport representors, store protocol-private pointers in `rep_data`, and transition atomic state through registered and loaded phases. Consumers retrieve representors by vport or uplink and add FDB forwarding rules with `mlx5_eswitch_add_send_to_vport_rule()`, which implementation files route through slow FDB/offload tables. Unregistration must unload and detach representor data before the eswitch or its vports disappear.

Metadata flow is defined by bit layouts rather than functions. Reg C0 carries source-port metadata for vport matching and user data; Reg C1 carries tunnel, zone, bridge, and IPsec metadata used by offload miss and restoration paths. Callers must use the published masks to avoid overlapping metadata domains.

When `CONFIG_MLX5_ESWITCH` is absent, mode and capability helpers return legacy/false/zero/null defaults. That lets generic callers compile but disables switchdev/offload behavior.

## State and Persistence Behavior

The opaque `struct mlx5_eswitch` owns persistent switch state in implementation files. This header exposes persistent representor state through `struct mlx5_eswitch_rep`: vport identity, VLAN state, per-protocol private data, and state atomics. Flow handles returned by `mlx5_eswitch_add_send_to_vport_rule()` persist in hardware/software flow steering until removed by `mlx5_del_flow_rules()` from `fs.h`.

## Dependencies and Integration Points

The header depends on `driver.h`, `vport.h`, and devlink eswitch types. It integrates with Ethernet representors (`en_rep.c`), RDMA IB representors (`ib_rep.c`), eswitch offloads (`eswitch_offloads.c`), bridge and TC offload code, IPsec/MACsec metadata users, and flow steering through `struct mlx5_flow_handle`. It also uses `mlx5_core_is_ecpf_esw_manager()` from `driver.h` to decide whether the manager vport is PF or ECPF.

## Risks and Edge Cases

- Reg C0/C1 bit allocations are shared across offloads. A new feature using these registers can break source-port matching, tunnel restoration, bridge VLAN marks, or IPsec IDs if masks overlap.
- Stubbed behavior under `!CONFIG_MLX5_ESWITCH` can hide missing capability checks; callers must tolerate legacy/false returns.
- Representor `rep_data` state is atomic, but private data lifetime still requires careful load/unload ordering.
- Send-to-vport rules cross eswitch and peer-eswitch contexts; incorrect `on_esw`, `from_esw`, representor, or SQN pairing can misdirect traffic.
- `mlx5_eswitch_manager_vport()` is valid only for eswitch managers, as noted in the header.

## Test Signals

Exercise legacy and switchdev modes, representor register/load/unload for Ethernet and IB, peer representor pairing/unpairing, FDB send-to-vport rules, ECPF manager vport behavior, metadata matching in Reg C0, tunnel/zone/IPsec Reg C1 restoration, bridge ingress VLAN special marks, and builds with `CONFIG_MLX5_ESWITCH` both enabled and disabled.
