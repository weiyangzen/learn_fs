# subset-b-004527 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_tx.c

## Purpose
`en_tx.c` implements the mlx4 Ethernet transmit datapath. It allocates and tears down TX send queues, transitions TX QPs to ready/reset, builds hardware work queue entries for SKB and XDP transmit, rings BlueFlame or doorbell MMIO, polls transmit completion queues, unmaps DMA, recycles page-pool pages, updates BQL/netdev queue state, and schedules port restart after TX CQ errors.

## Important APIs, Types, and Functions
Key ring lifecycle APIs are `mlx4_en_create_tx_ring()`, `mlx4_en_destroy_tx_ring()`, `mlx4_en_activate_tx_ring()`, `mlx4_en_deactivate_tx_ring()`, and `mlx4_en_free_tx_buf()`. Completion and interrupt entry points are `mlx4_en_process_tx_cq()`, `mlx4_en_tx_irq()`, and `mlx4_en_poll_tx_cq()`. Main transmit entry points are `mlx4_en_xmit()` for normal SKBs, `mlx4_en_select_queue()` for queue selection, `mlx4_en_init_tx_xdp_ring_descs()` for XDP ring template initialization, and `mlx4_en_xmit_frame()` for XDP TX frames.

Important helpers include `mlx4_en_is_tx_ring_full()`, `mlx4_en_stamp_wqe()`, `mlx4_en_free_tx_desc()`, `mlx4_en_recycle_tx_desc()`, `mlx4_en_handle_err_cqe()`, `mlx4_en_bounce_to_desc()`, `is_inline()`, `inline_size()`, `get_real_size()`, `build_inline_wqe()`, `mlx4_en_xmit_doorbell()`, `mlx4_en_tx_write_desc()`, and `mlx4_en_build_dma_wqe()`. The code operates on `struct mlx4_en_tx_ring`, `struct mlx4_en_tx_info`, `struct mlx4_en_tx_desc`, CQEs, WQE data segments, SKBs, RX page-pool frame descriptors, QP state, BlueFlame UARs, and netdev TX queues.

## Control Flow
Ring creation allocates software metadata, a bounce buffer, hardware queue resources, a QP number/QP object, and optionally a BlueFlame register. Activation zeros software and hardware rings, builds a QP context through `mlx4_en_fill_qp_context()`, programs UAR page information when BlueFlame was allocated, and moves the QP ready through `mlx4_qp_to_ready()`. Deactivation and destruction unwind QP state, QP reservations, HW queue memory, bounce buffer, and metadata.

`mlx4_en_xmit()` is the normal SKB path. It rejects sends when the port is down, computes the required descriptor shape for GSO, inline, or DMA-backed packets, handles VLAN insertion and BlueFlame eligibility, reserves ring producer space, selects direct ring memory or the bounce buffer for wraparound descriptors, fills `tx_info`, maps DMA fragments and linear data from tail to head, records timestamp requests, sets checksum and loopback flags, builds LSO or SEND control state, copies inline payload when allowed, sets encapsulation checksum flags, advances `ring->prod`, optionally copies the bounce buffer back into the ring, updates BQL, stops the netdev queue if the ring is full, and finally publishes the descriptor via BlueFlame or doorbell. On failures it drops the SKB and increments drop counters where appropriate.

`mlx4_en_process_tx_cq()` walks CQEs while ownership belongs to software and the work limit is not exceeded. It handles error CQEs once per recovering ring, advances over completed WQEs, extracts hardware timestamps for timestamp-requested descriptors, frees normal SKB descriptors or recycles XDP pages through an indirect call, stamps completed WQEs back to software ownership, updates packet/byte counters, commits CQ consumer index before ring consumer index, and wakes a stopped queue when space is available. XDP completions return early without BQL updates. IRQ handling schedules NAPI while the port is up and arms the CQ otherwise.

## State and Persistence
There is no filesystem persistence. Runtime state is in TX ring producer/consumer counters, `last_nr_txbb`, `tx_info[]`, HW queue memory, QP state, CQ consumer index, BlueFlame offset, timestamp mode, queue stop/wake counters, packet/byte/drop statistics, and page-pool ownership for XDP frames. DMA mappings persist from descriptor build until completion. The code relies on `READ_ONCE()`, `WRITE_ONCE()`, `dma_rmb()`, `dma_wmb()`, `wmb()`, and `smp_rmb()` to order ownership bits, descriptor contents, CQ consumer updates, and queue wake/stop checks.

## Dependencies and Integration Points
The file integrates with Linux netdev TX (`ndo_start_xmit`, BQL, XPS, NAPI, VLAN tags, GSO, checksum offload, timestamping), DMA mapping APIs, page pool XDP recycling, mlx4 core QP/CQ/UAR/HWQ allocation, mlx4 Ethernet private structures from `mlx4_en.h`, and device restart workqueues. Callers include mlx4 Ethernet netdev setup and self-test paths; completions depend on CQ arming and event delivery from the mlx4 EQ layer.

