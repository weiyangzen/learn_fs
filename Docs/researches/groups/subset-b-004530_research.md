# Research Group: subset-b-004530

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/resource_tracker.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/resource_tracker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/sense.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/sense.c

## Purpose

`sense.c` implements mlx4 port-type sensing for devices that can dynamically detect whether a physical port should run InfiniBand or Ethernet. It periodically issues firmware `SENSE_PORT` commands for auto-configured ports and requests port-type changes when the sensed configuration is valid.

## Important APIs, Types, And Functions

- `mlx4_SENSE_PORT()` sends `MLX4_CMD_SENSE_PORT` and returns an `enum mlx4_port_type`.
- `mlx4_do_sense_ports()` iterates all device ports, senses only ports enabled by `sense->do_sense_port[]`, `sense->sense_allowed[]`, and `possible_type == MLX4_PORT_TYPE_AUTO`, and falls back to defaults on errors or zero results.
- `mlx4_sense_port()` is the delayed-work callback that locks `port_mutex`, senses ports, validates with `mlx4_check_port_params()`, and applies with `mlx4_change_port_types()`.
- `mlx4_start_sense()`, `mlx4_stop_sense()`, and `mlx4_sense_init()` manage the deferrable delayed work.

## Control Flow

Initialization stores the device pointer, enables sensing for all ports by default, and initializes `sense_poll` as deferrable work. Starting is conditional on `MLX4_DEV_CAP_FLAG_DPDP`; if the device lacks dynamic port detection, no polling is queued.

Each poll builds a sensed type array using current `dev->caps.port_type[1]` as defaults. Invalid firmware values greater than `2` are rejected. If no type is sensed for a port, the existing configuration remains. The worker then validates the full port set and calls the port-type change function. Regardless of success, it requeues itself after `MLX4_SENSE_RANGE`.

## State And Persistence Behavior

State is volatile and stored in `mlx4_priv(dev)->sense`: the delayed work object, device pointer, and per-port enable/allow arrays. Port type defaults come from `dev->caps.port_type`. There is no persistence beyond the running driver instance.

## Dependencies And Integration Points

This file depends on the mlx4 command interface, device capabilities, global mlx4 workqueue `mlx4_wq`, `priv->port_mutex`, and port-type validation/change helpers. It is tightly coupled to dynamic port detection support and should only actively poll when DPDP capability is present.

## Risks

- Firmware sense failures silently fall back to current defaults, which is safe but can hide persistent sensing failures except for logs.
- Reconfiguration happens under `port_mutex`; callers that also manipulate port state must preserve lock ordering.
- The worker always requeues after a validation failure, so repeated invalid configurations can produce recurring work.

## Test Signals

Test with DPDP-capable hardware or mocked command responses for Ethernet, InfiniBand, invalid values, and command failures. Verify `mlx4_stop_sense()` cancels the delayed work synchronously and that port type changes are not attempted when validation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/sense.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/srq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/srq.c

## Purpose

`srq.c` manages mlx4 shared receive queues. It allocates SRQ ICM/table entries, creates hardware SRQ contexts, tracks live SRQs in a radix tree for event dispatch, arms and queries SRQs, and releases SRQ resources safely while asynchronous events may still hold references.

## Important APIs, Types, And Functions

- `mlx4_srq_alloc()` creates an SRQ, inserts it into the radix tree, builds the firmware SRQ context, and transitions it with `SW2HW_SRQ`.
- `mlx4_srq_free()` transitions the SRQ back to software, removes it from the radix tree, waits for outstanding event references, and frees ICM.
- `mlx4_srq_event()` looks up an SRQ from an async event and invokes its callback if it can acquire a refcount.
- `mlx4_srq_arm()` and `mlx4_srq_query()` wrap firmware arm/query commands.
- `__mlx4_srq_alloc_icm()` / `__mlx4_srq_free_icm()` are native table/bitmap allocation helpers.
- `mlx4_srq_alloc_icm()` / `mlx4_srq_free_icm()` use `ALLOC_RES`/`FREE_RES` when running in multi-function mode.
- `mlx4_init_srq_table()`, `mlx4_cleanup_srq_table()`, and `mlx4_srq_lookup()` manage the table/radix-tree container.

## Control Flow

Allocation reserves an SRQ number and ICM, inserts the caller-provided `struct mlx4_srq` into `srq_table->tree`, allocates a command mailbox, fills `struct mlx4_srq_context` with size, stride, XRC domain, CQ number, MTT base address, PD, and doorbell record address, then sends `SW2HW_SRQ`. On failure it removes the radix entry and frees ICM.

