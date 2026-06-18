# Research: subset-b-005888 mlx5 public header contracts

This grouped report covers seven source files under `sources/distributed-fs/ceph-client/include/linux/mlx5/`. Each file section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/driver.h -->
# `sources/distributed-fs/ceph-client/include/linux/mlx5/driver.h`

## Purpose

`driver.h` is the central public mlx5 core-driver contract for this Ceph client source tree's vendored Linux mlx5 stack. It exposes the top-level `struct mlx5_core_dev`, core private state, command transport definitions, health/page-allocation/debugfs resources, SR-IOV and LAG helpers, RoCE and MACsec capability gates, UAR/BFREG doorbell allocation types, rate-limiter state, memory-key helpers, notifier registration, and many firmware command entry points. Most implementation lives in mlx5 core, Ethernet, RDMA, LAG, and library `.c` files; this header defines the ABI those modules share inside the kernel tree.

## Important APIs, Types, and Constants

- Device identity and capability constants include `MLX5_ADEV_NAME`, `MLX5_IRQ_EQ_CTRL`, `MLX5_BOARD_ID_LEN`, `MLX5_MAX_PORTS`, register IDs such as `MLX5_REG_PCAP`, `MLX5_REG_MCAM`, and `MLX5_REG_RESOURCE_DUMP`, and capability-related enums for atomics, page-fault resume flags, DCBX mode, debug resource type, port policy, and core device type.
- Command infrastructure centers on `struct mlx5_cmd`, `struct mlx5_cmd_work_ent`, `struct mlx5_cmd_msg`, `struct mlx5_cmd_mailbox`, `struct mlx5_cmd_stats`, `struct mlx5_async_ctx`, and `struct mlx5_async_work`. Public command entry points include `mlx5_cmd_exec()`, `mlx5_cmd_do()`, `mlx5_cmd_check()`, `mlx5_cmd_exec_polling()`, `mlx5_cmd_exec_cb()`, `mlx5_cmd_use_events()`, `mlx5_cmd_use_polling()`, `mlx5_cmd_is_down()`, and the typed-size helper macros `mlx5_cmd_exec_inout()` and `mlx5_cmd_exec_in()`.
- `struct mlx5_core_dev` is the primary persistent device object. It holds Linux device and PCI pointers, PCI and interface state locks, firmware capabilities, command state, init segment mapping, `struct mlx5_priv`, device profile, mlx5e shared resources, RoCE/MACsec/IPsec state, clock/tracer/resource-dump handles, devlink pointer, write-combining state, and optional FPGA/SF/MACsec fields behind configuration guards.
- `struct mlx5_priv` aggregates submodule state: IRQ/EQ tables, page allocator counters and xarray, health reporter state, debugfs dentries, auxiliary devices, event dispatchers, flow steering, MPFS, eswitch, SR-IOV context, LAG, devcom, firmware reset, RoCE flow table objects, flow counter stats, rate-limit table, flow-table pool, BFREG allocators, and optional SF manager notifiers.
- Memory and queue helpers include `struct mlx5_frag_buf`, `struct mlx5_frag_buf_ctrl`, `mlx5_frag_buf_alloc_node()`, `mlx5_frag_buf_free()`, `mlx5_init_fbc()`, `mlx5_init_fbc_offset()`, `mlx5_frag_buf_get_wqe()`, and `mlx5_frag_buf_get_idx_last_contig_stride()`.
- Doorbell/UAR and BFREG types include `struct mlx5_db`, `struct mlx5_uars_page`, `struct mlx5_bfreg_head`, `struct mlx5_bfreg_data`, `struct mlx5_sq_bfreg`, plus `mlx5_db_alloc_node()`, `mlx5_db_alloc()`, `mlx5_db_free()`, `mlx5_alloc_bfreg()`, `mlx5_free_bfreg()`, `mlx5_get_uars_page()`, and `mlx5_put_uars_page()`.
- Resource-management APIs include memory key, protection domain, PSV, page-allocation, multicast group, register access, debugfs, flow-counter-adjacent, rate-limit, software ICM, TPH steering-tag, and VF get/put helpers.
- Notifier APIs split fast EQ/FW event paths from slow software paths: `mlx5_notifier_register()`, `mlx5_notifier_unregister()`, `mlx5_eq_notifier_register()`, `mlx5_eq_notifier_unregister()`, `mlx5_blocking_notifier_register()`, `mlx5_blocking_notifier_unregister()`, and `mlx5_blocking_notifier_call_chain()`.
- LAG, SR-IOV, multipath, RoCE, MACsec, and write-combining helpers include `mlx5_lag_is_*()`, `mlx5_lag_query_*()`, `mlx5_lag_for_each_peer_mdev`, `mlx5_sriov_blocking_notifier_register()`, `mlx5_core_is_pf()`, `mlx5_core_is_vf()`, `mlx5_core_is_ecpf_esw_manager()`, `mlx5_get_roce_state()`, `mlx5e_is_macsec_device()`, `mlx5_is_macsec_roce_supported()`, and `mlx5_wc_support_get()`.

