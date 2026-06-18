# Research: subset-b-004466

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_base.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_base.c

## Purpose

`ice_base.c` is the Intel ICE driver's VSI queue bring-up and queue-pair control implementation. It owns the local Linux-side preparation of Rx/Tx rings, maps VSI rings to interrupt vectors, allocates and frees `ice_q_vector` instances, programs queue interrupt registers, constructs RLAN/TLAN/TxTime queue contexts, calls the common AdminQ scheduler helpers to add or remove Tx queues, and provides single queue-pair disable/enable routines used by AF_XDP and dynamic queue operations.

This file is not a standalone hardware abstraction. It sits between high-level VSI/netdev orchestration in `ice_lib.c`, DCB/SR-IOV/XDP helpers, and lower-level register/AdminQ routines from `ice_common.c`.

## Important APIs, Types, and Functions

Exported entry points:

- `ice_vsi_cfg_single_rxq()` and `ice_vsi_cfg_rxqs()` configure one or all Rx rings, including XSK/page-pool setup, XDP RXQ metadata, RLAN context programming, tail pointer initialization, and initial buffer posting.
- `__ice_vsi_get_qs()` assigns PF-global queue IDs to a VSI using contiguous allocation first and scattered allocation as fallback.
- `ice_vsi_ctrl_one_rx_ring()` and `ice_vsi_wait_one_rx_ring()` request Rx queue enable/disable and optionally wait for `QRX_CTRL_QENA_STAT_M`.
- `ice_vsi_alloc_q_vectors()`, `ice_vsi_map_rings_to_vectors()`, and `ice_vsi_free_q_vectors()` allocate interrupt vector containers, register NAPI when a netdev exists, map rings evenly to vectors, and clean up interrupt/NAPI ownership.
- `ice_vsi_cfg_single_txq()`, `ice_vsi_cfg_lan_txqs()`, and `ice_vsi_cfg_xdp_txqs()` configure Tx rings through TLAN contexts and scheduler/AdminQ queue-add calls.
- `ice_cfg_itr()`, `ice_cfg_txq_interrupt()`, `ice_cfg_rxq_interrupt()`, and `ice_trigger_sw_intr()` program interrupt throttling, queue interrupt causes, and software interrupt triggers.
- `ice_vsi_stop_tx_ring()` and `ice_fill_txq_meta()` prepare and issue Tx queue disable requests.
- `ice_qp_dis()` and `ice_qp_ena()` implement one queue-pair teardown/restart, including netdev queue state, NAPI/IRQ toggles, Rx/Tx hardware control, ring cleaning, stats reset, XDP pool refresh, and carrier handling.
- `ice_calc_ts_ring_count()` derives a timestamp queue descriptor count from E830 TxTime fetch profile registers.

Key local helpers:

- `__ice_vsi_get_qs_contig()` and `__ice_vsi_get_qs_sc()` manipulate PF queue allocation bitmaps under `qs_cfg->qs_mutex`.
- `ice_vsi_alloc_q_vector()` handles vector allocation variants for PF, VF, loopback, and VF control VSIs.
- `ice_setup_tx_ctx()` and `ice_setup_txtime_ctx()` fill CPU-side queue context structs before common-layer packing.
- `ice_setup_rx_ctx()` fills `struct ice_rlan_ctx`, handles DVM/VF VLAN descriptor compatibility, switchdev descriptor selection, RLAN programming, and Rx tail setup.
- `ice_rxq_pp_create()` creates libeth page-pool fill queues, optionally with a separate header-split pool.
- `ice_vsi_cfg_txq()` builds an AdminQ add-Tx-queue group, calls `ice_ena_vsi_txq()`, records firmware TEIDs, and optionally configures a Tx timestamp queue.

## Control Flow

Queue allocation starts with `__ice_vsi_get_qs()`. The driver attempts a contiguous zero region in the PF queue bitmap; if that fails, it lowers `q_count` to `scatter_count`, marks `mapping_mode = ICE_VSI_MAP_SCATTER`, and assigns individual free bits. The scattered rollback path clears bits assigned in the current attempt and zeros corresponding VSI map entries.

Interrupt setup starts with `ice_vsi_alloc_q_vectors()`, which loops over `vsi->num_q_vectors`. `ice_vsi_alloc_q_vector()` creates an `ice_q_vector`, initializes default dynamic ITR state, derives VF register indexes for VF VSIs, reuses a control-VSI interrupt for VF control VSIs where appropriate, or allocates a PF IRQ with `ice_alloc_irq()`. If a netdev already exists, NAPI is registered immediately. Ring-to-vector mapping then distributes remaining Tx and Rx rings over remaining vectors with `DIV_ROUND_UP`, links rings into each vector's Tx/Rx container lists, sets ITR indexes, and maps XDP rings when XDP is enabled.

Rx configuration flows from `ice_vsi_cfg_rxqs()` to `ice_vsi_cfg_rxq()`. PF/SF/LB rings first choose any AF_XDP pool and either register an XSK memory model or create page-pool fill queues and attach the page pool to XDP RXQ metadata. `ice_setup_rx_ctx()` then prepares the RLAN context using ring DMA, descriptor count, buffer size, CRC strip flags, VLAN/DVM behavior, header-split fields, max frame constraints, descriptor prefetch, and switchdev descriptor ID. It writes the hardware context with `ice_write_rxq_ctx()`, then assigns and clears the per-queue tail register for non-VF queues. After context setup, the function posts XSK zero-copy buffers, control-Rx descriptors, or regular Rx buffers.