## Risks
The highest-risk areas are descriptor wraparound and bounce-buffer copying, owner-bit and memory-barrier ordering, DMA unmap symmetry after partial mapping failures, LSO header validation for nonlinear headers, ring full accounting with `HEADROOM` and `MLX4_MAX_DESC_TXBBS`, queue stop/wake races, timestamp delivery tied to CQE timestamps, and separation between normal SKB freeing and XDP page-pool recycling. A TX CQ error schedules a restart; repeated errors or incorrect recovering state handling can mask further diagnostics.

## Test Signals
Useful signals include SKB transmit across tiny, minimum-length, VLAN, QinQ, checksum, encapsulated, fragmented, inline, non-inline, and TSO packets; descriptor wraparound with bounce-buffer use; DMA mapping failure injection; hardware timestamp request/complete paths; BQL queue stop and wake behavior under saturation; CQE error handling and restart scheduling; XDP TX success, ring-full, and port-down paths; teardown with outstanding descriptors; and interrupt/NAPI polling with both budgeted and zero-budget XDP cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/eq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/eq.c

## Purpose
`eq.c` implements mlx4 event queue management and interrupt dispatch. It creates and destroys EQs, maps events to EQs, handles legacy INTx and MSI-X interrupts, dispatches completions and asynchronous firmware events, forwards virtualized events to SR-IOV slaves, maintains slave port state transitions, handles FLR cleanup, exposes EQ vector allocation helpers, and provides interrupt self-tests.

## Important APIs, Types, and Functions
Public/exported APIs include `mlx4_gen_pkey_eqe()`, `mlx4_gen_guid_change_eqe()`, `mlx4_gen_port_state_change_eqe()`, `mlx4_get_slave_port_state()`, `set_and_calc_slave_port_state()`, `mlx4_gen_slaves_port_mgt_ev()`, `mlx4_master_handle_slave_flr()`, `mlx4_MAP_EQ_wrapper()`, `mlx4_alloc_eq_table()`, `mlx4_free_eq_table()`, `mlx4_init_eq_table()`, `mlx4_cleanup_eq_table()`, `mlx4_test_async()`, `mlx4_test_interrupt()`, `mlx4_is_eq_vector_valid()`, `mlx4_get_eqs_per_port()`, `mlx4_is_eq_shared()`, `mlx4_get_cpu_rmap()`, `mlx4_assign_eq()`, `mlx4_eq_get_irq()`, and `mlx4_release_eq()`.

Important internal helpers are `get_async_ev_mask()`, `eq_set_ci()`, `get_eqe()`, `next_eqe_sw()`, `next_slave_event_eqe()`, `mlx4_gen_slave_eqe()`, `slave_event()`, `mlx4_slave_event()`, `mlx4_set_eq_affinity_hint()`, `set_all_slave_state()`, `mlx4_eq_int()`, `mlx4_interrupt()`, `mlx4_msi_x_interrupt()`, `mlx4_MAP_EQ()`, `mlx4_SW2HW_EQ()`, `mlx4_HW2SW_EQ()`, `mlx4_num_eq_uar()`, `mlx4_get_eq_uar()`, `mlx4_create_eq()`, `mlx4_free_eq()`, and IRQ/clear-register mapping helpers. Core state lives in `struct mlx4_eq`, `struct mlx4_eq_table`, `struct mlx4_eqe`, slave event queues, EQ contexts, MTTs, IRQ names, CPU affinity masks, and SR-IOV slave state.

## Control Flow
Initialization allocates an EQ array and UAR map, initializes the EQ bitmap, maps the interrupt clear register for non-slaves, creates one async EQ plus completion EQs, allocates DMA-coherent EQ pages, writes MTTs, transitions EQ contexts from software to hardware, requests either a shared legacy IRQ or MSI-X IRQs, maps the async event mask, and arms the async EQ. Completion EQ IRQs can be requested lazily by `mlx4_assign_eq()` when a consumer asks for a vector.

`mlx4_eq_int()` is the central event loop. It reads EQEs whose owner bit indicates software ownership, issues a DMA read barrier, switches on the event type, and dispatches to CQ completion, QP/SRQ/CQ events, command completion, port change, EQ overflow, operation-required work, communication-channel work, FLR work, fatal warning, port management change, recoverable error, or warning logs. In master mode it maps QP/SRQ/CQ resources back to owning slaves and forwards events instead of dispatching locally when appropriate. The loop periodically writes the consumer index to avoid overflow and arms the EQ at the end.