## Control Flow and Lifetimes

This header does not implement the driver state machine, but it describes the shared lifetimes. A PCI-backed `mlx5_core_dev` is created by core probe code, initialized through command queue setup, firmware capability reads, page allocation, health polling, IRQ/EQ setup, flow steering, auxiliary-device creation, and optional eswitch/LAG/SF/MACsec/RDMA resources. Consumers use inline predicates and exported entry points to gate behavior on capability bits and device type. Teardown must reverse those dependencies: stop health/page workers, destroy flow tables/counters/keys, unregister notifiers, remove auxiliary devices, release BFREG/UAR pages, reclaim pages, and mark interface/PCI state down.

The command flow is represented as a queue of `mlx5_cmd_work_ent` objects. Callers prepare input/output buffers and call `mlx5_cmd_exec*()`. The command layer uses semaphores and bitmasks in `mlx5_cmd.vars`, allocates command slots/tokens under spinlocks, submits via workqueue or polling, completes by event or polling, records stats, and returns firmware status through `mlx5_cmd_check()` and `mlx5_cmd_out_err()`. Async commands hold `mlx5_async_ctx.num_inflight` until `mlx5_cmd_cleanup_async_ctx()` can wait for callbacks to drain.

The fragment-buffer inline flow is simple but fast-path sensitive: initialize `mlx5_frag_buf_ctrl` from page fragments, queue stride and queue size; resolve a WQE index by adding `strides_offset`, selecting the fragment by `log_frag_strides`, and computing the byte offset by `log_stride`. An invalid `log_stride`, `log_sz`, or offset corrupts WQE addressing.

## State and Persistence Behavior

State is in memory and hardware/firmware, not on disk. Persistent-in-runtime fields include capability arrays, command queues, health counters, page-accounting counters, xarrays of pages/statistics/privileged UIDs, notifier chains, flow-steering handles, LAG/eswitch/SR-IOV state, device resource IDs, and debugfs/devlink handles. Locks and concurrency primitives are part of the contract: `pci_status_mutex`, `intf_state_mutex`, spinlocks in command/cache/stat structures, command semaphores, health workqueues/timers, page allocator xarrays, BFREG mutexes, rate-limit mutexes, and blocking notifier heads. Firmware objects created through command APIs persist until matching destroy/dealloc functions are called.

## Dependencies and Integration Points

The header depends on Linux kernel primitives (`pci`, `irq`, `workqueue`, `completion`, `semaphore`, `xarray`, `mempool`, `notifier`, `auxiliary_bus`, `mutex`, devlink, net namespaces) and mlx5 hardware-interface headers (`device.h`, `doorbell.h`, `eq.h`). It is included by mlx5 Ethernet core, RDMA, vDPA, eswitch, LAG, IPsec/MACsec, flow steering, and page/health/command modules. Usage references in this tree show flow-steering callers in `drivers/net/ethernet/mellanox/mlx5/core/*`, RDMA callers in `drivers/infiniband/hw/mlx5/*`, and exported command/LAG/MACsec/EQ symbols bridging between subsystems.

## Risks and Edge Cases

