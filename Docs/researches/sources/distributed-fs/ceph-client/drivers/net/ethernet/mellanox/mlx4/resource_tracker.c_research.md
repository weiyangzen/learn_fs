# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/resource_tracker.c

## Purpose

`resource_tracker.c` is the mlx4 SR-IOV master-side resource ownership and command-wrapping layer. It tracks which slave/PF owns hardware resources, enforces quotas, validates guest command parameters, translates virtual port and GID/P_Key state into physical device state, and tears down all resources owned by a slave during reset/removal.

The file is central to mlx4 multi-function safety. It prevents a VF from using another function's QPs, CQs, SRQs, MTTs, MPTs, MACs, VLANs, counters, EQs, XRCDs, and flow-steering rules, and it keeps refcounts between dependent objects so teardown happens in a valid order.

## Important APIs, Types, And Functions

Key resource records:

- `struct res_common`: common rb-tree/list node with `res_id`, `owner`, `state`, transition bookkeeping, and `removing`.
- `struct res_qp`, `res_mtt`, `res_mpt`, `res_eq`, `res_cq`, `res_srq`, `res_counter`, `res_xrcdn`, `res_fs_rule`: typed wrappers that store object-specific references and state.
- `struct mac_res` and `struct vlan_res`: list-only per-slave resources with hardware indexes and refcounts.
- `struct res_gid`: QP multicast/flow steering attachment tracking.

Core tracking helpers:

- `res_tracker_lookup()` and `res_tracker_insert()` maintain per-type rb-trees keyed by resource ID.
- `add_res_range()` allocates typed tracking records, inserts them into the rb-tree and per-slave list, and rolls back partial insertion.
- `rem_res_range()` validates owner/state/refcounts and removes tracked records.
- `get_res()`/`put_res()` temporarily mark a resource busy while a wrapper validates and submits a command.
- `*_res_start_move_to()`, `res_abort_move()`, and `res_end_move()` implement checked state transitions around firmware commands.

Quota and lifecycle APIs:

- `mlx4_init_resource_tracker()` allocates per-slave lists, rb-tree roots, quota/guarantee arrays, and initializes allocators.
- `mlx4_free_resource_tracker()` releases slave resources and/or tracker structures depending on `mlx4_res_tracker_free_type`.
- `mlx4_init_quotas()` exposes PF/non-multifunction quotas through `dev->quotas`.
- `mlx4_grant_resource()` and `mlx4_release_resource()` update quota/free/reserved accounting.
- `mlx4_delete_all_resources_for_slave()` is the ordered teardown path for one slave.

Command wrappers:

- `mlx4_ALLOC_RES_wrapper()` / `mlx4_FREE_RES_wrapper()` dispatch allocation/free operations by `RES_*` type.
- MPT/MTT wrappers: `mlx4_SW2HW_MPT_wrapper()`, `mlx4_HW2SW_MPT_wrapper()`, `mlx4_QUERY_MPT_wrapper()`, `mlx4_WRITE_MTT_wrapper()`.
- QP wrappers: `mlx4_RST2INIT_QP_wrapper()`, `mlx4_INIT2RTR_QP_wrapper()`, `mlx4_RTR2RTS_QP_wrapper()`, `mlx4_RTS2RTS_QP_wrapper()`, `mlx4_SQERR2RTS_QP_wrapper()`, `mlx4_SQD2SQD_QP_wrapper()`, `mlx4_SQD2RTS_QP_wrapper()`, `mlx4_2RST_QP_wrapper()`, and `mlx4_GEN_QP_wrapper()`.
- EQ/CQ/SRQ wrappers: `mlx4_SW2HW_EQ_wrapper()`, `mlx4_HW2SW_EQ_wrapper()`, `mlx4_GEN_EQE()`, `mlx4_QUERY_EQ_wrapper()`, `mlx4_SW2HW_CQ_wrapper()`, `mlx4_HW2SW_CQ_wrapper()`, `mlx4_MODIFY_CQ_wrapper()`, `mlx4_SW2HW_SRQ_wrapper()`, `mlx4_HW2SW_SRQ_wrapper()`, `mlx4_QUERY_SRQ_wrapper()`, and `mlx4_ARM_SRQ_wrapper()`.
- Flow steering: `mlx4_QP_ATTACH_wrapper()`, `mlx4_QP_FLOW_STEERING_ATTACH_wrapper()`, `mlx4_QP_FLOW_STEERING_DETACH_wrapper()`, `mlx4_bond_fs_rules()`, and `mlx4_unbond_fs_rules()`.
- VST/VGT updates: `update_vport_qp_param()` and `mlx4_vf_immed_vlan_work_handler()`.