SR-IOV event forwarding uses a software slave event queue protected by `event_lock`; `slave_event()` copies an EQE, stores a target slave or `ALL_SLAVES`, flips ownership, advances producer, and queues master communication work. `mlx4_gen_slave_eqe()` drains this queue and invokes `mlx4_GEN_EQE()` for target VFs, translating physical ports to slave ports for port-management events and suppressing bonded-port down notifications when another physical port is still up. FLR events mark slave state inactive/going down, dispatch a slave shutdown event, delete resources when the interface is up, reset slave state, and inform firmware that FLR is done.

## State and Persistence
There is no filesystem persistence. Persistent runtime state includes EQ DMA pages, MTTs, consumer indexes, IRQ registrations, UAR doorbell mappings, `actv_ports` bitmaps, vector refcounts, CPU rmap data, MSI-X pool bits, slave event producer/consumer indexes, slave port state, per-slave last command and activity flags, and interface workqueue items. Ordering is hardware-facing: owner-bit reads use `dma_rmb()`, generated slave EQEs use `dma_wmb()`, and EQ consumer doorbells use raw big-endian writes plus `wmb()`.

## Dependencies and Integration Points
This file ties firmware event delivery to mlx4 core subsystems: CQ/QP/SRQ event handlers, command event completion, resource tracking, SR-IOV communication, port sensing, workqueues, mlx4 event notifier dispatch, PCI IRQ/MSI-X allocation, CPU affinity/rmap, MTT allocation, and firmware commands `MAP_EQ`, `SW2HW_EQ`, and `HW2SW_EQ`. It is consumed by Ethernet, RDMA, and core code that need completion vectors or asynchronous device events.

## Risks
Risk centers on owner-bit parity and EQE stride calculations, CQ/EQ overflow if consumer indexes are not committed quickly enough, event forwarding to the wrong slave after port translation or resource lookup errors, bonded-port down suppression, FLR race handling during reset/load, IRQ teardown ordering with tasklets and `synchronize_irq()`, MSI-X vector refcount leaks, and capability-dependent async event masks. Incorrect port-state transitions can generate spurious IB up/down events or suppress required ones.

## Test Signals
Important tests are EQ creation/cleanup under MSI-X and shared IRQ, async NOP interrupt tests, completion interrupt tests per vector, port up/down events for Ethernet and IB, bonded mode event forwarding, CQ/QP/SRQ error events owned by PF and VF resources, command completions, communication channel events, FLR cleanup with active and inactive interfaces, recoverable cable events, IRQ affinity/rmap registration, vector assignment/release, and teardown with live interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/eq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw.c

## Purpose
`fw.c` is the mlx4 firmware command and capability translation layer. It builds and parses command mailboxes for firmware queries, HCA initialization, port initialization, ICM mapping, device configuration, diagnostics, WOL, required operations, MAD demux, register access, PHV/VLAN helper state, and SR-IOV command wrapping. It turns raw firmware mailbox fields into `mlx4_dev` capabilities and hides or translates PF-only capabilities for guests.

## Important APIs, Types, and Functions
Capability and firmware APIs include `mlx4_QUERY_FW()`, `mlx4_QUERY_FW_wrapper()`, `mlx4_QUERY_DEV_CAP()`, `mlx4_QUERY_DEV_CAP_wrapper()`, `mlx4_QUERY_PORT()`, `mlx4_QUERY_PORT_wrapper()`, `mlx4_QUERY_FUNC()`, `mlx4_QUERY_FUNC_CAP()`, `mlx4_QUERY_FUNC_CAP_wrapper()`, `mlx4_QUERY_ADAPTER()`, `mlx4_dev_cap_dump()`, and `mlx4_replace_zero_macs()`. Initialization and memory-map APIs include `mlx4_MOD_STAT_CFG()`, `mlx4_map_cmd()`, `mlx4_MAP_FA()`, `mlx4_UNMAP_FA()`, `mlx4_RUN_FW()`, `mlx4_INIT_HCA()`, `mlx4_QUERY_HCA()`, `mlx4_INIT_PORT()`, `mlx4_INIT_PORT_wrapper()`, `mlx4_CLOSE_PORT()`, `mlx4_CLOSE_PORT_wrapper()`, `mlx4_CLOSE_HCA()`, `mlx4_SET_ICM_SIZE()`, `mlx4_MAP_ICM_AUX()`, and `mlx4_UNMAP_ICM_AUX()`.

Configuration and utility APIs include `mlx4_config_dev_retrieval()`, `mlx4_config_vxlan_port()`, `mlx4_disable_rx_port_check()`, `mlx4_config_roce_v2_port()`, `mlx4_virt2phy_port_map()`, `mlx4_NOP()`, `mlx4_query_diag_counters()`, `mlx4_get_phys_port_id()`, `mlx4_wol_read()`, `mlx4_wol_write()`, `mlx4_opreq_action()`, `mlx4_config_mad_demux()`, `mlx4_ACCESS_PTYS_REG()`, `mlx4_ACCESS_REG_wrapper()`, `get_phv_bit()`, `set_phv_bit()`, and `mlx4_get_is_vlan_offload_disabled()`. The file uses local `MLX4_GET`/`MLX4_PUT` macros for endian-correct mailbox field access and many offset constants describing firmware command layouts.