Tx configuration flows through `ice_vsi_cfg_txqs()` or `ice_vsi_cfg_single_txq()` into `ice_vsi_cfg_txq()`. The ring's XPS mapping is initialized once, `ice_setup_tx_ctx()` fills the TLAN context, `ice_pack_txq_ctx()` packs it into the add-queue buffer, the software queue handle is calculated per TC/channel, and `ice_ena_vsi_txq()` adds the queue into firmware and the scheduler tree. Firmware's queue TEID response is copied back to the ring. If TxTime is enabled, the code allocates a timestamp ring, fills/packs its context, sets the doorbell, and calls `ice_aq_set_txtimeq()`. If timestamp setup fails after the LAN queue was enabled, it frees the timestamp ring and disables the LAN Tx queue to avoid leaving a partially configured queue.

Queue-pair disable in `ice_qp_dis()` synchronizes networking, drops carrier, stops the netdev Tx queue, disables IRQ/NAPI, disables the regular Tx ring and optional XDP Tx ring, requests Rx disable without waiting, cleans all rings, and resets per-ring stats. Queue-pair enable reverses this path by configuring Tx/XDP/Rx rings, programming MSI-X mapping, enabling Rx with a wait, enabling NAPI/IRQ, synchronizing XSK pointer visibility with `synchronize_net()`, and starting the netdev queue if link is up.

## State and Persistence Behavior

Persistent driver state updated here includes:

- PF queue bitmap allocation and VSI `txq_map`/`rxq_map` arrays through `__ice_vsi_get_qs()`.
- `vsi->q_vectors[]`, q-vector interrupt identities, NAPI registration, and ring `q_vector` linked-list membership.
- Ring fields such as `tail`, `q_handle`, `txq_teid`, XDP RXQ registration, page-pool pointers, header-split pool metadata, `xps_state`, and timestamp ring ownership.
- Hardware registers including `GLINT_CTL`, `QINT_TQCTL`, `QINT_RQCTL`, `QRX_CTRL`, `QRX_TAIL`, `QTX_COMM_DBELL`, and E830 TxTime doorbell registers.
- Firmware/scheduler state through `ice_ena_vsi_txq()`, `ice_dis_vsi_txq()`, and `ice_aq_set_txtimeq()`.

The file assumes context ownership is coordinated by the higher-level VSI lifecycle. It takes local locks for PF queue bitmap assignment but generally relies on caller sequencing for ring arrays, NAPI toggles, and queue pair operations.

## Dependencies and Integration Points

Direct dependencies include:

- `ice_common.c` for queue context packing/writes, Tx queue add/remove, TxTime AdminQ, link status, and scheduler-facing queue contexts.
- `ice_lib.c` and related VSI helpers for ring allocation, `ice_qvec_*()` IRQ/NAPI operations, XDP mapping, ring cleaning, and hardware VSI numbers.
- `ice_dcb_lib.h` for DCB traffic class decisions.
- `ice_sriov.h` and VF helpers for VF register indexing, port VLAN behavior, VF control VSI interrupt sharing, and VF-disable checks.
- Linux networking APIs: NAPI, XDP RXQ metadata, AF_XDP pool operations, page-pool/libeth fill queues, XPS, `netif_tx_*`, and carrier state.
- Device registers and AdminQ structures declared in ICE hardware headers.

## Risks and Edge Cases

- The scattered queue allocation rollback clears `qs_cfg->vsi_map[index]` instead of consistently using `index + vsi_map_offset` for the PF bitmap lookup in the first clear operation. The subsequent zeroing uses the offset. Any future changes here should verify rollback against nonzero `vsi_map_offset`.
- `ice_vsi_alloc_q_vectors()` can partially succeed and returns success when at least one vector was allocated, while shrinking `vsi->num_q_vectors`. Callers must tolerate fewer vectors than originally requested.
- `ice_vsi_cfg_rxq()` has multiple setup paths where XDP RXQ metadata, page pools, and XSK pool state must be unwound correctly. Error labels destroy fill queues but do not explicitly unregister every XDP RXQ state in this snippet, so callers and companion cleanup paths matter.
- `ice_vsi_ctrl_one_rx_ring()` does not bounds-check `rxq_idx`; public callers that accept external indexes must validate first.
- Tx timestamp setup is a partial-failure-sensitive path: LAN Tx queue add succeeds before timestamp queue setup. The cleanup path disables the Tx queue, but tests should verify TEID/q_handle state after failure.
- `ice_calc_ts_ring_count()` loops over `ICE_TXTIME_FETCH_PROFILE_CNT` but reads `E830_GLTXTIME_FETCH_PROFILE(prof, 0)` with `prof` fixed to zero. If multiple profiles are expected, this may be deliberate hardware behavior or a latent oversight worth checking against datasheet intent.
- Queue-pair disable asks Rx to stop without waiting, then immediately cleans rings. Higher-level users must ensure no in-flight DMA or polling race remains beyond the IRQ/NAPI disable and `synchronize_net()` ordering.

## Test Signals

Useful validation signals include:

- Build coverage with `CONFIG_DCB`, `CONFIG_XDP_SOCKETS`, SR-IOV, switchdev, and Tx timestamping variants.
- Queue bring-up smoke tests: create PF VSI, enable traffic, enable/disable a single queue pair, and verify no Rx/Tx timeout, NAPI leak, IRQ leak, or page-pool leak.
- AF_XDP zero-copy tests for pool bind/unbind and queue-pair restart paths.
- VF and VF control VSI tests to confirm interrupt sharing and VM/VF queue context fields.
- DCB traffic-class tests to verify `q_handle` calculations and scheduler placement.
- Fault injection for `ice_ena_vsi_txq()`, `ice_aq_set_txtimeq()`, page-pool creation, and buffer allocation failures.
- Register/AdminQ tracing around `QRX_CTRL`, `QINT_*`, Tx queue TEIDs, and scheduler node add/remove during reset and queue-pair operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_base.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_base.h

## Purpose

`ice_base.h` declares the queue-base services implemented in `ice_base.c`. It is the public header for VSI queue allocation, Rx/Tx queue configuration, interrupt mapping, queue-pair enable/disable, Tx queue metadata fill, and TxTime descriptor count calculation.

The header is intentionally thin. It includes `ice.h` for all core driver structures and exports function prototypes rather than defining data structures of its own.

## Important APIs and Types

The declared API groups are:

- Rx queue configuration: `ice_vsi_cfg_single_rxq()`, `ice_vsi_cfg_rxqs()`, `ice_vsi_ctrl_one_rx_ring()`, `ice_vsi_wait_one_rx_ring()`.
- PF queue ID assignment: `__ice_vsi_get_qs()` using `struct ice_qs_cfg`.
- q-vector lifecycle and ring mapping: `ice_vsi_alloc_q_vectors()`, `ice_vsi_map_rings_to_vectors()`, `ice_vsi_free_q_vectors()`.
- Tx queue configuration: `ice_vsi_cfg_single_txq()`, `ice_vsi_cfg_lan_txqs()`, `ice_vsi_cfg_xdp_txqs()`.
- interrupt setup: `ice_cfg_itr()`, `ice_cfg_txq_interrupt()`, `ice_cfg_rxq_interrupt()`, `ice_trigger_sw_intr()`.
- Tx queue stop metadata and operations: `ice_vsi_stop_tx_ring()`, `ice_fill_txq_meta()`.
- queue-pair operations: `ice_qp_ena()`, `ice_qp_dis()`.
- TxTime sizing: `ice_calc_ts_ring_count()`.

Types are not defined here but are central to the API contract: `struct ice_vsi`, `struct ice_qs_cfg`, `struct ice_hw`, `struct ice_q_vector`, `struct ice_tx_ring`, `struct ice_txq_meta`, and `enum ice_disq_rst_src`.

## Control Flow and Integration

This header allows higher-level driver code to sequence queue lifecycle steps without knowing the implementation details in `ice_base.c`. Typical ordering is:

1. Allocate PF queue IDs for a VSI through `__ice_vsi_get_qs()`.
2. Allocate and map q-vectors with `ice_vsi_alloc_q_vectors()` and `ice_vsi_map_rings_to_vectors()`.
3. Configure Tx and Rx rings with `ice_vsi_cfg_lan_txqs()`, `ice_vsi_cfg_xdp_txqs()`, and `ice_vsi_cfg_rxqs()`.
4. Configure MSI-X/ITR using `ice_cfg_itr()`, `ice_cfg_txq_interrupt()`, and `ice_cfg_rxq_interrupt()`.
5. Use `ice_qp_dis()` and `ice_qp_ena()` for dynamic per-queue restarts.

The declarations bridge queue lifecycle callers such as VSI rebuild, netdev open/close, AF_XDP setup, reset recovery, and SR-IOV control paths to the common hardware/AdminQ layer.

## State and Persistence Behavior

Although the header has no storage, its function contracts mutate persistent state in:

- VSI queue maps, ring arrays, ring `q_vector` pointers, and q-vector arrays.
- hardware Rx/Tx queue context registers and queue interrupt registers.
- firmware scheduler state through Tx queue add/remove operations.
- NAPI, IRQ allocation, XDP RXQ registration, page-pool ownership, and netdev queue/carrier state.

Callers should treat these APIs as stateful hardware operations, not pure configuration helpers.

## Dependencies

`ice_base.h` depends on `ice.h` for full type declarations and feature constants. Implementation users also indirectly depend on `ice_common.h`, scheduler/AdminQ declarations, SR-IOV helpers, XDP/page-pool APIs, and Linux netdev/NAPI infrastructure.

## Risks and Contract Notes

- Several functions accept raw queue indexes. Some implementations validate bounds, while others assume caller validation. Public use should check `q_idx`, `rxq_idx`, and ring pointer validity before calling.
- `__ice_vsi_get_qs()` has a double-underscore name but is exported within the driver; callers need to understand its locking and partial queue-count behavior.
- `ice_vsi_alloc_q_vectors()` may adjust `vsi->num_q_vectors` on partial allocation and still return success when at least one vector exists.
- `ice_vsi_stop_tx_ring()` requires correctly populated `struct ice_txq_meta`; callers should use `ice_fill_txq_meta()` unless they have a specific reset-flow reason not to.

## Test Signals

Header-level validation is mostly compile and integration coverage:

- Compile all translation units including `ice_base.h` under relevant feature configs.
- Confirm no prototype drift between `ice_base.h` and `ice_base.c`.
- Exercise callers from VSI open/rebuild, queue-pair restart, AF_XDP queue setup, VF queue setup, and Tx timestamping.
- Static analysis should flag any unchecked raw queue index passed to control or wait functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_common.c

## Purpose

`ice_common.c` is the ICE driver's shared hardware service layer. It implements device identification, reset, control queue command wrappers, hardware initialization/deinitialization, capability discovery/parsing, link/PHY configuration, queue context packing, Tx scheduler queue operations, resource allocation, RSS AdminQ operations, RDMA qset handling, CGU/DPLL/clock access, GPIO/I2C helpers, LLDP helpers, replay after reset, and statistics accumulation.

The file centralizes many operations that are needed by PF, VSI, PTP, switch, scheduler, SR-IOV, and netdev code. It is firmware-facing and register-facing: most public functions either send AdminQ/Sideband Queue commands, read/write device registers, or update long-lived `struct ice_hw` and `struct ice_port_info` state.

## Important APIs, Types, and Functions

Hardware initialization and reset:

- `ice_init_hw()` performs MAC type detection, PF reset, control queue creation, firmware logging setup, PF configuration clear, NVM and capability discovery, port/scheduler initialization, PHY/link discovery, filter management initialization, MAC read, jumbo MAC config, Flow Director resources, hardware tables, tunnel lock setup, firmware load wait, and lane-number discovery.
- `ice_deinit_hw()` frees Flow Director resources, filter management, scheduler state, package/hardware tables, tunnel lock, fwlog, control queues, and VSI contexts.
- `ice_check_reset()`, `ice_reset()`, and local `ice_pf_reset()` poll reset-completion registers and issue PF/core/global resets.
- `ice_clear_pf_cfg()` and `ice_clear_pxe_mode()` clear firmware-side PF/PXE state.

AdminQ and resource wrappers:

- `ice_aq_send_cmd()` serializes most AdminQ commands behind `ice_global_cfg_lock_sw` when firmware's global config lock could block them, then calls retry-capable send logic.
- `ice_sq_send_cmd_retry()` retries selected opcodes on firmware EBUSY after restoring descriptor and buffer state.
- `ice_aq_get_fw_ver()`, `ice_aq_send_driver_ver()`, and `ice_aq_q_shutdown()` wrap basic firmware commands.
- `ice_acquire_res()` and `ice_release_res()` implement firmware resource acquisition/release with polling semantics and special global-config-lock statuses.
- `ice_aq_alloc_free_res()`, `ice_alloc_hw_res()`, and `ice_free_hw_res()` allocate/free firmware resources.
- `ice_sbq_rw_reg()` sends Sideband Queue register read/write messages and backs CGU/FEC access.

Queue context and scheduler APIs:

- `ice_write_rxq_ctx()`, `ice_read_rxq_ctx()`, `ice_pack_txq_ctx()`, `ice_read_txq_ctx()`, `ice_write_txq_ctx()`, and `ice_pack_txtime_ctx()` pack/unpack sparse CPU queue contexts to dense hardware layouts using `linux/packing.h`.
- `ice_ena_vsi_txq()` and `ice_dis_vsi_txq()` add/remove LAN Tx queues in firmware and mirror them in the software scheduler tree.
- `ice_cfg_vsi_lan()`, `ice_cfg_vsi_rdma()`, `ice_ena_vsi_rdma_qset()`, and `ice_dis_vsi_rdma_qset()` configure LAN/RDMA queue capacities and RDMA qsets.
- `ice_aq_cfg_lan_txq()` moves/configures Tx queues through firmware.
- `ice_aq_set_txtimeq()` configures TxTime queue contexts.
- `ice_get_lan_q_ctx()` looks up per-VSI, per-TC queue context entries.

Capability, netlist, and safe-mode APIs:

- `ice_get_caps()`, `ice_discover_dev_caps()`, and local `ice_discover_func_caps()` query and parse firmware capability lists.
- Parsing helpers fill `hw->dev_caps`, `hw->func_caps`, timestamp capability substructures, FDIR limits, valid function bitmaps, NAC topology state, sensor support, RSS/DCB/MSI-X/RDMA/MTU/NVM flags, and queue ranges.
- `ice_set_safe_mode_caps()` overwrites capabilities to a minimal one-Rx/one-Tx-queue, two-MSI-X-vector profile while preserving critical base fields.
- `ice_is_phy_rclk_in_netlist()`, `ice_is_clock_mux_in_netlist()`, `ice_is_cgu_in_netlist()`, and `ice_is_gps_in_netlist()` probe firmware netlist nodes.

Link, PHY, and media APIs:

- `ice_aq_get_phy_caps()`, `ice_aq_set_phy_cfg()`, `ice_update_link_info()`, `ice_aq_get_link_info()`, and `ice_get_link_status()` synchronize PHY/link information into `port_info`.
- `ice_get_media_type()` classifies fiber, BASE-T, direct attach, backplane, or unknown from PHY type and module information.
- `ice_update_phy_type()` maps desired speed bitmaps to PHY type bitmaps; `ice_get_link_speed_based_on_phy_type()` maps a single PHY type to firmware speed; `ice_get_link_speed()` maps firmware speed bit index to Linux `SPEED_*`.
- `ice_caps_to_fc_mode()`, `ice_caps_to_fec_mode()`, `ice_cfg_phy_fc()`, `ice_set_fc()`, `ice_cfg_phy_fec()`, `ice_phy_caps_equals_cfg()`, and `ice_copy_phy_caps_to_cfg()` manage flow control and FEC configuration data.
- `ice_aq_set_link_restart_an()`, `ice_aq_set_event_mask()`, `ice_aq_set_mac_loopback()`, `ice_aq_set_port_id_led()`, `ice_aq_get_port_options()`, `ice_aq_set_port_option()`, `ice_get_phy_lane_number()`, `ice_aq_sff_eeprom()`, `ice_aq_get_phy_equalization()`, and `ice_aq_get_fec_stats()` expose additional link/PHY operations.

RSS, replay, stats, and peripheral APIs:

- `ice_aq_get_rss_lut()`, `ice_aq_set_rss_lut()`, `ice_aq_get_rss_key()`, and `ice_aq_set_rss_key()` get/set RSS tables and keys for valid VSIs.
- `ice_replay_vsi()` and `ice_replay_post()` restore RSS, switch filters, and scheduler aggregation after reset.
- `ice_stat_update40()` and `ice_stat_update32()` accumulate wrapping hardware counters into software counters.
- CGU/DPLL functions include input/output pin config, DPLL status/config/ref priority, CGU info, PHY recovered clock output, and raw CGU register read/write.
- `ice_aq_read_i2c()`, `ice_aq_write_i2c()`, `ice_get_pca9575_handle()`, `ice_read_pca9575_reg()`, `ice_aq_set_gpio()`, and `ice_aq_get_gpio()` access topology-attached I2C/GPIO devices.
- `ice_aq_set_lldp_mib()`, `ice_fw_supports_lldp_fltr_ctrl()`, `ice_lldp_fltr_add_remove()`, and `ice_lldp_execute_pending_mib()` wrap LLDP firmware interactions.
- Firmware version gates include `ice_fw_supports_link_override()`, `ice_fw_supports_report_dflt_cfg()`, and `ice_is_fw_health_report_supported()`.

## Control Flow

The core initialization flow in `ice_init_hw()` is sequential and has explicit unwind labels. It identifies MAC type from PCI IDs, records PF ID, performs PFR, derives ITR/INTRL granularity, creates all control queues, optionally initializes firmware logging on PF0, clears PF config, enables Flow Director, exits PXE mode, initializes NVM, queries device/function capabilities, allocates/initializes `port_info`, reads switch and scheduler configuration, initializes scheduler software state, queries PHY caps/link status, validates scheduler entry point, initializes filter management, reads LAN MAC address, sets max MAC frame size, allocates FDIR counters, initializes hardware tables, initializes tunnel locking and recipe reuse support, waits for external PHY firmware load, and computes lane number. Each failure after an allocation or firmware setup jumps to the appropriate cleanup stage.

AdminQ command flow uses `ice_fill_dflt_direct_cmd_desc()` to initialize descriptors, command-specific wrappers fill descriptor raw parameters, and `ice_aq_send_cmd()` sends through the admin queue. Most commands are serialized by `ice_global_cfg_lock_sw`; package download and a few package/VLAN/scheduler/recipe commands are allowed through while the global firmware config lock may be held. Selected opcodes retry on `LIBIE_AQ_RC_EBUSY`.

Rx/Tx queue context flow uses packed-field tables. Sparse structs (`ice_rlan_ctx`, `ice_tlan_ctx`, `ice_txtime_ctx`) are packed little-endian with LSW32-first ordering. Rx contexts are written directly to `QRX_CONTEXT` registers. Full Tx contexts use the global Tx context command/data registers protected by `pf->adapter->txq_ctx_lock` because the interface is shared by PFs. Short TLAN contexts are also packed into AdminQ add-queue buffers for scheduler queue creation.

LAN Tx queue enable flow in `ice_ena_vsi_txq()` validates `port_state`, VSI handle, group size, and queue context, then locks `pi->sched_lock`. It finds a free scheduler parent, fills default generic/CIR/EIR scheduling sections, sends `ice_aq_add_lan_txq()`, records the queue handle and TEID in software, adds the leaf scheduler node, and replays any queue bandwidth profile. Disable flow finds scheduler nodes by TEID, validates queue contexts, sends `ice_aq_dis_lan_txq()`, frees scheduler nodes, and invalidates software queue context fields.

Capability discovery sends list-capabilities AdminQ commands with a maximum 4 KiB buffer, then dispatches each returned element through common, function-specific, or device-specific parsers. Device capability parsing must precede function capability parsing because port-limited recalculation uses `hw->dev_caps.num_funcs`.

Link update flow uses `ice_aq_get_link_info()` to refresh current and previous link status, media type, flow-control mode, FEC, pacing, LSE state, and frame size. `ice_update_link_info()` optionally refreshes PHY caps when media is available. `ice_set_fc()` reads active PHY config, copies it to set-config shape, mutates pause bits, optionally requests automatic link update, writes the config, and retries link-status refresh up to ten times.

Reset replay starts with `ice_replay_vsi()` on the main VSI, which moves existing switch rules into replay lists and preps scheduler aggregation replay. Each VSI replay restores RSS config, filters, and aggregator state. `ice_replay_post()` then drops stale replay rules and finalizes aggregation replay.

