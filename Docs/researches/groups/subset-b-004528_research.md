# Research: subset-b-004528

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/main.c

## Purpose

`main.c` is the core PCI, firmware, resource, devlink, SR-IOV, and lifecycle driver for Mellanox ConnectX mlx4 HCAs. It owns module parameters, PCI probe/remove, firmware boot, HCA context-memory setup, master/slave multifunction negotiation, port type switching, devlink reload, PCI error recovery, suspend/resume, default counter allocation, interrupt vector selection, and the handoff to mlx4 auxiliary/upper drivers. It is the central state machine that turns a `pci_dev` into a fully registered `mlx4_dev`.

## Important APIs, Types, And Functions

Module and devlink configuration is exposed through `msi_x`, `num_vfs`, `probe_vf`, `log_num_mgm_entry_size`, `enable_64b_cqe_eqe`, `enable_4k_uar`, `log_num_mac`, `log_num_vlan`, `log_mtts_per_seg`, and `port_type_array`. `mlx4_devlink_params` maps some of those knobs to devlink driverinit/runtime parameters, including internal-error reset, max MACs, crash-dump snapshots, 64-byte CQE/EQE enablement, and 4K UAR mode. `mlx4_devlink_param_load_driverinit_values()` applies driverinit devlink values during reload.

Firmware and capability setup is split across `mlx4_init_fw()`, `mlx4_load_fw()`, `mlx4_dev_cap()`, `mlx4_init_hca()`, `mlx4_init_icm()`, and `mlx4_setup_hca()`. `mlx4_dev_cap()` translates firmware capability fields into `dev->caps`, selects port defaults, bounds MAC/VLAN table sizes, handles CQE/EQE stride policy, stores physical port capability data, chooses reserved QP ranges, and disables unsupported combinations such as timestamping in slave mode. `choose_steering_mode()` chooses A0, B0, or device-managed flow steering and sets `dev->oper_log_mgm_entry_size` plus `dev->caps.num_qp_per_mgm`; `choose_tunnel_offload_mode()` enables VXLAN tunnel offload only when DMFS and firmware flags allow it.

PCI lifecycle is driven by `mlx4_init_one()`, `__mlx4_init_one()`, `mlx4_load_one()`, `mlx4_unload_one()`, and `mlx4_remove_one()`. The registered `pci_driver` also installs `mlx4_shutdown()`, `mlx4_suspend()`, `mlx4_resume()`, and AER handlers `mlx4_pci_err_detected()`, `mlx4_pci_slot_reset()`, and `mlx4_pci_resume()`. Devlink reload delegates to `mlx4_restart_one_down()` and `mlx4_restart_one_up()`.

Port and HA management centers on `mlx4_check_port_params()`, `mlx4_change_port_types()`, sysfs handlers for `mlx4_portN` and `mlx4_portN_mtu`, devlink port ops, `mlx4_bond()`, `mlx4_unbond()`, `mlx4_mf_bond()`, `mlx4_mf_unbond()`, and async `mlx4_queue_bond_work()`. Exported helper APIs include `mlx4_get_parav_qkey()`, `mlx4_sync_pkey_table()`, slave GUID helpers, `mlx4_is_slave_active()`, `mlx4_handle_eth_header_mcast_prio()`, `mlx4_read_clock()`, `mlx4_get_internal_clock_params()`, counter allocation/free helpers, and admin GUID helpers.

## Control Flow

Module init validates parameters in `mlx4_verify_params()`, creates the global single-threaded `mlx4_wq`, and registers the PCI driver. Probe allocates a devlink-backed `mlx4_priv`, creates persistent state, registers devlink parameters, enables the PCI device, requests BARs, sets DMA masks, initializes crash dump and catastrophic-error support, then calls `mlx4_load_one()`.