## Control Flow
Firmware discovery starts with command mailbox allocation, `QUERY_FW`, firmware version parsing, command interface revision validation, maximum command count extraction, and PF-only mapping of catastrophic error, clear-int, communication vector, clock, and firmware-area page information. Device capability discovery issues `QUERY_DEV_CAP`, optionally masks unsupported RoCE capabilities in multifunction mode, decodes resource counts, reserved ranges, page and UAR sizing, BlueFlame, RSS, flow steering, timestamp, QoS, rate limiting, VXLAN, diagnostics, WOL, EQE/CQE stride, port capabilities, and reserved EQ adjustment based on UAR reservations or system EQ support.

SR-IOV wrappers call native firmware commands on behalf of slaves, then sanitize or translate results. `QUERY_FUNC_CAP_wrapper()` reports general quotas and per-port special QPs, physical port IDs, PHV/VLAN-offload flags, VST QinQ support, reserved lkeys, and non-power-of-two EQ support. `QUERY_DEV_CAP_wrapper()` hides host-only or unsafe guest capabilities such as timestamping, VXLAN, QoS, BlueFlame, memory windows, port remap, VST/FSM, QCN, rate limiting, and ignore-FCS, while remapping port counts and WOL bits. `QUERY_PORT_wrapper()` converts logical ports, overrides VF MAC/link state, constrains port type, and reports per-slave GID/PKey table limits.

HCA initialization builds the INIT_HCA mailbox from `struct mlx4_init_hca_param`, selects endian mode, enables checksum/counters/RSS/QoS where supported, configures CQE/EQE sizes and strides, optionally reports driver version, programs QP/SRQ/CQ/EQ/RDMARC/steering/TPT/UAR bases, and issues `INIT_HCA`. The query path reads those settings back. Port wrappers refcount per-port initialization across slaves and treat IB QP0 proxy state specially. CONFIG_DEV helpers read/write device-level settings for checksum mode, VXLAN, RoCEv2 UDP port, and RX port check disabling. `mlx4_map_cmd()` iterates ICM chunks and sends MAP command batches with page-size encodings.

## State and Persistence
There is no filesystem persistence. Runtime state is stored in `dev->caps`, `mlx4_priv(dev)->fw`, `mlx4_priv(dev)->cmd`, per-port capability arrays, multifunction VF admin/oper state, slave state flags, QP0 proxy state, init-port refcounts, PHV bits, physical port IDs, and op-required work counters. Mailboxes are temporary DMA buffers. Firmware state persists in the device across command calls until explicit close/unmap/config commands or device reset.

## Dependencies and Integration Points
The file depends on the mlx4 command interface (`mlx4_cmd*`, command mailboxes), ICM allocation/iteration from `icm.c`, resource tracking and SR-IOV helpers from `mlx4.h`, Ethernet constants, RDMA ABI user capability bits, multicast attach/detach, port and slave mapping helpers, workqueues, and exported APIs used by mlx4 main initialization, Ethernet, IB, devlink, ethtool/WOL, flow steering, and QoS code.

## Risks
This file is highly offset-sensitive: a wrong mailbox offset, endian conversion, bit mask, or wrapper sanitization can misreport hardware capabilities or expose PF-only controls to VFs. Other risks include command-interface revision mismatches, page-count rounding for ICM pages, guest capability inconsistencies, VST QinQ state rollback, port-init refcount leaks, IB QP0 proxy gating, QoS enablement tied to module parameter and firmware flags, CONFIG_DEV support probing, and operation-required work acknowledgement errors. The `mlx4_ACCESS_REG_wrapper()` write restriction is a security boundary for non-master functions.

## Test Signals
Important tests include firmware query on supported and unsupported command revisions, capability parsing with and without multifunction mode, guest wrappers for each hidden/translated capability, physical/logical port conversion failures, HCA init/query round trips for steering modes and CQE/EQE stride, old and new port command paths, per-slave init/close refcounting, ICM map batching and alignment errors, CONFIG_DEV get/set for checksum/VXLAN/RoCE, WOL read/write, diagnostic counter bounds checks, op-required ADD_TO_MCG attach/detach, MAD demux secure-host detection, ACCESS_PTYS read/write permission, PHV set/get, VLAN offload disabled query, and zero MAC replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw.h