## State and Persistence Behavior

This file updates durable driver and hardware state across several layers:

- `struct ice_hw`: MAC type, PF ID, logical PF ID, firmware/API version, NVM state, dev/func capabilities, switch info, port info, FDIR counter base, hardware tables, tunnel lock, fwlog state, CGU part number, cached IO expander handle, lane number, scheduler layer data, and package/segment state.
- `struct ice_port_info`: link information, old link information, media type, FC current/requested state, local forwarding mode, scheduler xarray, scheduler lock/tree, and PHY cached user requests.
- firmware state: PF configuration, PXE ownership, MAC config, port params, PHY config, event masks, LLDP MIB/filter state, health event config, Tx/RDMA queue scheduler nodes, RSS LUT/key, resource ownership, CGU/DPLL/pin config, GPIO/I2C/SFF state, and port options.
- hardware registers: reset triggers/status, queue context registers, Tx context shared command/data registers, statistics registers, power/ITR granularity source registers, MAC pause timer/threshold registers, sideband-addressed CGU/FEC registers.
- software replay/filter/scheduler lists, including switch recipe filter lists and replay lists.

The code has both volatile and persistent effects. Some settings are runtime-only and replayed after reset; others are firmware/NVM-adjacent, such as MAC address writes, port options, and link default override reads. Callers must distinguish read-only status wrappers from mutating firmware commands.

## Dependencies and Integration Points

Major dependencies include:

- Control queue infrastructure from `ice_controlq`/`libie`, including `struct libie_aq_desc`, AdminQ status, descriptor flags, and command opcodes from `ice_adminq_cmd.h`.
- Scheduler APIs from `ice_sched.h`, including scheduler tree initialization, resource queries, parent selection, node add/free, bandwidth replay, aggregation replay, and queue capacity configuration.
- Switch/filter APIs from `ice_switch.h` and related filter replay/removal helpers.
- NVM and package helpers from `ice_nvm.h`, flex-pipe/package code, parser code, and flow/FDIR helpers.
- PTP/clock hardware definitions from `ice_ptp_hw.h` and CGU/Sideband Queue device IDs.
- Linux APIs: `packing.h`, bitfield helpers, xarray, mutex/spinlock primitives, memory allocation, jiffies/polling helpers, endian helpers, PCI IDs, netdev speed constants, and device-managed allocation.
- `ice_base.c` depends on this file for queue context writes, Tx queue AdminQ operations, TxTime setup, and link status checks.
- SR-IOV/RDMA/PTP/LLDP/devlink/ethtool flows depend on exported helpers from this file.

## Risks and Edge Cases

- `ice_pf_reset()` compares `cnt == ICE_PF_RESET_WAIT_COUNT` after a loop whose bound is `ICE_GLOBAL_CFG_LOCK_TIMEOUT + ICE_PF_RESET_WAIT_COUNT`. If `ICE_GLOBAL_CFG_LOCK_TIMEOUT` is nonzero, the timeout check may not match the actual loop bound. This warrants review against intended timeout semantics.
- `ice_aq_send_cmd()` relies on a software mutex to reduce commands sent during global config lock ownership, but the comment notes it does not prevent all command types. Any new AdminQ wrapper must be classified carefully.
- AdminQ retry copies the indirect buffer only when retrying selected commands. New retryable opcodes with output-mutating buffers must be added to `ice_should_retry_sq_send_cmd()`.
- Several getters write to output pointers without checking all of them for NULL, such as some CGU/DPLL helpers. Callers must satisfy implicit non-NULL contracts.
- `ice_get_link_speed_based_on_phy_type()` expects exactly one PHY-type bit across low/high; callers passing multi-bit masks receive unknown. This is correct for documented use but easy to misuse.
- Link/FEC/FC configuration combines firmware support gates, default-config reporting, link override TLVs, auto-link-update bits, and cached user requests. Regression risk is high around old firmware versions.
- Queue context packing tables are bit-position-sensitive. Any struct layout change or hardware definition update requires tests or static assertions against expected packed bytes/registers.
- Tx context register access is protected by `txq_ctx_lock`; Rx context register access is not similarly locked, implying callers should avoid concurrent writes to the same Rx queue context.
- Scheduler queue operations require `ICE_SCHED_PORT_STATE_READY`; callers during reset/rebuild can see `-EIO` and must handle retry or abort.
- `ice_set_safe_mode_caps()` preserves only selected capability fields. New required base capabilities may need explicit restore there.
- Topology/netlist probing assumes maximum scan size `ICE_MAX_NETLIST_SIZE` and specific node part numbers. New boards may require updates.
- `ice_aq_write_i2c()` documents data sizes inconsistently with its check and copies `data` without a NULL check. Callers must pass valid data even for small writes.

## Test Signals

High-value validation signals include:

- Probe/remove and reset tests across E810, E82x/E823, E825, E830/E835 PCI IDs, including PF0 and non-PF0 firmware logging paths.
- Fault injection for every `ice_init_hw()` stage to verify unwind paths do not leak control queues, scheduler state, filter structures, port info, or hardware tables.
- AdminQ tests that simulate EBUSY for retryable opcodes and global-config-lock contention for blocked opcodes.
- Capability parser tests using synthetic list-capability buffers for common, device, function, timestamp, FDIR, NAC, sensor, RDMA, multi-port, and safe-mode behavior.
- Queue context pack/unpack golden tests for RLAN, TLAN, and TxTime fields.
- Scheduler tests for LAN queue add/remove, RDMA qset add/remove, reset-flow disable with no queue group, and queue bandwidth replay.
- Link tests for media classification, single-bit and multi-bit PHY speed mapping, FC/FEC conversion, firmware-version-gated default config/link override, and old firmware fallback.
- RSS LUT/key get/set tests validating VSI-handle checks and LUT size/type constraints.
- PTP/CGU tests for dual-complex E825 destination selection, DPLL status sign extension, pin config round trips, and CGU register SBQ failures.
- I2C/GPIO/SFF tests for invalid lengths, absent PCA9575 topology, cached handle behavior, and AQ failure propagation.
- Replay tests after reset verifying RSS, filters, and aggregation state are restored and stale replay lists are cleaned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_common.h

## Purpose

`ice_common.h` declares the ICE shared hardware service API implemented mostly by `ice_common.c`. It exposes initialization/reset, control queue, AdminQ wrappers, queue context packing, RSS, capability discovery, PHY/link management, scheduler queue operations, RDMA qsets, CGU/DPLL/clock helpers, statistics helpers, GPIO/I2C, LLDP, firmware feature gates, and low-level CGU register access.

The header is the broad integration contract for many ICE driver subsystems. It also defines small constants for AdminQ retry behavior, FEC sideband register offsets, and CGU register bitfields used by PTP/clock code.

## Important APIs, Types, and Constants

Constants:

- `ICE_SQ_SEND_DELAY_TIME_MS` and `ICE_SQ_SEND_MAX_EXECUTE` define retry delay/count for selected AdminQ send retries.
- FEC register and receiver ID constants define sideband register offsets for corrected/uncorrected FEC counters across ports and PCS receivers.
- `ICE_CGU_*` register offsets and masks define CGU PLL, reference, lock, counter, and bandwidth-monitor fields.

Initialization and control queues:

- `ice_init_hw()`, `ice_deinit_hw()`, `ice_check_reset()`, `ice_reset()`.
- `ice_create_all_ctrlq()`, `ice_init_all_ctrlq()`, `ice_shutdown_all_ctrlq()`, `ice_destroy_all_ctrlq()`, `ice_clean_rq_elem()`.
- `ice_sq_send_cmd()`, `ice_aq_send_cmd()`, `ice_fill_dflt_direct_cmd_desc()`, `ice_check_sq_alive()`.

Resource and capability APIs:

- `ice_acquire_res()`, `ice_release_res()`, `ice_aq_alloc_free_res()`, `ice_alloc_hw_res()`, `ice_free_hw_res()`.
- `ice_get_caps()`, `ice_discover_dev_caps()`, `ice_set_safe_mode_caps()`, `ice_aq_list_caps()`.
- Netlist probes: `ice_is_phy_rclk_in_netlist()`, `ice_is_clock_mux_in_netlist()`, `ice_is_cgu_in_netlist()`, `ice_is_gps_in_netlist()`, `ice_aq_get_netlist_node()`.

Queue context, RSS, and scheduler APIs:

- `ice_write_rxq_ctx()`, `ice_read_rxq_ctx()`, `ice_read_txq_ctx()`, `ice_write_txq_ctx()`, `ice_pack_txq_ctx()`, `ice_pack_txtime_ctx()`.
- `ice_aq_get_rss_lut()`, `ice_aq_set_rss_lut()`, `ice_aq_get_rss_key()`, `ice_aq_set_rss_key()`.
- `ice_cfg_vsi_lan()`, `ice_ena_vsi_txq()`, `ice_dis_vsi_txq()`, `ice_aq_cfg_lan_txq()`, `ice_get_lan_q_ctx()`, `ice_aq_set_txtimeq()`.
- RDMA: `ice_cfg_vsi_rdma()`, `ice_ena_vsi_rdma_qset()`, `ice_dis_vsi_rdma_qset()`.
- Replay: `ice_replay_vsi()`, `ice_replay_post()`.

Link, PHY, and port APIs:

- `ice_get_link_status()`, `ice_update_link_info()`, `ice_aq_get_link_info()`, `ice_aq_get_phy_caps()`, `ice_aq_set_phy_cfg()`.
- `ice_update_phy_type()`, `ice_get_link_speed_based_on_phy_type()`, `ice_get_link_speed()`, `ice_is_100m_speed_supported()`.
- `ice_caps_to_fc_mode()`, `ice_caps_to_fec_mode()`, `ice_set_fc()`, `ice_cfg_phy_fc()`, `ice_phy_caps_equals_cfg()`, `ice_copy_phy_caps_to_cfg()`, `ice_cfg_phy_fec()`.
- `ice_aq_set_link_restart_an()`, `ice_aq_set_mac_cfg()`, `ice_aq_set_event_mask()`, `ice_aq_set_mac_loopback()`, `ice_aq_set_port_id_led()`, `ice_aq_get_port_options()`, `ice_aq_set_port_option()`, `ice_get_phy_lane_number()`, `ice_aq_sff_eeprom()`.
- `ice_aq_get_phy_equalization()` and `ice_aq_get_fec_stats()`.

Clock, peripheral, LLDP, and miscellaneous APIs:

- CGU/DPLL: input/output pin measure/config, DPLL status/config/ref priority, CGU info, recovered clock output, sensor reading, `ice_read_cgu_reg()`, `ice_write_cgu_reg()`.
- Stats: `ice_stat_update40()`, `ice_stat_update32()`.
- Scheduler query: `ice_sched_query_elem()`.
- GPIO/I2C: `ice_aq_set_gpio()`, `ice_aq_get_gpio()`, `ice_aq_read_i2c()`, `ice_aq_write_i2c()`, `ice_get_pca9575_handle()`, `ice_read_pca9575_reg()`.
- Firmware feature gates: `ice_fw_supports_link_override()`, `ice_is_fw_health_report_supported()`, `ice_fw_supports_lldp_fltr_ctrl()`, `ice_fw_supports_report_dflt_cfg()`.
- LLDP: `ice_aq_set_lldp_mib()`, `ice_lldp_fltr_add_remove()`, `ice_lldp_execute_pending_mib()`.

The header also declares `extern struct mutex ice_global_cfg_lock_sw`, the software-side serialization companion for firmware global configuration lock behavior.

## Control Flow and Integration

Subsystems include this header when they need firmware or hardware services but do not own the lower-level command details. For example:

- Probe and teardown code use init/deinit/reset/control queue declarations.
- Queue setup code uses Rx/Tx context writes, Tx queue add/remove, TxTime queue setup, and scheduler configuration.
- ethtool/devlink/netdev paths use link status, PHY caps, FEC/FC conversion, port options, SFF EEPROM, sensor, GPIO, and statistics helpers.
- PTP/DPLL code uses CGU register and DPLL/pin APIs plus CGU bit masks.
- SR-IOV and RDMA code use capability, resource, scheduler, and queue/qset helpers.
- Reset rebuild uses replay declarations to restore filters, RSS, and scheduler aggregation.

The header intentionally exposes AdminQ and SBQ abstractions rather than raw register sequences for most operations. Callers are expected to pass valid ICE core structures and to understand whether a function is read-only, runtime-mutating, or firmware/NVM-affecting.

## State and Persistence Behavior

The header has no state itself except exported constants and the global mutex declaration, but its APIs represent operations that mutate:

- `struct ice_hw` capability/version/NVM/scheduler/filter/tunnel/fwlog state.
- `struct ice_port_info` link, PHY, FC/FEC, local forwarding, scheduler, and cached user-request state.
- queue contexts in hardware registers and firmware scheduler nodes.
- firmware-owned resources, MAC/PHY/port/LLDP/RSS/CGU/GPIO/I2C/DPLL state.
- software replay lists, stats accumulation baselines, and cached topology handles.

The presence of both getters and setters with similar names means call sites should be explicit about side effects. `ice_aq_get_*` functions usually read firmware state but may also cache output into `hw` or `port_info`; `ice_aq_set_*` functions generally mutate firmware or hardware state.

## Dependencies

`ice_common.h` includes:

- Linux `bitfield.h` for `GENMASK`, `BIT`, and field helper constants.
- Core ICE headers: `ice.h`, `ice_type.h`, `ice_nvm.h`, `ice_flex_pipe.h`, `ice_parser.h`, `ice_switch.h`, and `ice_fdir.h`.
- `linux/avf/virtchnl.h` for virtualization-related shared definitions.

Implementation dependencies extend to AdminQ command definitions, scheduler, PTP hardware definitions, packing helpers, libie control queue/firmware logging APIs, and Linux networking/PCI/endian primitives.

## Risks and Contract Notes

- This is a high-fanout header. Prototype or type changes can break many ICE subsystems, so changes should be source-compatible or staged carefully.
- Many functions return negative errno values but also rely on `hw->adminq.sq_last_status` for firmware-specific detail. Callers that log or branch on firmware cause need both.
- Output pointer nullability varies by function. Some APIs allow optional outputs; others assume non-NULL. The header does not annotate this, so implementation comments and call sites matter.
- Firmware feature-gate helpers must be used before newer AQ commands or report modes. Bypassing them risks `-EINVAL`, firmware rejection, or incorrect fallback behavior on older NVM/API combinations.
- Queue/scheduler APIs assume valid VSI handles and `ICE_SCHED_PORT_STATE_READY`. Reset paths must handle transient `-EIO`/`-EINVAL`.
- CGU/FEC constants are hardware-generation-sensitive. PTP and diagnostics changes should verify that register masks apply to the target MAC type and topology.
- The exported `ice_global_cfg_lock_sw` mutex is a shared serialization primitive; new direct users should avoid deadlocks with AdminQ wrappers that already acquire it.

## Test Signals

Useful header/API validation includes:

- Full driver compile coverage across feature configs using this header: DCB, SR-IOV, RDMA, PTP/DPLL, LLDP, XDP, and safe mode.
- ABI/prototype consistency checks between `ice_common.h` and `ice_common.c`.
- Static analysis for unchecked NULL output pointers and invalid VSI/queue indexes before calls.
- Integration tests for each API group: init/reset, AdminQ/resource, queue context, scheduler, RSS, link/PHY/FEC/FC, CGU/DPLL, GPIO/I2C/SFF, LLDP, stats, and replay.
- Firmware matrix tests against old and new API versions to validate feature-gated declarations are used correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_common.h -->