`mlx4_load_one()` initializes auxiliary-device support and core locks, detects PF versus VF, claims PF ownership, resets PF hardware, initializes the command interface, and enters either master, slave, or native flow. Slave mode initializes the multifunction communication channel and asks the PF for caps. Master mode may query device caps, enable SR-IOV through `mlx4_enable_sriov()`, reset, and restart command setup so firmware-visible resources match VF layout. After firmware/HCA init it initializes master multifunction resources, allocates EQ tables, chooses MSI-X or INTx, initializes software steering lists for PF/native devices, initializes quotas, calls `mlx4_setup_hca()`, arms the master communication channel, creates per-port devlink/sysfs state, registers the mlx4 device, starts link sensing, and clears the `pf_loading` probe-defer gate.

`mlx4_setup_hca()` has a strict resource ladder: UAR table and driver UAR, kernel access region mapping, PD/XRCD/MR tables, MCG table and MAD demux for non-slaves, EQ table, event-driven command mode and NOP interrupt test, CQ/SRQ/QP tables, counters, default counters, IB port default capabilities, and `SET_PORT`. Every failure path unwinds in reverse and switches commands back to polling before tearing down EQs.

Unload and error recovery reverse the same hierarchy. `mlx4_unload_one()` saves current port types, stops sensing, unregisters upper consumers, closes ports, frees resource trackers, default counters, QP/SRQ/CQ/EQ/MCG/MR/XRCD/PD/UAR resources, clears steering, disables MSI-X, releases ownership, destroys slave special-QP caps, frees VF metadata, cleans auxiliary devices, and preserves persistent fields through `mlx4_clean_dev()`. AER and suspend paths mark device state, unload under devlink/interface locks, and later reload through `mlx4_load_one()` with saved VF and port state.

## State And Persistence Behavior

The most important persistent anchor is `struct mlx4_dev_persistent`, stored in PCI drvdata. It survives `mlx4_clean_dev()` across reload/reset flows and carries the PCI device pointer, interface and PCI status mutexes, `num_vfs`, per-port VF distribution, saved current/possible port types, crash-dump state, and device state flags. `struct mlx4_priv` is zeroed during clean reloads, then rebuilt around that persistent pointer.

Runtime state is distributed across `dev->caps`, `dev->phys_caps`, `dev->quotas`, `dev->flags`, `dev->dev_vfs`, and many tables inside `mlx4_priv`: command context, firmware memory, UAR/MR/CQ/EQ/SRQ/QP/MCG tables, counters bitmap, port info, steering lists, bond map, slave state, and resource tracker. Port type changes persist for restart through `persist->curr_port_type` and `persist->curr_port_poss_type`. SR-IOV intent persists in `persist->num_vfs` and `persist->nvfs`; actual VF metadata is allocated per load. Devlink driverinit values persist in devlink until reload and are copied back into module-level globals before reload-up.

Synchronization is explicit: devlink lock guards load/unload/reload paths; `interface_state_mutex`, `device_state_mutex`, and `pci_status_mutex` guard persistent status; `port_mutex` guards port type and MTU reconfiguration; `bond_mutex` guards bond/remap state; `cmd.slave_cmd_mutex` serializes VF communication setup; `pf_loading` defers VF probe while the PF is enabling SR-IOV; table-specific locks protect resource allocators.

## Dependencies And Integration Points

The file depends on Linux PCI, DMA, devlink, sysfs, workqueue, MSI-X, PM, AER, RDMA core headers, and mlx4 internal modules (`fw.h`, `icm.h`, command wrappers, table allocators, resource tracker, sense, port, EQ/CQ/QP/SRQ/MR/UAR code). It exports symbols consumed by mlx4 Ethernet, mlx4 InfiniBand, virtualization, and auxiliary-device paths. It integrates with firmware through commands such as `QUERY_FW`, `MAP_FA`, `RUN_FW`, `QUERY_DEV_CAP`, `INIT_HCA`, `QUERY_HCA`, `SET_PORT`, `QUERY_ADAPTER`, `ALLOC_RES`, and `FREE_RES`. It integrates with userspace through module parameters, devlink params/reload/ports, sysfs port attributes, PCI device IDs, and ethtool-visible counter allocation used by upper drivers.

## Risks