- `struct mlx5_core_dev` and `struct mlx5_priv` are broad shared contracts; layout or semantic changes can silently break many modules.
- Command execution is highly concurrent. Slot, token, semaphore, callback, and timeout handling need strict pairing to avoid command leaks, callback-after-free, or firmware command starvation.
- Hardware capability gates must be checked before optional flows such as RoCE disable, MACsec RoCE, LAG, TPH, SF, eswitch management, and write combining.
- Inline helpers assume non-null device pointers and initialized capability/fragment metadata; misuse is likely to produce low-level memory or hardware failures rather than friendly errors.
- Notifier callbacks may run in atomic or blocking contexts depending on registration path; callback implementations must respect the context.
- Hardware resources such as mkeys, PDs, PSV objects, BFREGs, UARs, flow tables, counters, and software ICM must follow create/destroy pairing, often across error unwind paths.

## Test Signals

Useful validation includes building mlx5 core with `CONFIG_MLX5_CORE`, RDMA, eswitch, LAG, SF, TPH, and MACsec combinations; sparse/smatch checks for pointer and lock misuse; command failure injection and timeout tests; module probe/remove/reload cycles; firmware reset and health reporter tests; SR-IOV PF/VF and ECPF capability tests; RoCE enable/disable and GID table tests; LAG peer iteration and bond speed paths; and hardware or simulator tests that exercise command event mode, polling mode, page allocation, debugfs/devlink visibility, and MACsec RoCE capability gating.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/eq.h -->
# `sources/distributed-fs/ceph-client/include/linux/mlx5/eq.h`

## Purpose

`eq.h` defines the compact public API for mlx5 event queues. Event queues carry firmware and completion events from the HCA to mlx5 core consumers. The header exposes sizing constants, generic EQ create/destroy and enable/disable functions, consumer-index maintenance helpers, and the `mlx5_nb` wrapper used to bind notifier callbacks to a specific firmware event type.

## Important APIs, Types, and Constants

- `MLX5_NUM_CMD_EQE`, `MLX5_NUM_ASYNC_EQE`, and `MLX5_NUM_SPARE_EQE` define command, async, and spare EQ entry sizing expectations.
- `struct mlx5_eq_param` passes the requested entry count, a 256-bit event mask (`mask[4]`), and an IRQ object into generic EQ creation.
- `mlx5_eq_create_generic()` allocates a generic EQ for a device using `mlx5_eq_param`; `mlx5_eq_destroy_generic()` tears it down.
- `mlx5_eq_enable()` registers a notifier and enables event delivery for an EQ; `mlx5_eq_disable()` removes it and disables delivery.
- `mlx5_eq_get_eqe()` returns an event queue entry for a consumer counter, and `mlx5_eq_update_ci()` writes the consumer index back to hardware, optionally arming the queue.
- `mlx5_eq_update_cc()` is an inline IRQ-handler helper that forces periodic CI updates when the local consumed count reaches `MLX5_NUM_SPARE_EQE`.
- `struct mlx5_nb`, `mlx5_nb_cof()`, and `MLX5_NB_INIT()` wrap a `notifier_block` with a concrete `MLX5_EVENT_TYPE_*` selector.

## Control Flow and Lifetimes

Typical flow is allocate an EQ with `mlx5_eq_create_generic()`, enable it with a notifier callback through `mlx5_eq_enable()`, process EQEs in an interrupt path by repeatedly reading entries and calling `mlx5_eq_update_cc()` on every event, and finally call `mlx5_eq_disable()` before destroying the EQ. The inline comment documents a key hardware flow-control rule: because EQs are created with spare entries, software must update hardware's consumer index at least once per spare-entry window or the HCA may treat the queue as overflowed.

## State and Persistence Behavior

The opaque `struct mlx5_eq` owns hardware queue state, DMA memory, producer/consumer indices, and IRQ binding in implementation files. `eq.h` exposes only the caller-owned `mlx5_eq_param` and notifier wrapper. The consumed counter passed through `mlx5_eq_update_cc()` is caller-maintained transient state and resets to zero after a forced CI update.

## Dependencies and Integration Points

The header forward-declares `mlx5_eq`, `mlx5_irq`, and `mlx5_core_dev`, and relies on `notifier_block` and mlx5 event type definitions visible through including context. `driver.h` includes this header and publishes `mlx5_eq_notifier_register()` for broader event dispatch. Usage in this tree includes core EQ implementation under `drivers/net/ethernet/mellanox/mlx5/core/eq.c` and RDMA ODP creating generic EQs for page-fault/event handling.

## Risks and Edge Cases