Freeing sends `HW2SW_SRQ`, logs but continues on command failure, deletes the radix-tree entry, drops the initial refcount, waits for event handlers to drain through the completion, and frees ICM.

Event dispatch masks the SRQN by `num_srqs - 1`, looks up the SRQ under the table spinlock, uses `refcount_inc_not_zero()` to avoid racing a free, invokes the event callback outside the lock, and completes the free path when the last reference drops.

## State And Persistence Behavior

Runtime state lives in `mlx4_priv(dev)->srq_table`: spinlock, radix tree, and bitmap for non-slave devices. Each `struct mlx4_srq` has `srqn`, callback, completion, and refcount state supplied by upper layers. Hardware SRQ context persists only in device firmware while the SRQ is active.

## Dependencies And Integration Points

The file integrates with mlx4 command wrappers, ICM table management, bitmap allocation, radix trees, MTT address helpers, and exported SRQ APIs used by RDMA/core consumers. In SR-IOV/multifunction mode, it delegates SRQ number and ICM allocation to the master resource tracker via wrapped `ALLOC_RES` commands.

## Risks

- Free continues after `HW2SW_SRQ` failure; this prevents software leaks but can leave firmware state uncertain.
- Radix-tree lookup masks SRQN with `num_srqs - 1`, relying on power-of-two sizing semantics from the device caps.
- Event callback correctness depends on upper layers not freeing callback-owned memory before `mlx4_srq_free()` completion.
- Allocation cleanup must keep radix, ICM table, completion table, and bitmap rollback in sync.

## Test Signals

Exercise SRQ allocate/free, forced failures after radix insertion and after mailbox allocation, async event delivery during free, query/arm command failures, and multifunction `ALLOC_RES`/`FREE_RES` delegation. KASAN/refcount debugging is useful for event/free races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/Kconfig

## Purpose

This Kconfig file defines build-time feature selection for the mlx5 core driver and its Ethernet, SR-IOV, offload, steering, subfunction, FPGA, DPLL, and crypto acceleration features. It controls which pieces of the large `mlx5_core` module are available and which kernel subsystems must be present.

## Important Options

- `MLX5_CORE`: tristate core driver for Mellanox/NVIDIA 5th generation ConnectX/Connect-IB adapters; depends on PCI, optional MLXFW, optional PTP, optional Hyper-V PCI interface, optional HWMON, and selects `AUXILIARY_BUS` and `NET_DEVLINK`.
- `MLX5_CORE_EN`: Ethernet support; depends on networking and `MLX5_CORE`, selects page pool and DIM support.
- `MLX5_EN_ARFS`, `MLX5_EN_RXNFC`, and `MLX5_MPFS`: Ethernet receive steering/classification and multi-PF switch features.
- `MLX5_ESWITCH`: SR-IOV e-switch support, including legacy and switchdev modes.
- `MLX5_BRIDGE`, `MLX5_CLS_ACT`, `MLX5_TC_CT`, and `MLX5_TC_SAMPLE`: bridge and traffic-control offload support.
- `MLX5_CORE_EN_DCB`, `MLX5_CORE_IPOIB`: DCB and IPoIB feature gates.
- `MLX5_MACSEC`, `MLX5_EN_IPSEC`, `MLX5_EN_TLS`, `MLX5_EN_PSP`: cryptographic/security protocol offload gates.
- `MLX5_SW_STEERING` and `MLX5_HW_STEERING`: software-managed and hardware-managed flow steering.
- `MLX5_SF` and `MLX5_SF_MANAGER`: auxiliary-bus subfunction device support and devlink-managed subfunction ports.
- `MLX5_DPLL`: separate tristate DPLL support.
- `MLX5_FPGA`: Innova FPGA support compiled into mlx5 core.

## Control Flow

Kconfig has no runtime control flow. It contributes compile-time symbols that drive object inclusion in the adjacent Makefile and preprocessor/runtime feature availability elsewhere in the driver.

## State And Persistence Behavior

The file contributes kernel configuration state. Selected symbols persist in the kernel build configuration and module composition, not in runtime driver state.

## Dependencies And Integration Points

The options integrate mlx5 with PCI, devlink, auxiliary bus, netdev, RFS, switchdev, bridge, TC, netfilter flow table, MACsec, XFRM/IPsec, kTLS, software/hardware steering, subfunction auxiliary devices, DPLL, page pool, DIM, DCB, HWMON, Hyper-V, and PTP subsystems. The dependency expressions also protect invalid built-in/module combinations such as TLS built as a module while mlx5 core is built in.