The riskiest area is lifecycle unwinding: `mlx4_load_one()` and `mlx4_setup_hca()` have many partially initialized stages and mode-specific cleanup paths. Regressions commonly show as leaked ICM memory, stale MSI-X vectors, double cleanup of steering/counters, or a device left in command-event mode after a failed NOP. SR-IOV transitions are also fragile because PF reset, firmware caps, `pf_loading`, existing VFs, and slave probe deferral must align. Port type changes unregister and re-register upper devices, so they can race with userspace, link sensing, and reload unless locks are held consistently. Timestamp mapping and BlueFlame mapping depend on BAR offsets and firmware caps. Devlink driverinit values mutate module globals at reload time, so validation must catch invalid combinations before hardware reinit.

## Test Signals

Useful signals include successful probe/remove across PF, VF, and no-SR-IOV modes; devlink reload with changed `max_macs`, `enable_64b_cqe_eqe`, `enable_4k_uar`, and crash-dump settings; sysfs/devlink port type switching between IB/ETH/auto; suspend/resume and PCI AER reset recovery; MSI-X fallback after a failed NOP interrupt test; counter allocation/free under native and multifunction modes; low-memory/kdump profile boot; active VF removal warnings; and leak/error-path testing that forces failures at each table initialization stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mcg.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4.h

## Purpose

`mlx4.h` is the private core header for the mlx4 driver. It defines the internal constants, firmware context layouts, command virtualization structures, resource trackers, hardware tables, per-device private state, and cross-file prototypes used by `main.c`, command handling, resource allocators, port code, EQ/CQ/QP/SRQ/MR/UAR code, multicast steering, and multifunction PF/VF support. It is the shared contract for the mlx4 core implementation rather than a public userspace ABI.

## Important APIs, Types, And Functions

Important constants include HCR/communication/clock BAR offsets, MGM entry sizing bounds, command cleanup masks, resource types, allocation modes, QP zone flags, `MGM_QPN_MASK`, `MGM_BLCK_LB_BIT`, VLAN/MAC table sizes, and `MLX4_MAX_NUM_SLAVES`. Firmware-facing packed or endian-aware structures include `mlx4_vhcr`, `mlx4_vhcr_cmd`, `mlx4_mpt_entry`, `mlx4_eq_context`, `mlx4_cq_context`, `mlx4_srq_context`, `mlx4_mgm`, `mlx4_set_port_general_context`, and `mlx4_set_port_rqp_calc_context`.

Core runtime tables include `mlx4_bitmap`, `mlx4_buddy`, `mlx4_icm_table`, `mlx4_uar_table`, `mlx4_mr_table`, `mlx4_cq_table`, `mlx4_eq_table`, `mlx4_srq_table`, `mlx4_qp_table`, and `mlx4_mcg_table`. Multifunction state is modeled by `mlx4_slave_state`, `mlx4_vport_state`, admin/oper VF state arrays, `mlx4_resource_tracker`, `mlx4_mfunc_master_ctx`, and `mlx4_mfunc`. Per-port state is in `mlx4_port_info`, `mlx4_sense`, `mlx4_mac_table`, `mlx4_vlan_table`, and `mlx4_roce_gid_table`. `struct mlx4_priv` embeds the public `struct mlx4_dev` and all private tables, locks, firmware mappings, steering lists, bond map, and work items.

The header declares the internal API surface for bitmap and zone allocation, table init/cleanup, resource wrappers, command setup/cleanup, event dispatch, port sensing, MAC/VLAN/GID operations, resource tracker operations, QP attach/promisc wrappers, MCG sizing helpers, bonding, quotas, and auxiliary-device registration.

## Control Flow Role

This header does not execute control flow directly, but it shapes most mlx4 flows. `main.c` allocates `struct mlx4_priv`, fills `dev->caps`, initializes the table structs declared here, and calls the declared init/cleanup routines in strict order. `mcg.c` uses `mlx4_mcg_table`, `mlx4_mgm`, `mlx4_steer`, and promisc list types to mutate legacy multicast and steering state. Command handling uses `mlx4_cmd`, `mlx4_cmd_info`, VHCR structs, cleanup masks, and wrapper prototypes to route PF and VF commands. Resource tracking uses the enum resource IDs and per-slave lists to reserve, map, and free objects under SR-IOV.