- Forgetting to call `mlx5_eq_update_cc()` for every EQE can lead to hardware-visible overflow even when software is processing events.
- Notifier callbacks must match the event type initialized by `MLX5_NB_INIT()` and must obey IRQ-context constraints.
- Disable/destroy ordering matters: destroying an enabled EQ risks callbacks racing with freed queue memory.
- The `mask[4]` contract is low-level; wrong bit placement can silently subscribe to the wrong firmware events.

## Test Signals

Validate with mlx5 core EQ creation/destruction paths, interrupt-driven event delivery, RDMA ODP generic EQ setup, command EQ behavior, synthetic event bursts above `MLX5_NUM_SPARE_EQE`, module unload while events are active, and lockdep/IRQ-context checks for notifier callbacks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/eq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/eswitch.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/eswitch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/fs.h -->
# `sources/distributed-fs/ceph-client/include/linux/mlx5/fs.h`

## Purpose

`fs.h` is the public mlx5 flow-steering API. It defines namespaces, table types, table attributes, match specifications, destinations, actions, groups, counters, modify-header/reformat objects, match definers, root namespace handling, and helper constants used by Ethernet, RDMA, vDPA, eswitch, IPsec, MACsec, LAG, and packet-classification paths.

## Important APIs, Types, and Constants

- General constants include `MLX5_FS_DEFAULT_FLOW_TAG`, `MLX5_RDMA_TRANSPORT_BYPASS_PRIO`, `MLX5_FS_MAX_POOL_SIZE`, `LEFTOVERS_RULE_NUM`, `MLX5_FS_VLAN_DEPTH`, and `MLX5_DECLARE_FLOW_ACT()`.
- `enum mlx5_flow_destination_type` covers no destination, vport, flow table, TIR, sampler, uplink, port, counter, flow-table number, range, table type, and VHCA RX.
- Action flags extend firmware flow actions with `MLX5_FLOW_CONTEXT_ACTION_FWD_NEXT_PRIO`, encrypt/decrypt, and forward-next-namespace. Flow-table flags describe tunnel reformat/decap, termination, unmanaged tables, other/uplink vports, and other eswitch ownership.
- `enum mlx5_flow_namespace_type` defines the high-level steering namespaces for NIC RX/TX, MACsec, LAG, offloads, ethtool, kernel, leftovers, FDB, eswitch ingress/egress, sniffer, RDMA RX/TX, port select, counters, IPsec, MACsec, and RDMA transport.
- FDB priority constants such as `FDB_DROP_ROOT`, `FDB_TC_OFFLOAD`, `FDB_BR_OFFLOAD`, and `FDB_SLOW_PATH` define ordering within FDB steering.
- `enum fs_flow_table_type` maps software table classes to firmware op-mod table types: NIC RX/TX, eswitch ACLs, FDB, sniffer, RDMA, port select, FDB RX/TX, and RDMA transport.
- `struct mlx5_flow_context` carries flow tag/source flags; `struct mlx5_flow_spec` carries match criteria enable bits plus match mask/value arrays sized to `fte_match_param`.
- `struct mlx5_flow_destination` is a tagged union for all destination forms, including table pointers/numbers, TIR, counters, vport fields with VHCA ID and packet reformat, range hit/miss tables, sampler ID, and VHCA RX ID.
- `struct mlx5_flow_table_attr` defines priority, maximum FTEs, level, flags, UID, vport, eswitch owner VHCA ID, optional next table, and autogroup sizing/reserved entries.
- Table and group APIs include namespace lookup (`mlx5_get_flow_namespace()`, `mlx5_get_fdb_sub_ns()`, `mlx5_get_flow_vport_namespace()`), table creation variants (`mlx5_create_flow_table()`, `mlx5_create_auto_grouped_flow_table()`, `mlx5_create_vport_flow_table()`, `mlx5_create_lag_demux_flow_table()`), `mlx5_destroy_flow_table()`, `mlx5_create_flow_group()`, and `mlx5_destroy_flow_group()`.
- `struct mlx5_flow_act` combines action bits, modify-header object, packet-reformat object, crypto parameters, flags, VLAN stack, IB counters, selected flow group, and ASO execution data.
- Rule APIs include `mlx5_add_flow_rules()`, `mlx5_del_flow_rules()`, and `mlx5_modify_rule_destination()`.
- Counter APIs include `mlx5_fc_create()`, local counter create/destroy/get/put, cached and raw query helpers, synchronous query, ID lookup, and last-use query.
- Object APIs include RX underlay QPN add/remove, modify-header alloc/dealloc, match definer create/destroy/ID lookup, packet reformat alloc/dealloc, `mlx5_flow_table_id()`, root namespace lookup, and `mlx5_fs_set_root_dev()`.