## Risks

- Feature gates are highly cross-dependent; weakening dependencies can create link errors or runtime feature exposure without required subsystems.
- Defaults of `y` for several offload features can increase module surface area unexpectedly when dependencies are enabled.
- Hidden bools such as `MLX5_BRIDGE` and `MLX5_SF_MANAGER` are selected through dependency/default logic and may be overlooked in build matrix testing.

## Test Signals

Important signals are allmodconfig/allyesconfig/allnoconfig builds, representative modular builds, and targeted configs for switchdev, TC CT/sample, IPsec/TLS/MACsec/PSP, SF, FPGA, DPLL, HWMON, Hyper-V, and PTP combinations. Kconfig warnings and unresolved symbol/link failures are the primary validation outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/Makefile

## Purpose

This Makefile maps mlx5 Kconfig symbols to the object files that compose `mlx5_core.o` and the separate `mlx5_dpll.o` module. It is the build manifest for the mlx5 core, Ethernet datapath, TC/offload stack, steering implementations, accelerators, subfunctions, diagnostics, and support libraries.

## Important Build Groups

- Base `mlx5_core-y`: core probe, command interface, debugfs, firmware, EQ, UAR, page allocation, health, MCG, CQ, allocation, port, MR/PD, transport objects, vport, SR-IOV, flow steering, IRQ, counters, rate limiting, lag, devlink, diagnostics, reset, QoS, timeout, ASO, write-combining, and support libraries.
- `CONFIG_MLX5_CORE_EN`: Ethernet channels, RX/TX, XDP, stats, selftests, reporters, params, XSK, devlink, PTP, QoS, traps, selected queues, and congestion event support.
- `CONFIG_MLX5_CLS_ACT`: TC classifier/action implementation, representor TC, tunneling offloads, post actions, meters, action stats, and individual TC action handlers.
- `CONFIG_MLX5_ESWITCH`: e-switch core/offloads, ECPF, RDMA hooks, legacy mode, vport tables, QoS, IPsec, and ACL helpers.
- `CONFIG_MLX5_SW_STEERING` and `CONFIG_MLX5_HW_STEERING`: separate software and hardware steering object sets.
- Optional accelerators: FPGA, MACsec, IPsec, TLS, PSP.
- Optional support: HWMON, MPFS, VXLAN, PTP clock, Hyper-V, IPoIB, bridge offloads, SF/SF manager, PCIe TPH.
- `obj-$(CONFIG_MLX5_DPLL)` builds `mlx5_dpll.o` from `dpll.o`.

## Control Flow

The file is declarative build control. Kbuild appends object files to `mlx5_core-y` or `mlx5_core-$(CONFIG_*)` depending on configuration symbols. Conditional `ifneq` blocks handle symbols where non-empty values include built-in or module states.

## State And Persistence Behavior

There is no runtime state. The persistent effect is the compiled module layout and which translation units are linked into `mlx5_core.o` or `mlx5_dpll.o`.

## Dependencies And Integration Points

The Makefile consumes symbols from `Kconfig`, adds `-I$(src)` include scope, and integrates many subdirectories: `en/`, `en/tc/`, `esw/`, `lag/`, `lib/`, `diag/`, `steering/sws/`, `steering/hws/`, `sf/`, `fpga/`, `ipoib/`, and `en_accel/`. Its organization mirrors feature ownership and is the final authority on which source files participate in each feature.

## Risks

- Object inclusion must match Kconfig dependencies; adding source files under the wrong symbol can cause unresolved references or dead feature code.
- `ifneq ($(CONFIG_*),)` includes objects for both `y` and `m`; this is deliberate but easy to misuse when code assumes built-in-only behavior.
- Large feature groups can hide accidental cross-feature dependencies because many objects are linked together whenever `MLX5_CORE_EN` or `MLX5_ESWITCH` is enabled.

## Test Signals

Build matrix coverage is the main signal: core-only, Ethernet-only, switchdev/e-switch, TC CT/sample, software steering only, hardware steering only, crypto accelerators, SF, FPGA, IPoIB, DPLL, and modular vs built-in combinations. Link errors and missing object references identify mismatches between Kconfig and Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/alloc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/alloc.c

## Purpose

`alloc.c` provides mlx5 core memory allocation utilities for DMA-backed fragmented buffers and doorbell records. These helpers are used by queues and firmware object setup code that need page arrays, DMA addresses, and compact doorbell slots.