## State And Persistence Behavior

Most structs declared here represent in-kernel runtime state, not persistent storage. Persistent reload state is referenced through `struct mlx4_dev::persist` but the private tables in `mlx4_priv` are rebuilt after reset. Several fields mirror hardware state and must be kept synchronized: ICM table mappings, bitmaps for allocatable objects, MCG and promisc steering lists, MAC/VLAN/GID tables, EQ/CQ/SRQ/QP radix trees, and resource tracker trees. Locking primitives are embedded next to their state: mutexes for port, bond, MCG, MAC/VLAN/GID, command and page-directory paths; spinlocks for bitmap/resource/event fast paths; rwsem/semaphore fields for command execution.

## Dependencies And Integration Points

The header depends on Linux mutex, radix tree, rb tree, timers, semaphores, workqueues, interrupts, spinlocks, rwsems, auxiliary bus, notifier chains, devlink, and public mlx4 device/driver/doorbell/cmd headers. It is included by core implementation files and is tightly coupled to firmware command definitions and public `linux/mlx4/*` device types. Upper mlx4 Ethernet and InfiniBand modules indirectly depend on these declarations through exported core symbols, but external consumers should use public mlx4 headers where possible.

## Risks

Because this header defines shared firmware layouts, structure packing, endianness, and table sizes, small changes can break hardware command ABI. `struct mlx4_priv` is zeroed wholesale by reload code while preserving only selected persistent fields, so adding fields that require special preservation needs explicit lifecycle review. The command wrapper prototype surface is broad; mismatched semantics for wrapped VF commands can cause privilege or resource-accounting bugs. Several arrays are indexed by one-based ports or slave IDs, so bounds assumptions must be maintained consistently. Changes to constants such as MGM entry size, MAC/VLAN table size, or cleanup masks can affect multiple initialization and unwind paths.

## Test Signals

Header changes should be validated by full mlx4 core builds with `CONFIG_MLX4_CORE`, `CONFIG_MLX4_EN`, `CONFIG_MLX4_INFINIBAND`, SR-IOV, DCB, and RFS combinations. Runtime signals include successful PF/VF probe, wrapped command execution, resource allocation/free accounting, port type switching, MCG attach/detach, suspend/resume reload, and AER recovery. Static analysis should check packed firmware structs, endian conversions, array bounds for port/slave indexing, and cleanup coverage for every table declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4_en.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4_en.h

## Purpose

`mlx4_en.h` is the private Ethernet driver header for mlx4. It defines mlx4 Ethernet constants, descriptor and ring structures, CQ/RX/TX state, per-port profiles, device-level Ethernet state, multicast and MAC bookkeeping, DCB/XDP/PTP/statistics integration, and function prototypes shared by the mlx4 Ethernet implementation files. It connects the mlx4 core device API to Linux `net_device`, NAPI, ethtool, XDP, page-pool, PTP, hardware timestamping, RSS, and DCB features.

## Important APIs, Types, And Functions

The header defines ring sizing, allocation, interrupt moderation, bounce-buffer, checksum, loopback, pause, queue, and MTU constants such as `MAX_RX_RINGS`, `MAX_TX_RINGS`, `TXBB_SIZE`, `MLX4_EN_ALLOC_SIZE`, `MLX4_EN_MAX_RX_FRAGS`, `MLX4_EN_DEF_RX_RING_SIZE`, coalescing thresholds, `MLX4_EN_EFF_MTU()`, and self-test loopback limits. It defines descriptor state in `mlx4_en_tx_info`, `mlx4_en_tx_desc`, `mlx4_en_rx_desc`, `mlx4_en_tx_ring`, `mlx4_en_rx_ring`, and `mlx4_en_cq`.