## Control Flow

Initialization creates per-slave resource lists, one rb-tree per resource type, and quota state. Resource allocations usually follow this pattern:

1. Check `vhcr` resource type and operation modifier.
2. Grant quota with `mlx4_grant_resource()`.
3. Allocate hardware/ICM state through an internal helper such as `__mlx4_qp_reserve_range()`, `__mlx4_alloc_mtt_range()`, `__mlx4_cq_alloc_icm()`, or `__mlx4_counter_alloc()`.
4. Add a tracking record with `add_res_range()`.
5. Roll back quota and hardware allocation on any failure.

State-changing commands mark the object busy before issuing firmware commands. For example, `mlx4_RST2INIT_QP_wrapper()` moves a QP from mapped to HW, verifies its MTT/CQ/SRQ references, adjusts scheduling/port state, sends the wrapped firmware command, increments referenced object refcounts, and ends the transition. Error paths unwind `get_res()` holds and call `res_abort_move()`.

VLAN/MAC resources are tracked as per-slave lists rather than rb-tree typed records. They call `__mlx4_register_mac()` / `__mlx4_unregister_mac()` and `__mlx4_register_vlan()` / `__mlx4_unregister_vlan()` and maintain their own refcounts.

Slave teardown marks all resources of each type busy, then walks resource types in dependency order. QPs and flow steering are removed before CQs/SRQs/MRs/MTTs so references can be decremented before backing memory is released. Each `rem_slave_*()` function converts HW-owned objects back to SW/reset state with native commands as needed, decrements dependencies, erases tracking nodes, frees ICM/bitmap resources, and releases quota.

## State And Persistence Behavior

All state is in memory under `mlx4_priv(dev)->mfunc.master.res_tracker`, per-slave lists, rb-trees, quota arrays, and per-resource refcounts. Nothing is persisted across driver reloads or device reset. The firmware holds actual object state; this tracker mirrors ownership and dependency state so wrapped VF commands can be validated.

`res_common.state`, `from_state`, and `to_state` form a transactional state machine. `RES_ANY_BUSY` is used as an in-progress marker. `removing` prevents teardown from reprocessing resources already marked for removal. QP records also persist original VLAN/QoS-related fields so `mlx4_vf_immed_vlan_work_handler()` can restore VGT behavior after forced VST settings.

## Dependencies And Integration Points

This file integrates with:

- mlx4 command transport through `mlx4_cmd()`, `mlx4_cmd_imm()`, `mlx4_DMA_wrapper()`, and `mlx4_cmd_box()` wrappers.
- mlx4 object allocators for QP/CQ/SRQ/MPT/MTT/counter/XRCD ICM and bitmaps.
- SR-IOV state in `priv->mfunc.master`, including slave active state, virtual-to-physical P_Key maps, vport operational state, and event EQ data.
- Ethernet/VLAN helpers and netdevice constants for spoof checking and VST enforcement.
- RoCE GID helpers, flow steering attach/detach helpers, and bonding mirroring logic.
- The global tracker lock returned by `mlx4_tlock(dev)`, per-slave mutexes, and QP multicast spinlocks.

## Risks

- The file is concurrency-sensitive: busy-state transitions, irq-safe spinlocks, per-slave mutexes, atomic refcounts, and firmware commands interleave. Missing `put_res()` or `res_abort_move()` can strand objects in busy state.
- Cleanup paths intentionally proceed after some firmware command failures; this avoids leaks but can desynchronize software tracking from hardware if firmware remains partially active.
- `remove_eq_ok()` appears to compare against MPT states (`RES_MPT_BUSY`/`RES_MPT_RESERVED`) rather than EQ states, which deserves review in this source snapshot.
- MAC/VLAN list management is protected by the caller's per-slave mutex in many paths, but individual helper assumptions must be maintained.
- Flow steering mirror rules use stored mailbox copies and paired resource IDs; bonding/unbonding failures can leave primary/mirror asymmetry.
- Quota accounting for per-port MAC/VLAN resources differs from global resources, increasing the risk of accounting bugs.

## Test Signals

Useful validation includes SR-IOV VF resource exhaustion tests, allocate/free rollback fault injection, QP lifecycle transitions with invalid MTT/CQ/SRQ ownership, VF attempts to use another VF's MAC/VLAN/counter/flow rule, teardown during busy commands, bonded flow-steering mirror/unmirror cycles, and VST/VGT immediate VLAN changes against live QPs. Kernel lockdep, KASAN/KCSAN, firmware command failure injection, and reference-leak checks around `mlx4_delete_all_resources_for_slave()` are high-value signals.