## Control Flow and Lifetimes

The normal flow-steering lifecycle is: get a namespace, create a flow table with attributes, optionally create flow groups from firmware inbox criteria, allocate supporting objects such as counters, modify headers, packet reformat objects, definers, or crypto objects, then add rules with a match spec, action, and destination array. `mlx5_add_flow_rules()` returns an opaque handle that must be deleted with `mlx5_del_flow_rules()`. Tables and groups must be destroyed after all dependent rules are removed. Counter objects and packet transformation objects have their own create/destroy or get/put lifetimes.

Autogrouped tables move group selection into flow-steering internals using `ft_attr.autogroup`, while explicit groups require caller-provided firmware inbox data containing start/end flow indexes and match criteria. Forwarding can target next priority/namespace, explicit destination tables, vports, uplink, TIRs, counters, ranges, or no destination for drop/terminal/action-only rules depending on action bits and namespace semantics.

## State and Persistence Behavior

Most objects are opaque handles backed by firmware resources and flow-steering software state: namespaces, tables, groups, rules, counters, modify headers, match definers, and packet reformats. They persist until explicit destruction. `struct mlx5_flow_spec`, `struct mlx5_flow_act`, and `struct mlx5_flow_destination` are caller-owned setup descriptors. Counters can have cached state (`mlx5_fc_query_cached*()` and last-use data), local reference state, and synchronous firmware query state.

## Dependencies and Integration Points

The header depends on `driver.h` and `mlx5_ifc.h` for device, firmware structure sizes, and action constants. It is heavily used by mlx5 Ethernet receive/transmit steering, TC offloads, eswitch ACL/bridge/offload tables, MACsec and IPsec crypto steering, RDMA and RDMA transport steering, LAG demux, vDPA multicast/unicast filters, ethtool flow rules, accelerated RFS, and root namespace ownership transitions. `lag.h` uses `mlx5_flow_table_attr`; `eswitch.h` returns `mlx5_flow_handle` objects created through this API.

## Risks and Edge Cases

- Match masks and values are raw firmware-layout arrays; wrong `match_criteria_enable`, mask width, or field packing can make rules too broad, too narrow, or invalid.
- Destination union fields must match `type`; misuse can pass table IDs where pointers or vport metadata are expected.
- Rule/table/group/object destruction ordering is critical. Rules generally must be removed before groups, groups before tables, and actions/counters/reformat objects after dependent rules are gone.
- Multi-destination, crypto, modify-header, VLAN, ASO, and range flows combine several subsystems and need capability checks in callers.
- Flow levels/priorities and FDB priority constants affect packet path ordering. Incorrect levels can shadow security, MACsec/IPsec, bridge, TC, or slow-path rules.
- Counter cached queries may lag hardware state; callers needing exact packet/byte values must use synchronous query paths.

## Test Signals

Validation should include compile coverage for all mlx5 users, create/add/delete/destroy cycles under error unwinds, flow rule matching tests for NIC RX/TX, FDB, eswitch ACL, RDMA RX/TX, RDMA transport, LAG demux, IPsec/MACsec crypto paths, counter query tests including cached and synchronous modes, modify-header/reformat allocation failures, namespace root-device changes, and hardware traffic tests verifying priority ordering and destination behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/fs_helpers.h -->
# `sources/distributed-fs/ceph-client/include/linux/mlx5/fs_helpers.h`

## Purpose

`fs_helpers.h` provides inline helpers for identifying whether a flow-steering match specification represents an outer IPv4 or IPv6 flow. It abstracts the difference between newer devices that support matching on an explicit outer IP version field and older devices that require ethertype matching.

## Important APIs, Types, and Constants

- `MLX5_FS_IPV4_VERSION` and `MLX5_FS_IPV6_VERSION` define the expected IP version nibble values.
- `_mlx5_fs_is_outer_ipv_flow()` is the common helper. It receives an `mlx5_core_dev`, match criteria array, match value array, and target version.
- `mlx5_fs_is_outer_ipv4_flow()` and `mlx5_fs_is_outer_ipv6_flow()` are the public inline wrappers for IPv4 and IPv6.