Configuration and lifetime state is captured by `mlx4_en_port_profile`, `mlx4_en_profile`, `mlx4_en_dev`, `mlx4_en_rss_map`, `mlx4_en_port_state`, `mlx4_en_mc_list`, `mlx4_en_frag_info`, `mlx4_en_stats_bitmap`, `mlx4_en_priv`, `mlx4_mac_entry`, and optional DCB/RFS structures. `mlx4_en_get_cqe()` is an inline CQE accessor parameterized by CQE size.

The prototypes cover netdev creation/destruction, port start/stop, CQ/TX/RX ring creation and activation, NAPI poll handlers, TX submission and completion, XDP TX/recycle paths, RSS steering, drop QP handling, multicast/VLAN filter commands, stats dumping and folding, traffic-class setup, self-test, PTP timestamp conversion, hardware timestamp reset, XDP metadata helpers, and netdev notifier handling.

## Control Flow Role

This header does not implement control flow, but it defines the data contracts used by `en_main.c`, `en_netdev.c`, `en_rx.c`, `en_tx.c`, `en_cq.c`, `en_port.c`, `en_ethtool.c`, and related files. A typical Ethernet bring-up allocates `mlx4_en_dev`, creates one `net_device`/`mlx4_en_priv` per active Ethernet port, configures the profile, creates CQs and TX/RX rings, activates QPs, configures RSS steering and multicast filters, starts NAPI and service/stat delayed work, and later tears those resources down through the paired prototypes. Fast-path TX/RX code reads ring fields laid out here, while slow-path ethtool, DCB, timestamp, and stats code reads `mlx4_en_priv` aggregates.

## State And Persistence Behavior

All state is runtime kernel memory. `mlx4_en_dev` is device-wide and tracks core device pointer, port netdevs, workqueue, UAR/MR/PD resources, PTP clock/timecounter state, notifier blocks, and profile. `mlx4_en_priv` is per netdev/port and owns active VLAN bitmap, link state, ring arrays, CQ arrays, RSS map, work items, counters/stats, multicast lists, MAC hash, tunnel registration, VXLAN port, DCB state, RFS filters, RSS key/hash function, XDP programs on RX rings, and flags. The header deliberately separates device-wide resources from per-port resources, which matters during port restart, netdev close/open, and reload.

Concurrency assumptions are embedded in the layout: TX completion and TX submission fields are separated by cacheline alignment; RX XDP programs are RCU pointers; stats use `stats_lock` and a stats bitmap mutex; UAR access has `uar_lock`; work items handle RX mode changes, restarts, link state, stats, and service tasks. Many counters are `unsigned long` software aggregates folded from per-ring or firmware stats.

## Dependencies And Integration Points

The file depends on Linux networking, VLAN, timestamping, CPU rmap, PTP clock, IRQ, XDP, page-pool-adjacent data structures, optional DCB and RFS configs, and public mlx4 QP/CQ/SRQ/doorbell/cmd headers. It includes `en_port.h` for firmware Ethernet stats mailbox layouts and `mlx4_stats.h` for software stat structs and count constants. Its prototypes are the integration surface between mlx4 core exported APIs and Linux netdev/ethtool/XDP/PTP subsystems.

## Risks

Fast-path struct layout is performance-sensitive; moving fields can increase cacheline sharing or break assumptions in TX/RX code. Ring size constants must remain compatible with hardware descriptor sizes, page allocation, BQL, XDP, and firmware limits. Stats count macros from `mlx4_stats.h` must stay aligned with ethtool string/data iteration. RCU and workqueue fields require correct teardown ordering to avoid use-after-free during close, unregister, or reset. XDP and timestamp fields interact with RX buffer layout and CQE size selected by core caps, so core `main.c` changes to CQE stride/size can affect this header's users.

## Test Signals