## Purpose
`fw.h` declares the firmware-facing data structures and command helper prototypes implemented mainly by `fw.c` and partly by `icm.c`. It is the local contract for mlx4 firmware discovery, HCA setup, port capabilities, function capabilities, adapter identity, ICM mapping, basic firmware lifecycle commands, and operation-required handling.

## Important APIs, Types, and Functions
Important data structures are `struct mlx4_mod_stat_cfg`, `struct mlx4_port_cap`, `struct mlx4_dev_cap`, `struct mlx4_func_cap`, `struct mlx4_func`, `struct mlx4_adapter`, `struct mlx4_init_hca_param`, `struct mlx4_init_ib_param`, and `struct mlx4_set_ib_param`. These structures aggregate parsed firmware capability fields for resources, ports, BlueFlame, UARs, ICM, RSS, steering, WOL, rate limiting, health buffers, special QPs, reserved lkeys, HCA context bases, CQE/EQE sizing, and IB port setup.

The header declares firmware query and lifecycle functions such as `mlx4_QUERY_DEV_CAP()`, `mlx4_QUERY_PORT()`, `mlx4_QUERY_FUNC_CAP()`, `mlx4_QUERY_FUNC_CAP_wrapper()`, `mlx4_QUERY_FUNC()`, `mlx4_QUERY_FW()`, `mlx4_QUERY_ADAPTER()`, `mlx4_INIT_HCA()`, `mlx4_QUERY_HCA()`, `mlx4_CLOSE_HCA()`, `mlx4_RUN_FW()`, `mlx4_NOP()`, and `mlx4_MOD_STAT_CFG()`. It also declares ICM mapping helpers `mlx4_MAP_FA()`, `mlx4_UNMAP_FA()`, `mlx4_map_cmd()`, `mlx4_SET_ICM_SIZE()`, `mlx4_MAP_ICM_AUX()`, `mlx4_UNMAP_ICM_AUX()`, plus `mlx4_opreq_action()`.

## Control Flow
The header itself has no executable control flow. Its structure reflects initialization order: query firmware and device capabilities, allocate/map firmware and ICM memory, initialize the HCA with `mlx4_init_hca_param`, query or initialize ports, then use capability structures to enable higher-level Ethernet, IB, steering, QoS, and virtualization features.

## State and Persistence
There is no direct state mutation in the header. State is represented by structs populated by firmware commands and then copied into `struct mlx4_dev` capability fields or private firmware state. The declarations define which capability fields are durable driver runtime state and which command parameters must remain aligned with firmware mailbox layouts.

## Dependencies and Integration Points
The header includes `mlx4.h` and `icm.h`, so it sits between core device state and ICM management. It is consumed by core initialization, EQ setup, port management, Ethernet and IB subdrivers, SR-IOV command wrappers, and firmware memory setup. Any structure change must remain consistent with parsing in `fw.c` and with consumers in `main.c`, `eq.c`, and related mlx4 modules.

## Risks
The main risks are ABI drift between declared structures and firmware parser expectations, missing prototypes for exported helpers, and ambiguous ownership of capability fields. Because many values are sizes, resource counts, or bitfields decoded from firmware, incorrect type widths can truncate hardware limits or flags. The header also exposes wrapper prototypes, so misuse by non-wrapper paths could bypass expected validation.

## Test Signals
Compile coverage is the primary signal: all consumers should build with no prototype or type mismatches. Runtime signals come from successful firmware query/init flows, correct capability propagation into `dev->caps`, correct ICM mapping, correct port capability consumers, and SR-IOV wrapper calls matching the declared signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw_qos.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw_qos.c

## Purpose
`fw_qos.c` implements firmware command helpers for mlx4 Enhanced QoS. It configures port priority-to-traffic-class mapping, traffic-class scheduler bandwidth/rate limits, virtual port priority allocation (VPP), and per-vport QoS bandwidth parameters.

## Important APIs, Types, and Functions
Exported APIs are `mlx4_SET_PORT_PRIO2TC()`, `mlx4_SET_PORT_SCHEDULER()`, `mlx4_ALLOCATE_VPP_get()`, `mlx4_ALLOCATE_VPP_set()`, `mlx4_SET_VPORT_QOS_get()`, and `mlx4_SET_VPORT_QOS_set()`. Internal mailbox structures are `struct mlx4_set_port_prio2tc_context`, `struct mlx4_port_scheduler_tc_cfg_be`, `struct mlx4_set_port_scheduler_context`, `struct mlx4_alloc_vpp_param`, `struct mlx4_prio_qos_param`, and `struct mlx4_set_vport_context`.