## Important APIs, Types, And Functions

- `struct mlx5_db_pgdir`: one DMA-coherent doorbell page, bitmap of free cache-line slots, and list node.
- `mlx5_frag_buf_alloc_node()` / `mlx5_frag_buf_free()`: allocate and free page-sized DMA coherent fragments for a logical buffer.
- `mlx5_db_alloc_node()` / `mlx5_db_free()`: allocate and free a doorbell record from a shared doorbell page.
- `mlx5_fill_page_frag_array_perm()` / `mlx5_fill_page_frag_array()`: fill firmware physical address arrays from fragment DMA mappings, optionally ORing low permission bits.
- `mlx5_dma_zalloc_coherent_node()`: temporarily sets the DMA device's NUMA node under `alloc_mutex` before `dma_alloc_coherent()`.

## Control Flow

Fragment buffer allocation computes `npages`, allocates a `mlx5_buf_list` array, then allocates each DMA-coherent fragment on the requested NUMA node. It validates DMA alignment against `page_shift`. Failure unwinds already allocated fragments and the array.

Doorbell allocation locks `dev->priv.pgdir_mutex`, scans existing page directories for a free bit, and if none exists allocates a new `mlx5_db_pgdir`. A free cache-line slot is cleared in the bitmap, `db->db` and `db->dma` are set to the slot, and the first two doorbell words are zeroed. Freeing sets the bit and destroys the entire page directory when all slots are free.

## State And Persistence Behavior

Runtime state is held in `dev->priv.pgdir_list`, each page directory's bitmap, and `struct mlx5_db` handles returned to callers. Fragment buffers hold their own `size`, `npages`, `page_shift`, and fragment list. No state persists across device teardown.

## Dependencies And Integration Points

The file depends on Linux DMA coherent allocation, NUMA node assignment, bitmaps, `cache_line_size()`, mlx5 DMA-device selection through `mlx5_core_dma_dev()`, and driver-private mutexes. Firmware-facing callers use the page arrays produced by `mlx5_fill_page_frag_array*()` in command inboxes.

## Risks

- `mlx5_dma_zalloc_coherent_node()` mutates the device node temporarily; the `alloc_mutex` must protect every such allocation path.
- Doorbell slots are cache-line-sized; wrong cacheline assumptions or double frees corrupt the bitmap/page lifetime.
- Fragment allocation frees failed fragments with `PAGE_SIZE`, while the last allocated fragment may be smaller only after success paths; alignment with the loop's `frag_sz` behavior should be preserved if changed.
- `WARN_ON(perm & 0xfc)` implies only low two permission bits are expected; callers passing other bits produce malformed physical address arrays.

## Test Signals

Exercise allocation/free across NUMA nodes, non-page-multiple sizes, injected DMA allocation failures at each fragment, doorbell page exhaustion and full-page release, double-free detection via debug configs, and firmware commands that consume `pas` arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/cmd.c

## Purpose

`cmd.c` implements the mlx5 firmware command interface. It allocates command descriptors and mailbox chains, serializes work through command slots, rings the device command doorbell, handles completions by event or polling, translates delivery and firmware status into Linux errors, exposes debugfs command injection helpers, manages async command contexts, and initializes/disables the command queue.

## Important APIs, Types, And Functions

Command submission and status:

- `mlx5_cmd_do()`: executes a command and returns `-EREMOTEIO` when firmware executed the command but outbox status is non-OK.
- `mlx5_cmd_exec()` and `mlx5_cmd_exec_polling()`: execute and normalize status through `mlx5_cmd_check()`.
- `mlx5_cmd_exec_cb()`: asynchronous command execution with callback and inflight accounting.
- `mlx5_cmd_check()`, `cmd_status_err()`, `cmd_status_to_err()`, `deliv_status_to_err()`: error/status translation.
- `mlx5_cmd_out_err()` and trace helpers log firmware failures.

Command engine:

- `cmd_alloc_ent()`, `cmd_ent_get()`, `cmd_ent_put()`: command work entry lifecycle and slot release.
- `cmd_alloc_index()` / `cmd_free_index()`: command slot bitmap management.
- `cmd_work_handler()`: builds a descriptor, copies mailbox data, schedules timeout work, rings the doorbell, and optionally polls.
- `mlx5_cmd_comp_handler()`: handles real or forced completions, copies output, verifies signatures, runs callbacks, frees messages, and completes waiters.
- `wait_func()` and `wait_func_handle_exec_timeout()`: blocking wait and EQ recovery on timeout.
- `mlx5_cmd_flush()` and `mlx5_cmd_trigger_completions()`: force completion of pending commands during teardown/reset.