## Control Flow and Lifetimes

The helper first checks `MLX5_CAP_FLOWTABLE_NIC_RX(mdev, ft_field_support.outer_ip_version)`. If the device does not support explicit outer IP version matching, it maps the requested version to `ETH_P_IP` or `ETH_P_IPV6` and verifies that the ethertype mask is exact (`0xffff`) and the ethertype value matches. If explicit IP-version matching is supported, it verifies that the `ip_version` mask is exact (`0xf`) and the match value is the requested version. Unsupported version input returns false.

The function reads from caller-owned match arrays only; it allocates and persists no state.

## State and Persistence Behavior

There is no persistent state. The observable behavior depends on the device's flow-table capability bits and the contents of `match_c` and `match_v`, which are expected to be firmware-layout `fte_match_param` arrays.

## Dependencies and Integration Points

The helper depends on `mlx5_ifc.h` layout macros (`MLX5_ADDR_OF`, `MLX5_GET`) and flow-table capability macros from the mlx5 include environment. It integrates with flow-steering users that need to classify or validate specs before installing rules, especially code that must work across devices with different field support.

## Risks and Edge Cases

- The function assumes `match_c` and `match_v` point to valid `fte_match_param` buffers; no null or bounds checks are present.
- For older devices, flows that match IP version indirectly through other fields but do not have an exact ethertype mask will return false.
- For newer devices, exact `ip_version` mask/value is required; partial masks intentionally do not count as IPv4/IPv6 identification.
- The capability check is NIC RX-specific. Callers applying it to other table types must confirm the capability is meaningful for their path.

## Test Signals

Unit-style validation can construct match arrays for IPv4 and IPv6 using both ethertype and explicit `ip_version` fields, toggle mocked capability values, and verify false results for unsupported versions, partial masks, wrong values, and zero masks. Integration coverage should include flow-steering callers on devices with and without `outer_ip_version` support.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/fs_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/lag.h -->
# `sources/distributed-fs/ceph-client/include/linux/mlx5/lag.h`

## Purpose

`lag.h` exposes the public mlx5 LAG demultiplexing API. It lets consumers initialize and clean up a LAG demux flow table, add and delete per-vport demux rules, and query the device sequence used to identify the local device position in a LAG setup.

## Important APIs, Types, and Constants

- The header forward-declares `struct mlx5_core_dev`, `struct mlx5_flow_table`, and `struct mlx5_flow_table_attr`.
- `mlx5_lag_demux_init()` initializes LAG demux resources for a device using flow table attributes.
- `mlx5_lag_demux_cleanup()` releases those resources.
- `mlx5_lag_demux_rule_add()` installs a rule mapping a vport number to a vport index.
- `mlx5_lag_demux_rule_del()` removes a demux rule by vport index.
- `mlx5_lag_get_dev_seq()` returns a device sequence/index value for the current mlx5 device.

## Control Flow and Lifetimes

Callers initialize demux resources before loading representor or RDMA paths that need vport demultiplexing. After initialization, they add rules for vports as representors are loaded or peer paths become active, and delete those rules before the vport/representor disappears. Cleanup destroys the demux flow table and supporting firmware state after all rules have been removed. Usage references show RDMA main initialization calling `mlx5_lag_demux_init()`/cleanup and IB representor load/unload adding/deleting demux rules.

## State and Persistence Behavior

The header exposes no structs, but implementation state includes a LAG demux flow table and per-vport rule handles stored in mlx5 LAG private state. Rules persist in hardware flow steering until deleted or cleanup occurs. `vport_index` is the stable key used for deletion.

## Dependencies and Integration Points

The API depends on `mlx5_core_dev` and flow-steering table attributes from `fs.h`. Implementation references in this tree live under `drivers/net/ethernet/mellanox/mlx5/core/lag/lag.c`, with additional internal declarations in the LAG core header. It integrates with RDMA representors (`drivers/infiniband/hw/mlx5/ib_rep.c`) and RDMA device startup (`drivers/infiniband/hw/mlx5/main.c`), and it uses flow tables created through the mlx5 flow-steering API.