## Control Flow
Each API allocates a command mailbox, fills or reads a firmware-defined context, invokes `mlx4_cmd()` or `mlx4_cmd_box()` with the relevant opcode and modifier, then frees the mailbox. `mlx4_SET_PORT_PRIO2TC()` packs two user priorities per byte. `mlx4_SET_PORT_SCHEDULER()` iterates all traffic classes, sets priority group, ETS bandwidth percentage, and either a default or explicit rate limit using 100 Mbps or 1 Gbps units. VPP query/set commands read or write available/distributed VPP counts per user priority. Vport QoS query/set commands transfer `bw_share`, `max_avg_bw`, and an enable bit per user priority.

## State and Persistence
The file does not retain local state. Successful commands persist configuration in device firmware for the selected physical port or vport. Mailbox data is temporary, and the caller owns arrays passed for priority, traffic class, rate limit, VPP allocation, and vport QoS.

## Dependencies and Integration Points
The file depends on the mlx4 command mailbox layer, command opcodes from `linux/mlx4/cmd.h`, device types from `linux/mlx4/device.h`, and declarations/constants from `fw_qos.h` and `fw.h`. It is used by Ethernet DCB/netlink and SR-IOV QoS management paths after firmware capability checks in `fw.c` and HCA initialization enablement.

## Risks
Risks include invalid caller-provided arrays, bandwidth percentages that do not sum correctly within priority groups, rate-limit unit conversion truncation for values above the 100 Mbps range, endian conversion mistakes in firmware contexts, and issuing commands when the device or port lacks QoS/VPP support. The enable bit in vport QoS is shifted to bit 31 on set and decoded from low bits on get, so firmware format assumptions should be validated.

## Test Signals
Useful tests cover priority-to-TC packing, scheduler programming with null and non-null rate-limit arrays, boundary rate limits around `MLX4_MAX_100M_UNITS_VAL`, VPP query before and after allocation, per-vport QoS set/get round trips for all eight priorities, unsupported firmware failures, mailbox allocation failure, and integration through DCB configuration tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw_qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw_qos.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw_qos.h

## Purpose
`fw_qos.h` defines the public mlx4 QoS firmware helper contract. It provides constants for user priorities and traffic classes, default VPP values, the per-vport QoS parameter type, and prototypes for port scheduler, VPP, and vport QoS commands.

## Important APIs, Types, and Functions
The header defines `MLX4_NUM_UP`, `MLX4_NUM_TC`, `MLX4_DEFAULT_QOS_PRIO`, and `MLX4_VPP_DEFAULT_VPORT`. `struct mlx4_vport_qos_param` carries `bw_share`, `max_avg_bw`, and `enable` for one user priority. Declared functions are `mlx4_SET_PORT_PRIO2TC()`, `mlx4_SET_PORT_SCHEDULER()`, `mlx4_ALLOCATE_VPP_get()`, `mlx4_ALLOCATE_VPP_set()`, `mlx4_SET_VPORT_QOS_get()`, and `mlx4_SET_VPORT_QOS_set()`.

## Control Flow
The header has no executable control flow. It documents expected sequencing: configure priority-to-TC and scheduler settings at the port level, query and allocate VPP resources per priority after port type is set and before QPs are open, and set vport QoS before associating QPs with that vport.

## State and Persistence
No state is stored in the header. State is represented by caller-owned arrays and `struct mlx4_vport_qos_param` values that `fw_qos.c` serializes into firmware mailboxes. Successful calls persist the configuration in firmware.

## Dependencies and Integration Points
The header includes mlx4 command and device public headers and is used by QoS/DCB implementation code plus `fw_qos.c`. It forms the interface between netdev QoS policy and firmware command encoding.

## Risks
Risks are mostly contract-related: all arrays are expected to have eight entries, VPP allocation must not exceed firmware-reported availability, scheduler bandwidth percentages must be valid per priority group, and callers must check firmware capability before invoking these helpers. Misordered VPP or QoS setup relative to QP creation can fail or produce undefined firmware behavior.

## Test Signals
Compile-time tests ensure consumers match the prototypes and constants. Runtime signals include successful DCB scheduler configuration, VPP allocation validation, vport QoS query/set round trips, and failure behavior on unsupported firmware or invalid port/vport identifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw_qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/icm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/icm.c

## Purpose
`icm.c` manages mlx4 ICM, the host memory backing firmware object tables. It allocates chunked DMA memory, maps and unmaps that memory into firmware address space, lazily backs ICM table chunks on demand, tracks references, finds lowmem table entries, and initializes/cleans reserved table ranges.

## Important APIs, Types, and Functions
Public APIs are `mlx4_alloc_icm()`, `mlx4_free_icm()`, `mlx4_MAP_ICM_AUX()`, `mlx4_UNMAP_ICM_AUX()`, `mlx4_table_get()`, `mlx4_table_put()`, `mlx4_table_find()`, `mlx4_table_get_range()`, `mlx4_table_put_range()`, `mlx4_init_icm_table()`, and `mlx4_cleanup_icm_table()`. Internal helpers include `mlx4_free_icm_pages()`, `mlx4_free_icm_coherent()`, `mlx4_alloc_icm_pages()`, `mlx4_alloc_icm_coherent()`, `mlx4_MAP_ICM()`, and `mlx4_UNMAP_ICM()`. Core structures come from `icm.h`: `struct mlx4_icm`, `struct mlx4_icm_chunk`, `struct mlx4_icm_buf`, and `struct mlx4_icm_table`.