Mailbox and caches:

- `mlx5_alloc_cmd_msg()`, `mlx5_free_cmd_msg()`, `alloc_cmd_box()`, `free_cmd_box()`: command message/mailbox chain allocation.
- `mlx5_copy_to_msg()` / `mlx5_copy_from_msg()`: linear buffer to/from command message chains.
- `create_msg_cache()` / `destroy_msg_cache()` and `alloc_msg()`: reusable input-message caches for common sizes.

Initialization and mode:

- `mlx5_cmd_init()` / `mlx5_cmd_cleanup()`: command workqueue and command debugfs scaffolding.
- `mlx5_cmd_enable()` / `mlx5_cmd_disable()`: command interface page, DMA pool, semaphores, caches, debugfs, and firmware queue address.
- `mlx5_cmd_use_events()` / `mlx5_cmd_use_polling()`: switch between EQ completion and polling modes.
- `mlx5_cmd_set_state()`, `mlx5_cmd_is_down()`, and `mlx5_cmd_allowed_opcode()`: state and gating.
- `mlx5_cmd_add_privileged_uid()` / `mlx5_cmd_remove_privileged_uid()`: privileged UID throttling exceptions.

Helper commands:

- `mlx5_cmd_allow_other_vhca_access()`, `mlx5_cmd_alias_obj_create()`, and `mlx5_cmd_alias_obj_destroy()` build specific general-object/access commands on top of the command interface.

## Control Flow

For synchronous commands, `cmd_exec()` checks device state/opcode gating, optionally takes a throttle or unprivileged semaphore, allocates input/output command messages, assigns a token, copies input data, and calls `mlx5_cmd_invoke()`. `mlx5_cmd_invoke()` creates a work entry, queues `cmd_work_handler()` on the command workqueue unless it is the page queue, then waits through `wait_func()`.

`cmd_work_handler()` takes a regular command slot semaphore or the special manage-pages semaphore, allocates an index, fills `struct mlx5_cmd_layout`, sets owner to hardware, calculates signatures if enabled, records timestamps, schedules async timeout work when needed, marks the entry pending completion, and rings `dev->iseg->cmd_dbell`. In polling mode it waits for the owner bit to return to software and directly invokes the completion handler.

Completions arrive through `cmd_comp_notifier()` when event mode is enabled or are forced during timeout/reset. `mlx5_cmd_comp_handler()` walks the completion vector, ignores duplicate/late completions appropriately, cancels async timeout work, copies out the descriptor data, validates signatures, stores delivery status, updates stats, releases command slots, and either calls the async callback or completes the synchronous waiter.

Initialization is split: `mlx5_cmd_init()` creates the workqueue, while `mlx5_cmd_enable()` validates command interface revision, reads queue sizing from the initialization segment, creates semaphores and the DMA pool, allocates an aligned command page, programs its DMA address to the device, initializes caches/debugfs, and starts in polling mode.

## State And Persistence Behavior

Runtime state is held in `dev->cmd`: command mode, command-interface state, slot bitmask, semaphores, workqueue, DMA pool, command descriptor page, entry array, token counter, mailbox caches, debugfs buffers, xarray of privileged UIDs, stats xarray, and notifier. Command state is volatile and rebuilt on device enable. Debugfs `in`, `out`, `out_len`, `status`, and `run` files expose temporary buffers only.

The code tracks stalled entries with `MLX5_CMD_ENT_STATE_PENDING_COMP` and `MLX5_CMD_ENT_STATE_TIMEDOUT`. Timed-out commands can intentionally leak a command resource until a late real completion arrives, avoiding reuse of a slot still owned by firmware.

## Dependencies And Integration Points

The command engine integrates with PCI MMIO (`dev->iseg` doorbell and queue address registers), DMA pools, workqueues, completions, semaphores, xarrays, debugfs, mlx5 EQ notifier infrastructure, timeout policy from `lib/tout`, tracepoints from `diag/cmd_tracepoint.h`, and the wider mlx5 driver through exported command functions. Almost every mlx5 object-management file depends on this interface.

## Risks

