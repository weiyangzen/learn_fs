# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mcg.c

## Purpose

`mcg.c` implements mlx4 multicast group, unicast steering, promiscuous steering, and device-managed flow steering glue. It abstracts two hardware models: legacy firmware-managed MGM/AMGM hash chains for A0/B0 steering, and device-managed flow steering (DMFS) where rules are encoded into firmware mailboxes and returned as registration IDs. Ethernet and InfiniBand upper drivers use this file to attach or detach QPs to multicast/unicast destinations, install promisc/default receive rules, steer tunnel traffic, and query steering entry sizing.

## Important APIs, Types, And Functions

Sizing helpers `mlx4_get_mgm_entry_size()` and `mlx4_get_qp_per_mgm()` derive hardware MCG entry size from `dev->oper_log_mgm_entry_size`. Low-level firmware command wrappers include `mlx4_QP_FLOW_STEERING_ATTACH()`, `mlx4_QP_FLOW_STEERING_DETACH()`, `mlx4_READ_ENTRY()`, `mlx4_WRITE_ENTRY()`, `mlx4_WRITE_PROMISC()`, and `mlx4_GID_HASH()`.

Legacy steering is built around `struct mlx4_mgm`, `struct mlx4_mcg_table`, `struct mlx4_steer`, `struct mlx4_steer_index`, and `struct mlx4_promisc_qp` from `mlx4.h`. `find_entry()` walks the firmware MGM/AMGM hash chain for a GID and protocol. `mlx4_qp_attach_common()` and `mlx4_qp_detach_common()` mutate those chains, allocate/free AMGM indexes from `priv->mcg_table.bitmap`, and update software promisc bookkeeping. `new_steering_entry()`, `existing_steering_entry()`, `check_duplicate_entry()`, `promisc_steering_entry()`, `can_remove_steering_entry()`, `add_promisc_qp()`, and `remove_promisc_qp()` keep software lists consistent with hardware entries.

DMFS support is handled by `trans_rule_ctrl_to_hw()`, `parse_trans_rule()`, `mlx4_flow_attach()`, `mlx4_flow_detach()`, `mlx4_tunnel_steer_add()`, and `mlx4_trans_to_dmfs_attach()`. Exported mapping helpers `mlx4_map_sw_to_hw_steering_mode()`, `mlx4_map_sw_to_hw_steering_id()`, and `mlx4_hw_rule_sz()` translate public rule enums into firmware IDs and sizes. Public attach APIs include `mlx4_multicast_attach()`, `mlx4_multicast_detach()`, `mlx4_unicast_attach()`, `mlx4_unicast_detach()`, `mlx4_flow_steer_promisc_add()`, `mlx4_flow_steer_promisc_remove()`, and the multicast/unicast promisc add/remove wrappers. `mlx4_PROMISC_wrapper()` services wrapped VF promisc commands on the PF.

## Control Flow

For legacy attach, callers pass QP, GID, protocol, steering type, and loopback policy. `mlx4_qp_attach_common()` allocates a mailbox, locks `priv->mcg_table.mutex`, calls `find_entry()`, initializes an empty hash entry or allocates an AMGM entry if needed, checks capacity and duplicate QPN membership, appends the QPN with optional loopback-block bit, writes the entry, links new AMGM entries from the previous chain element, and updates Ethernet steering/promisc lists. Detach performs the reverse: find the entry, suppress removal when a promisc duplicate still needs the membership, remove the QPN by swapping with the last member, either rewrite the non-empty entry or unlink/free empty MGM/AMGM entries, and tolerate internal-error state for close paths.

For DMFS, callers construct `struct mlx4_net_trans_rule` lists. `mlx4_flow_attach()` verifies the QP exists, writes a control header, serializes each spec node into the mailbox with `parse_trans_rule()`, and issues `MLX4_QP_FLOW_STEERING_ATTACH`, returning a firmware registration ID. Detach sends that ID to firmware. `mlx4_multicast_attach()` dispatches by `dev->caps.steering_mode`: A0 ignores Ethernet multicast, B0/native uses legacy MGM or wrapped QP attach, and device-managed mode builds a DMFS rule. Promisc in DMFS stores one registration ID per port for all-promisc or all-multicast mode.

## State And Persistence Behavior

State is runtime-only and hardware-resident. The hardware MCG table stores hash-chain entries with protocol bits, GID, member QPNs, and next pointers. The software mirror stores only enough per-port/per-steer metadata to maintain promisc behavior: promisc QP lists and steering-entry duplicate lists. `priv->mcg_table.bitmap` tracks available AMGM indexes; direct MGM indexes are hash-derived and not allocated. `dev->regid_promisc_array` and `dev->regid_allmulti_array` store DMFS registration IDs for default promisc rules. All legacy table mutation is serialized by `priv->mcg_table.mutex`; DMFS attach/detach relies on firmware registration IDs and QP existence.

## Dependencies And Integration Points

This file depends on mlx4 command mailbox allocation, QP lookup, firmware command opcodes, device caps selected in `main.c`, and data structures declared in `mlx4.h` and public mlx4 device headers. It is called by mlx4 Ethernet receive-mode, multicast-list, RSS/tunnel offload, RFS/ethtool flow, and mlx4 InfiniBand multicast paths. Wrapped command entry points integrate VF requests with PF resource and port translation. The DMFS parser supports Ethernet, IB, IPv4, TCP, UDP, and VXLAN specs; IPv6 is explicitly unsupported in `parse_trans_rule()`.

## Risks

Capacity handling is critical. MGM entries have `dev->caps.num_qp_per_mgm` slots, so promisc QPs can exhaust entries that were otherwise valid. AMGM allocation and chain relinking must be rolled back on firmware write failure or stale hash chains can leak unreachable entries. Software duplicate tracking must match hardware membership exactly; otherwise removing a promisc QP can accidentally drop traffic for a regular QP or leave promisc traffic active. The code indexes `gid[5]` as a port for legacy paths, so malformed GIDs or callers that do not encode port consistently fail validation or steer to the wrong port. DMFS rule serialization depends on exact firmware sizes and endianness, and unsupported IPv6 specs return `-EOPNOTSUPP`. Internal-error close paths intentionally convert some detach failures to success, which is correct for teardown but can hide hardware state loss in tests.

## Test Signals

Exercise attach/detach for IB and Ethernet in A0, B0, multifunction wrapped, and DMFS modes. Verify AMGM allocation/free when hash collisions create chains, full-entry failure when QPN capacity is reached, duplicate attach idempotence, promisc add/remove with existing steering entries, promisc removal when duplicate entries remain, allmulti/promisc DMFS registration ID lifecycle, VXLAN tunnel rule install/remove, invalid port and invalid rule ID rejection, IPv6 unsupported behavior, and teardown while `MLX4_DEVICE_STATE_INTERNAL_ERROR` is set.