## Control Flow
`mlx4_alloc_icm()` allocates an ICM container and then repeatedly allocates chunks up to 256 KiB, lowering allocation order on failure. Non-coherent allocations use pages and scatterlists that are DMA-mapped when a chunk fills or at the end. Coherent allocations use `dma_alloc_coherent()` and require page-aligned virtual addresses. On failure, all partially allocated chunks are freed.

`mlx4_table_get()` maps an object number to a table chunk, locks the table, increments the refcount if the chunk already exists, or allocates and firmware-maps a new 256 KiB ICM chunk at `table->virt + chunk_offset`. `mlx4_table_put()` decrements the chunk refcount and unmaps/frees the chunk at zero. Range helpers repeat this per chunk and unwind on failure. `mlx4_init_icm_table()` allocates the table pointer array, records table metadata, and preallocates/maps chunks that contain reserved firmware objects with a permanent reference. `mlx4_table_find()` returns a CPU pointer and optional DMA handle for lowmem-backed table objects by walking chunk DMA segments.

## State and Persistence
There is no filesystem persistence. Runtime state is the ICM chunk list, chunk page/scatterlist/coherent-buffer descriptors, DMA mappings, per-ICM refcount, and per-table metadata protected by `table->mutex`. Firmware mappings persist in the device until `UNMAP_ICM` or cleanup. Reserved chunks intentionally keep a positive refcount so they remain mapped for firmware-owned objects.

## Dependencies and Integration Points
The file depends on Linux page allocation, DMA mapping, scatterlists, mutexes, mlx4 command helpers in `fw.c`, PCI device DMA context, and table definitions in `mlx4.h`. It is used by core device initialization and resource subsystems for QP, CQ, SRQ, MPT, MTT, EQ, multicast, and auxiliary firmware tables.

## Risks
Risk areas include high-order allocation fallback, coherent allocation alignment, DMA map/unmap symmetry, refcount underflow if `put` exceeds `get`, object-to-chunk index calculations when object counts are not powers of two, lowmem-only pointer lookup assumptions, reserved range sizing near the end of a table, and firmware map/unmap failures leaving host and device views inconsistent. The code assumes DMA mapping may merge but not split pages when deriving DMA handles.

## Test Signals
Useful tests include allocation with coherent and non-coherent modes, fallback from high-order pages, DMA mapping failure injection, table get/put refcount behavior, range get unwind, reserved chunk preallocation, table lookup pointer and DMA-handle correctness for lowmem tables, cleanup after partial initialization failure, and map/unmap command error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/icm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/icm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/icm.h

## Purpose
`icm.h` defines mlx4 ICM data structures, constants, iterator helpers, and public APIs for firmware table backing memory. It is the shared contract between ICM allocation/mapping code and firmware initialization/resource table consumers.

## Important APIs, Types, and Functions
Important constants are `MLX4_ICM_CHUNK_LEN`, `MLX4_ICM_PAGE_SHIFT`, and `MLX4_ICM_PAGE_SIZE`. Key types are `struct mlx4_icm_buf` for coherent DMA buffers, `struct mlx4_icm_chunk` for a list node containing either scatterlist pages or coherent buffers, `struct mlx4_icm` for a refcounted list of chunks, and `struct mlx4_icm_iter` for walking mapped segments. Inline iterator APIs are `mlx4_icm_first()`, `mlx4_icm_last()`, `mlx4_icm_next()`, `mlx4_icm_addr()`, and `mlx4_icm_size()`.

Declared APIs include `mlx4_alloc_icm()`, `mlx4_free_icm()`, `mlx4_table_get()`, `mlx4_table_put()`, `mlx4_table_get_range()`, `mlx4_table_put_range()`, `mlx4_init_icm_table()`, `mlx4_cleanup_icm_table()`, `mlx4_table_find()`, `mlx4_MAP_ICM_AUX()`, and `mlx4_UNMAP_ICM_AUX()`.

## Control Flow
The inline iterator starts at the first chunk in an ICM list, advances through `nsg` segments in each chunk, moves to the next list entry, and ends when it wraps back to the list head. Address and size helpers select coherent-buffer DMA fields or scatterlist DMA fields based on `chunk->coherent`.

## State and Persistence
No state is created by the header itself. It defines the in-memory representation used by `icm.c`: chunk list membership, number of pages/segments, coherent-vs-scatterlist storage, and ICM refcount. Firmware visibility of that state is established by map commands outside the header.