## Risks and Edge Cases

- Add/delete pairing is index-based. Reusing or miscomputing `vport_index` can remove the wrong rule or leak a rule.
- Demux initialization may choose firmware or flow-table paths depending on capabilities in implementation; callers must not assume a specific backend.
- Cleanup while rules are active risks dangling handles or traffic steering loss.
- LAG state is topology-sensitive; tests must cover active/inactive LAG, representor reload, and multiport cases.

## Test Signals

Validate RDMA startup/shutdown with LAG enabled, representor load/unload rule add/delete, error unwind after partial rule creation, active bond changes, multiport device sequence values from `mlx5_lag_get_dev_seq()`, and builds against the 2026 NVIDIA LAG API header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/lag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/macsec.h -->
# `sources/distributed-fs/ceph-client/include/linux/mlx5/macsec.h`

## Purpose

`macsec.h` exposes the mlx5 MACsec-to-RoCE flow-steering bridge when `CONFIG_MLX5_MACSEC` is enabled. It lets MACsec events and RoCE GID updates install or remove MACsec-aware RoCE steering rules for transmit and receive security associations.

## Important APIs, Types, and Constants

- `struct mlx5_macsec_event_data` carries MACsec event context: MACsec flow-steering object pointer, MACsec netdev/private pointer, flow-steering ID, and direction flag.
- `mlx5_macsec_add_roce_rule()` installs RoCE MACsec rules for a MACsec device/address/GID index pair and records transmit and receive rules in caller-provided lists.
- `mlx5_macsec_del_roce_rule()` removes the rules for a GID index from the MACsec flow-steering context and rule lists.
- `mlx5_macsec_add_roce_sa_rules()` installs rules for a specific security-association flow-steering ID and direction.
- `mlx5_macsec_del_roce_sa_rules()` removes rules for a specific security-association flow-steering ID and direction.
- All declarations are compiled only under `CONFIG_MLX5_MACSEC`; there are no non-MACsec stubs in this header.

## Control Flow and Lifetimes

MACsec and RoCE integration starts from capability gating in `driver.h`, where `mlx5_is_macsec_roce_supported()` requires NIC-to-RDMA flow-table capabilities, MACsec device support, and `mdev->macsec_fs`. When a RoCE GID or MACsec SA appears, callers provide the MACsec device pointer, sockaddr, GID index, rule lists, and MACsec flow-steering context to add TX/RX rules. SA-specific add/delete functions update one direction based on `is_tx`. Deletion must remove rules from the same lists and flow-steering context before the GID, SA, MACsec device, or `mlx5_macsec_fs` object is destroyed.

## State and Persistence Behavior

The header exposes event context only. Persistent state is stored in `struct mlx5_macsec_fs` implementation objects and in caller-owned `tx_rules_list` and `rx_rules_list`. Added rules are hardware/software flow-steering handles that persist until corresponding delete functions run.

## Dependencies and Integration Points

The API depends on kernel socket address types, list heads, `struct mlx5_macsec_fs`, and MACsec configuration. Implementation references in this tree include `drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.c`, while RDMA integration calls are visible in `drivers/infiniband/hw/mlx5/macsec.c`. It integrates with flow-steering APIs from `fs.h`, device capability checks from `driver.h`, and MACsec notifier chains stored in `struct mlx5_core_dev` when MACsec is configured.

## Risks and Edge Cases

- No declarations are available without `CONFIG_MLX5_MACSEC`; callers must guard all use.
- Rule list ownership is external. Add/delete mismatches, wrong GID index, or wrong `is_tx` direction can leak rules or remove the wrong SA rules.
- The API uses `void *macdev`, so type safety is delegated to implementation and callers.
- MACsec RoCE depends on multiple capabilities and `mdev->macsec_fs`; bypassing the capability gate can fail late or program unsupported steering paths.
- Address family handling is hidden in implementation; callers should pass sockaddr values that match RoCE GID semantics.

## Test Signals

Validate builds with and without `CONFIG_MLX5_MACSEC`, MACsec RoCE capability gating, RoCE GID add/delete while MACsec is active, TX and RX SA add/delete, rule-list cleanup on error paths, MACsec device teardown before/after RoCE cleanup, and traffic tests verifying encrypted RoCE steering in both directions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mlx5/macsec.h -->