Relevant tests include Ethernet netdev open/close, MTU changes, ring resize via ethtool, interrupt moderation updates, RSS indirection changes, multicast/promisc changes, VLAN filtering, XDP attach/drop/redirect/TX, PTP timestamping, hardware timestamp config reset, DCB/PFC where enabled, suspend/resume or devlink reload with netdevs present, and ethtool stats string/count consistency against `NUM_ALL_STATS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4_en.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4_stats.h

## Purpose

`mlx4_stats.h` defines the software statistics schema used by the mlx4 Ethernet driver. It groups packet, PF counter, port software, XDP, PHY, and flow-control pause statistics and defines the count/index macros used to expose those values through ethtool and related netdev statistic paths.

## Important APIs, Types, And Functions

The header defines `NUM_PRIORITIES` as nine packet-priority buckets, including an extra no-VLAN bucket, and `MLX4_NUM_PRIORITIES` as the eight hardware traffic priorities used by flow-control stats. `mlx4_en_pkt_stats` stores multicast/broadcast/jabber/range-error counters plus RX/TX per-priority frame/byte pairs. `mlx4_en_counter_stats` stores PF-level packets and bytes. `mlx4_en_port_stats` stores software-maintained TSO, queue, timeout, allocation, checksum, and transmit helper counters. `mlx4_en_xdp_stats` stores XDP drop/redirect/redirect-fail/TX/TX-full counters. `mlx4_en_phy_stats` stores physical packets and bytes.

`mlx4_en_flow_stats_rx`, `mlx4_en_flow_stats_tx`, and `mlx4_en_stat_out_flow_control_mbox` describe pause-frame, pause-duration, and pause-transition counters. `MLX4_DUMP_ETH_STATS_FLOW_CONTROL` is the command modifier bit used to request flow-control stats from firmware. Count macros such as `NUM_PKT_STATS`, `NUM_PF_STATS`, `NUM_PORT_STATS`, `NUM_XDP_STATS`, `NUM_PHY_STATS`, `NUM_FLOW_STATS`, and `NUM_ALL_STATS` provide ethtool iteration bounds. `FLOW_PRIORITY_STATS_IDX_RX_FRAMES` and `FLOW_PRIORITY_STATS_IDX_TX_FRAMES` identify offsets in the flattened stat vector, and `MLX4_FIND_NETDEV_STAT()` maps a `struct net_device_stats` member to its index.

## Control Flow Role

The file has no executable logic. Its structs are embedded in `struct mlx4_en_priv`, filled by paths such as `mlx4_en_DUMP_ETH_STATS()` and software stat folding, selected by `mlx4_en_set_stats_bitmap()`, and flattened by ethtool getters. Firmware flow-control mailbox data is read in big-endian form and copied into the software RX/TX flow stat structs.

## State And Persistence Behavior

These counters are runtime statistics. They are reset on netdev reset/port restart paths, refreshed from firmware dump commands, or accumulated from ring software counters. Widths are mixed: many software-facing counters use `unsigned long`, while flow-control counters use `u64` and firmware mailbox fields use `__be64`. The schema relies on strict ordering because ethtool string and data paths cast these structs to linear arrays.

## Dependencies And Integration Points

The header is included by `mlx4_en.h` and consumed by Ethernet netdev, port, and ethtool code. It depends on kernel definitions for `__be64`, `offsetof`, and `struct net_device_stats` through includers. Firmware integration occurs through `MLX4_CMD_DUMP_ETH_STATS` users that fill `mlx4_en_stat_out_flow_control_mbox`.

## Risks

The main risk is count/order drift. Adding, removing, or reordering fields without updating the associated `NUM_*` macros, ethtool strings, bitmap offsets, and extraction loops will mislabel or truncate statistics. The two priority counts are intentionally different (`NUM_PRIORITIES` 9 versus `MLX4_NUM_PRIORITIES` 8); confusing them can overrun arrays or omit no-VLAN packet stats. Mixed `unsigned long`, `u64`, and big-endian mailbox fields require care on 32-bit builds and firmware conversion paths.

## Test Signals

Check ethtool stats count and names against `NUM_ALL_STATS`, run firmware stats dump with and without flow-control stats, verify PFC priority stats when pause priority flags are enabled, exercise XDP drop/redirect/TX paths, trigger queue stop/wake and TX timeout counters, and validate 32-bit builds or sparse/endian checking for mailbox conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/mlx4_stats.h -->