## Dependencies and Integration Points
The header depends on Linux list, PCI, mutex, scatterlist/DMA types through included headers, and `struct mlx4_icm_table` from `mlx4.h`. It is included by `fw.h`, `fw.c`, `icm.c`, and mlx4 core initialization paths that allocate and map firmware tables.

## Risks
Iterator correctness depends on `nsg` being populated after DMA mapping and on chunk lists remaining stable while iterated. The union layout means callers must respect `chunk->coherent`. `MLX4_ICM_CHUNK_LEN` is sized to keep chunks compact; changes to structure fields can alter allocation density. Address/size helpers assume DMA mappings are valid.

## Test Signals
Compile tests catch structure and prototype mismatches. Runtime signals include successful ICM map command iteration over coherent and non-coherent chunks, correct end-of-list behavior, correct segment sizes, and clean table allocation/free cycles under resource stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/icm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/intf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/intf.c

## Purpose
`intf.c` manages mlx4 auxiliary devices and event notifier dispatch for protocol subdrivers. It creates auxiliary devices for Ethernet and IB capabilities, registers/unregisters auxiliary drivers, rescans subdevices when the core device state or bonding mode changes, dispatches core events through an atomic notifier chain, and exposes devlink port access.

## Important APIs, Types, and Functions
Public APIs include `mlx4_adev_init()`, `mlx4_adev_cleanup()`, `mlx4_register_auxiliary_driver()`, `mlx4_unregister_auxiliary_driver()`, `mlx4_do_bond()`, `mlx4_dispatch_event()`, `mlx4_register_event_notifier()`, `mlx4_unregister_event_notifier()`, `mlx4_register_device()`, `mlx4_unregister_device()`, and `mlx4_get_devlink_port()`. Internal helpers are `is_eth_supported()`, `is_ib_supported()`, `adev_release()`, `add_adev()`, `del_adev()`, `add_drivers()`, `delete_drivers()`, and `rescan_drivers_locked()`. State is guarded by the global `intf_mutex` and auxiliary-device IDs are allocated by `mlx4_adev_ida`.

## Control Flow
`mlx4_adev_init()` allocates a unique auxiliary-device ID and the per-device auxiliary pointer array. `mlx4_register_device()` marks the interface up under `intf_mutex`, rescans supported auxiliary devices, unwinds on failure, and starts catastrophic-error polling. Rescanning deletes unsupported devices and adds supported missing devices based on current port types and IBoE capability. `mlx4_unregister_device()` stops catas polling, handles VF communication-channel error state during deletion, marks the interface down, and rescans to delete all auxiliary devices.

`mlx4_do_bond()` toggles bonded mode after checking port-remap support and programming RX port check or virtual-to-physical port map. It then locks the interface list, finds loaded auxiliary devices whose drivers advertise bonding support, skips SR-IOV multifunction devices, deletes and recreates those auxiliary devices so protocol drivers re-probe with the new bonding mode. Event notifier functions wrap `atomic_notifier_call_chain()` and notifier registration. Auxiliary driver registration delegates to the kernel auxiliary bus.

## State and Persistence
There is no filesystem persistence. Runtime state includes the global auxiliary IDA, `priv->adev_idx`, `priv->adev[]`, `dev->persist->interface_state`, `dev->flags` bonded bit, catastrophic polling state, auxiliary device lifecycle references, and registered notifier blocks. Auxiliary devices persist in the kernel device model until deleted/uninitialized and released.

## Dependencies and Integration Points
The file depends on the Linux auxiliary bus, IDA allocation, device model locking, devlink ports, atomic notifier chains, mlx4 core state, port capability fields, bonding flags, firmware helpers `mlx4_disable_rx_port_check()` and `mlx4_virt2phy_port_map()`, catastrophic error polling, and VF communication health handling. It is the bridge that lets mlx4 Ethernet and IB protocol drivers bind to the same PCI core device.

## Risks
Risks include auxiliary-device lifetime mistakes, rescanning while drivers are bound, global mutex ordering with device locks, partial add failure cleanup, bonded-mode reprobe behavior, SR-IOV restrictions during bonding, interface-state races during remove, and error-state transition if VF communication is already down. Support detection must stay aligned with port type and IBoE capability or subdrivers may fail to probe or remain loaded incorrectly.

## Test Signals
Important tests include registering/unregistering the core device with Ethernet-only, IB-only, mixed, and IBoE configurations; auxiliary driver bind/unbind paths; add failure injection and unwind; notifier registration and event dispatch; bonded mode enable/disable with bonding-capable and non-capable subdrivers; SR-IOV bonding refusal; VF deletion with communication error; repeated register/unregister cycles; and devlink port retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/intf.c -->