- Timeout handling is deliberately complex. Forced completions, late real completions, refcounts, and slot bitmaps must stay balanced to avoid use-after-free, leaked slots, or reusing firmware-owned descriptors.
- Async callbacks cannot sleep and may free their `mlx5_async_work`; the handler correctly avoids touching `work` after user callback, but future edits must preserve that rule.
- `mlx5_cmd_allowed_opcode()` and mode changes drain all semaphores; misuse can block command progress globally.
- Debugfs command injection accepts raw command buffers and should remain restricted to debugfs permissions and trusted users.
- Throttling and privileged UID semaphores protect command queue saturation; bypassing them for high-volume opcodes can stall the device.
- Signature/checksum code is present but `checksum_disabled` is initialized to `1` in this snapshot, so checksum coverage is disabled unless changed elsewhere.

## Test Signals

High-value tests include command success/failure status translation, mailbox sizes crossing cache thresholds, async callback cleanup, forced polling during teardown, event completion mode, timeout/EQ recovery, late completion after timeout, PCI/internal-error state returning synthetic statuses, all-slots-stalled rejection, manage-pages special queue behavior, privileged UID throttling, and debugfs command paths. Lockdep, KASAN/KCSAN, fault injection for DMA/mailbox allocation, and tracepoint/stat checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/cq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/cq.c

## Purpose

`cq.c` manages mlx5 completion queues at the core layer. It creates and destroys firmware CQs, registers them with completion and async EQ lookup trees, handles deferred completion callback processing via tasklets, and exposes query/modify helpers.

## Important APIs, Types, And Functions

- `mlx5_cq_tasklet_cb()`: drains a tasklet process list for a bounded time and invokes CQ completion callbacks.
- `mlx5_add_cq_to_tasklet()`: queues a CQ for tasklet processing while holding a CQ reference.
- `mlx5_create_cq()` / `mlx5_core_create_cq()`: create a firmware CQ, initialize software CQ state, register with EQs, and add debugfs state.
- `mlx5_core_destroy_cq()`: remove debug/EQ registrations, destroy the firmware CQ, synchronize IRQs, drop the final CQ reference, and wait for free completion.
- `mlx5_core_query_cq()`, `mlx5_core_modify_cq()`, and `mlx5_core_modify_cq_moderation()`: firmware query/modify helpers.
- `mlx5_core_cq_dummy_cb()`: default completion callback that logs if callers did not install one.

## Control Flow

Tasklet scheduling avoids duplicate list entries by checking `list_empty_careful()` under the tasklet context lock. The first queued CQ schedules the tasklet. The tasklet splices pending CQs into a process list, invokes each CQ's completion callback, drops the reference acquired during queueing, and reschedules itself if it exceeds the short time budget.

CQ creation obtains the target completion EQ from the command input, sends `CREATE_CQ` through `mlx5_cmd_do()`, initializes CQN, indices, arm sequence, EQ pointer, UID, optional arm doorbell, refcount, completion, callback, and tasklet context, then registers the CQ in both the completion EQ and async EQ trees. If async registration fails it unregisters from the completion EQ and destroys the firmware CQ.

Destroy removes debugfs and both EQ registrations before issuing `DESTROY_CQ`. On success it synchronizes the EQ IRQ, drops the CQ reference, and waits for outstanding tasklet/event users to finish.

## State And Persistence Behavior

CQ software state is held in caller-owned `struct mlx5_core_cq`: CQN, indices, arm state, EQ pointer, UID, refcount, completion, tasklet list node, callback, creator PID, and IRQ number. Firmware owns the actual CQ until destroy. There is no persistence across driver/device teardown.

## Dependencies And Integration Points

The file uses mlx5 command execution, EQ core registration (`mlx5_eq_add_cq()`, `mlx5_eq_del_cq()`), async EQ lookup, debug CQ tracking, Linux tasklets, IRQ synchronization, refcounts, and RDMA/core CQ structures. Upper layers such as netdev and RDMA create CQs through these exported helpers.

## Risks

- Destroy must account for tasklet-held references and late IRQs; removing EQ entries and synchronizing IRQ before waiting is important.
- `mlx5_create_cq()` uses `mlx5_cmd_do()` and leaves outbox status checking to callers on error; `mlx5_core_create_cq()` normalizes with `mlx5_cmd_check()`.
- Tasklet callback time slicing can defer completion handling under heavy CQ load.
- Callers must set `arm_db` for kernel CQs before creation when they expect command sequence initialization.

## Test Signals

Test CQ create/destroy success and failure at each registration step, completion event delivery through tasklet, duplicate queue suppression, destroy while tasklet work is pending, query/modify/moderation commands, and IRQ synchronization under stress. Debugfs CQ entries and refcount completion are useful leak signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/cq.c -->
