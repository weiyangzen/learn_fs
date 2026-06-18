# subset-b-004477 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp_hw.c

## Purpose

`ice_ptp_hw.c` is the low-level PTP, PHC, PHY timer, timestamp-memory, SMA/GPIO, and CGU/DPLL hardware access layer for Intel `ice` devices. It translates common PTP operations from `ice_ptp.c` and related driver code into register writes, sideband queue transactions, and family-specific calibration flows for E810, E822/E823, E825C/ETH56G, and E830 hardware. The file is hardware-stateful: most functions prepare shadow registers, program PHY blocks, and then execute synchronized timer commands so source timers and port timers change together.

## Important APIs, Types, And Functions

The public device-agnostic entry points are `ice_ptp_init_hw`, `ice_ptp_init_phc`, `ice_ptp_init_time`, `ice_ptp_write_incval`, `ice_ptp_write_incval_locked`, `ice_ptp_adj_clock`, `ice_read_phy_tstamp`, `ice_clear_phy_tstamp`, `ice_get_phy_tx_tstamp_ready`, `ice_check_phy_tx_tstamp_ready`, `ice_ptp_reset_ts_memory`, `ice_ptp_one_port_cmd`, `ice_ptp_lock`, `ice_ptp_unlock`, and `ice_get_ptp_src_clock_index`.

Family-specific exported helpers include E82x calibration and interrupt APIs (`ice_stop_phy_timer_e82x`, `ice_start_phy_timer_e82x`, `ice_phy_cfg_tx_offset_e82x`, `ice_phy_cfg_rx_offset_e82x`, `ice_phy_cfg_intr_e82x`, `ice_ptp_clear_phy_offset_ready_e82x`, quad register helpers), E825C/ETH56G APIs (`ice_stop_phy_timer_eth56g`, `ice_start_phy_timer_eth56g`, `ice_phy_cfg_intr_eth56g`, `ice_phy_cfg_ptp_1step_eth56g`, `ice_ptp_phy_soft_reset_eth56g`, `ice_ptp_read_tx_hwtstamp_status_eth56g`), and E810 CGU/SMA APIs (`ice_read_sma_ctrl`, `ice_write_sma_ctrl`, `ice_ptp_read_sdp_ac`, `ice_cgu_get_num_pins`, `ice_cgu_get_pin_type`, `ice_cgu_get_pin_freq_supp`, `ice_cgu_get_pin_name`, `ice_get_cgu_state`, `ice_get_cgu_rclk_pin_info`, `ice_cgu_get_output_pin_state_caps`).

Core dispatch is keyed by `hw->mac_type`: `ICE_MAC_E810`, `ICE_MAC_E830`, `ICE_MAC_GENERIC` for E82x/E823, and `ICE_MAC_GENERIC_3K_E825` for ETH56G. The code also uses `hw->device_id`, `hw->cgu_part_number`, `hw->func_caps.ts_func_info`, `hw->ptp`, and link state from `hw->port_info->phy.link_info`.

## Control Flow

PTP timer commands follow a common pattern. `ice_ptp_init_time`, `ice_ptp_write_incval`, or `ice_ptp_adj_clock` first write source timer shadow registers such as `GLTSYN_SHTIME_*` or `GLTSYN_SHADJ_*`. They then call family-specific PHY preparation helpers to write matching PHY shadow registers. Finally `ice_ptp_tmr_cmd` calls `ice_ptp_src_cmd`, `ice_ptp_port_cmd`, and `ice_ptp_exec_tmr_cmd` so source and PHY timers apply the command synchronously through `GLTSYN_CMD_SYNC`.

`ice_ptp_src_cmd` and `ice_ptp_exec_tmr_cmd` route non-primary functions to the primary hardware where needed. `ice_ptp_exec_tmr_cmd` serializes access to `GLTSYN_CMD_SYNC` with `pf->adapter->ptp_gltsyn_time_lock`. Wider PTP operations that cannot overlap use the hardware semaphore implemented by `ice_ptp_lock` and `ice_ptp_unlock` through `PFTSYN_SEM`.

For E82x, `ice_start_phy_timer_e82x` stops the PHY timer, configures lane type, UI conversion, PAR/PCS conversion, programs TIMETUS from current source incval, issues `ICE_PTP_INIT_INCVAL`, toggles `P_REG_PS` reset/start/clock/load bits, executes sync commands, and finally calls `ice_sync_phy_timer_e82x`. Vernier calibration is completed later by `ice_phy_cfg_tx_offset_e82x` and `ice_phy_cfg_rx_offset_e82x`, which poll offset-valid registers, calculate fixed and measured offsets, write total offsets, and mark `P_REG_TX_OR`/`P_REG_RX_OR` ready.

For ETH56G/E825C, `ice_start_phy_timer_eth56g` stops timestamp readiness, configures PAR/PCS, one-step PTP, MAC TSU config, writes incval into `PHY_REG_TIMETUS_*`, issues init-incval for the port, syncs the PHY timer against the PHC, and sets Tx/Rx offset-ready registers. ETH56G also supports sideband access to PTP, memory, XPCS, MAC, and GPCS resource spaces, one-step peer delay, bitslip/deskew offset computation, timestamp interrupt status, and PHY soft reset.

For E810, the code accesses an external PHY over SBQ, or through low-latency firmware proxy registers when capabilities advertise low-latency timestamp read or timer update. E810 PHC init enables PHY time sync with `ETH_GLTSYN_ENA`, timestamp reads come from external PHY timestamp banks, and PHY commands are written through `E810_ETH_GLTSYN_CMD`. E830 is simpler for several operations: PHC time and incval are written directly, timestamp readiness is read from E830 MAC registers, and port commands use `E830_ETH_GLTSYN_CMD`.

CGU/DPLL control flow is table-driven. Device IDs select board-specific pin description arrays. `ice_get_cgu_state` fetches raw DPLL status from firmware, maps it to Linux DPLL lock states, and preserves holdover semantics based on the previously reported state. Recovered clock pin discovery is device-specific and may inspect E810 C827 topology.

## State And Persistence Behavior

The file persists no disk state. It mutates device state in MMIO registers, PHY registers reachable through sideband queue messages, NVM-read-derived configuration, GPIO expanders, timestamp memory banks, PHY offset-ready flags, and DPLL state reported by firmware. Timestamp memory is explicitly reset for E82x quads and ETH56G ports; E810 reset is a no-op in the generic reset entry point.

`hw->ptp` stores family parameters such as number of logical ports, ports per PHY, ETH56G one-step flags, peer delay, SFD mode, and E810 low-latency waitqueue state. `hw->func_caps.ts_func_info` determines the owned and associated PHC timer indices. E82x `time_ref` in capabilities is mutable through inline helpers in the header and feeds PLL frequency/incval calculations.

Concurrency state is important. `PFTSYN_SEM` is a hardware semaphore, `ptp_gltsyn_time_lock` serializes sync-command writes, and E810 low-latency proxy access waits on `ptp.phy.e810.atqbal_wq` while `ATQBAL_FLAGS_INTR_IN_PROGRESS` is set. Failure to respect these locks risks corrupt timer updates or racing firmware-assisted timestamp reads.

## Dependencies And Integration Points

The file depends on `ice_common.h` for register helpers, admin queue helpers, NVM/GPIO/CGU commands, and `ice_sbq_rw_reg`; on `ice_ptp_hw.h` for exported prototypes and register macros; and on `ice_ptp_consts.h` for timing and calibration tables such as `e82x_time_ref`, `e822_vernier`, `eth56g_phy_res`, and `eth56g_mac_cfg`.

Main callers are PTP control code in `ice_ptp.c`, timestamp transmit/interrupt paths, E82x calibration work, DPLL integration, and board feature code for SMA/SDP/recovered clock support. The sideband message ABI is defined by `ice_sbq_cmd.h` and implemented in `ice_common.c`. The representor code is separate but shares normal driver infrastructure, while PTP hooks integrate with device capabilities, link topology, and firmware/admin queue paths.

## Risks And Edge Cases

The largest risk is hardware-family divergence. E810, E830, E82x, and ETH56G differ in timestamp layout, command registers, PHY access mechanism, valid-bit behavior, and shadow-register semantics. A generic entry point must route to the correct implementation or return `-EOPNOTSUPP`.

Timer updates are sensitive to ordering. Source and PHY shadow registers must be prepared before the sync command, and stale port commands are avoided by `ice_ptp_one_port_cmd` programming non-target ports to `ICE_PTP_NOP`. Bugs here can desynchronize PHC and PHY timers or apply old commands to unrelated ports.

Calibration arithmetic is overflow-prone. The E82x Vernier functions intentionally divide before multiplying in several places. ETH56G fixed-point Q9 offset logic masks and combines integer/fractional fields. Small mistakes in masks, shifts, link-speed classification, FEC handling, or PMD alignment can cause timestamp bias without obvious functional failures.

Sideband and firmware paths can fail or time out. Many functions propagate errors from `ice_sbq_rw_reg`, NVM reads, GPIO access, and `read_poll_timeout*`; callers must handle `-EBUSY`, `-EINVAL`, `-EIO`, and `-EOPNOTSUPP`. E82x Tx/Rx offset calibration can legitimately return `-EBUSY` until packets have exercised the PHY.

## Test Signals

Useful signals include PHC initialization success for every supported `mac_type`, successful `ice_ptp_init_time`/`ice_ptp_write_incval`/`ice_ptp_adj_clock` cycles, absence of Tx/Rx PHY timer mismatch warnings after sync, E82x offset calibration eventually logging completion after traffic, correct `ice_get_phy_tx_tstamp_ready` bitmaps by family, timestamp reads clearing/reusing memory indices, and DPLL pin enumeration matching the board. Fault injection around SBQ, NVM, low-latency proxy timeouts, invalid ports/quads, and unsupported device IDs should return documented errors without leaving locks held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp_hw.h

## Purpose

`ice_ptp_hw.h` is the public and private contract for the `ice` PTP hardware layer. It declares timer command enums, link-speed/FEC enums, calibration data structures, DPLL/CGU pin descriptors, exported PTP hardware APIs, inline E82x time-reference helpers, family-specific APIs, and a large set of register offsets and bit masks used by `ice_ptp_hw.c`.

## Important APIs, Types, And Constants

`enum ice_ptp_tmr_cmd` defines the abstract timer commands consumed by the C file: init time, init incval, adjust time, adjust-at-time, read time, and no-op. `enum ice_ptp_serdes`, `enum ice_ptp_link_spd`, `enum ice_ptp_fec_mode`, and `enum ice_eth56g_link_spd` normalize hardware link encodings for calibration logic.

`struct ice_time_ref_info_e82x` maps E82x TIME_REF choices to PLL frequency and nominal incval. `struct ice_vernier_info_e82x` stores E82x Vernier calibration frequencies and fixed delays. `struct ice_eth56g_mac_reg_cfg` stores ETH56G MAC TSU mode, delay, fixed-point offset, and one-step/SFD parameters. `struct ice_cgu_pin_desc` backs DPLL pin discovery.

The header declares the common API used outside the hardware file: `ice_ptp_init_hw`, `ice_ptp_init_phc`, `ice_ptp_init_time`, `ice_ptp_write_incval`, `ice_ptp_write_incval_locked`, `ice_ptp_adj_clock`, timestamp read/clear/readiness helpers, and CGU/SMA helpers. It also declares E82x and ETH56G family functions needed by other driver modules.

The register section defines source timer command bits (`GLTSYN_CMD_*`), PHY command bits (`PHY_CMD_*`), sync command values, E82x quad/port register offsets, E810/E830 GLTSYN offsets, low-latency proxy fields, timestamp-bank address macros, SMA GPIO masks, and ETH56G PHY/MAC/quad register offsets.

## Control Flow Role

The header does not execute control flow, but it encodes the control decisions used by `ice_ptp_hw.c`. `ice_get_base_incval` selects a nominal source increment value based on `hw->mac_type`. Inline E82x helpers get and set `hw->func_caps.ts_func_info.time_ref`, and derive PLL frequency/incval from exported calibration tables.

Register macros keep the C file from hard-coding family-specific offsets. For example, E82x timestamp memory uses `Q_REG_TX_MEMORY_*` and `TS_L`/`TS_H`, E810 external PHY access uses `TS_EXT`, and ETH56G resource spaces use `PHY_*` offsets and one-step PTP masks.

## State And Persistence Behavior

The header itself has no runtime state. Its types describe state stored elsewhere: `hw->ptp`, PHY calibration tables, DPLL pin descriptors, and hardware register fields. The `extern` calibration tables must remain consistent with the enum ordering in this header, especially `NUM_ICE_PTP_LNK_SPD`, `NUM_ICE_ETH56G_LNK_SPD`, and `NUM_ETH56G_PHY_RES`.

## Dependencies And Integration Points

The header includes `<linux/dpll.h>` for DPLL pin types, frequencies, lock status, and pin capability bits. It is included by PTP implementation files, common device code, TSPLL code, and other modules that need hardware-level PTP operations. It relies on register helper macros from the broader `ice` driver, such as `BIT`, `GENMASK`, `FIELD_PREP`, `ICE_M`, and hardware register names declared in other generated or shared headers.

## Risks And Edge Cases

Enum ordering is part of the ABI between tables and code. Adding a link speed, resource type, or TIME_REF without updating tables can silently index the wrong calibration constants. Masks for 40-bit and 64-bit timestamp layouts differ by family; using `PHY_EXT_40B_*` where `PHY_40B_*` is expected, or vice versa, will corrupt timestamps. Duplicate C827 handle defines are present and should remain consistent if edited.

## Test Signals

Compile coverage is the first signal: all prototypes must match `ice_ptp_hw.c`, and all macros must resolve against the target kernel tree. Runtime signals include correct base incval selection for E810/E830/E82x/E825, successful DPLL pin enumeration, and timestamp values whose high/low parts match the expected family layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ptp_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_repr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_repr.c

## Purpose

`ice_repr.c` implements port representor netdevices for the `ice` switchdev/eswitch model. It creates VF and SF representors, registers their netdev operations, reports stats, wires TC flower offload callbacks to the represented VSI, coordinates devlink port lifetime, and starts/stops representor queues. The representor is the host-visible netdevice used to steer traffic and offloads for a VF or SF through the PF eswitch.

## Important APIs, Types, And Functions

Public functions are `ice_repr_create_vf`, `ice_repr_create_sf`, `ice_repr_destroy`, `ice_repr_start_tx_queues`, `ice_repr_stop_tx_queues`, `ice_netdev_to_repr`, `ice_is_port_repr_netdev`, `ice_repr_inc_tx_stats`, `ice_repr_inc_rx_stats`, and `ice_repr_get`.

The main internal lifecycle functions are `ice_repr_create`, `ice_repr_add_vf`, `ice_repr_add_sf`, `ice_repr_rem_vf`, `ice_repr_rem_sf`, `ice_repr_reg_netdev`, `ice_repr_ready_vf`, and `ice_repr_ready_sf`. Netdev operations are split between VF and SF tables but share stats, xmit, TC setup, and offload stat operations. VF open/stop also forces VF link state and notifies the VF through virtchnl; SF open/stop only controls carrier and queues.

Stats are split between hardware VSI stats (`ice_repr_get_stats64`) and CPU-hit slow-path per-CPU stats (`ice_repr_sp_stats64`). `ice_repr_inc_tx_stats` records transmit success/bytes or drops based on `NET_XMIT_SUCCESS`/`NET_XMIT_CN`; `ice_repr_inc_rx_stats` increments receive slow-path stats for a representor netdev.

## Control Flow

Creation starts with `ice_repr_create`, which allocates `struct ice_repr`, an Ethernet netdev with `struct ice_netdev_priv`, per-CPU stats, fills `src_vsi`, derives `id` from `vsi_num`, stores the back pointer in netdev private data, sets MTU bounds, and binds the netdev device to the PF device.

`ice_repr_create_vf` resolves the VF VSI, calls the generic creator, sets type, VF pointer, add/remove/ready ops, and parent MAC. `ice_repr_add_vf` then creates a devlink VF port, binds it to the netdev, registers the netdev, drops VF Tx LLDP, configures the VSI for eswitch operation, switches virtchnl ops to representor mode, and initializes devlink rate topology if ADQ/DCB allow it. Error unwind reverses these steps in order.

`ice_repr_create_sf` mirrors the VF path for a dynamic port, but without VF link forcing, LLDP handling, or virtchnl ops. `ice_repr_add_sf` creates a devlink SF port, registers the netdev, and publishes rate topology.

TC setup enters through `ndo_setup_tc`, registers a flow block callback, and passes flower replace/destroy operations to `ice_add_cls_flower` or `ice_del_cls_flower` with the represented VSI. Data-plane transmit uses `ice_eswitch_port_start_xmit`, and receive/transmit slow-path stats are updated from eswitch/TxRx integration points.

## State And Persistence Behavior

The file persists no disk state. Runtime state lives in `struct ice_repr`, the allocated netdev, per-CPU stats, devlink port objects, `pf->eswitch.reprs` xarray entries owned by eswitch code, represented VF/SF state, and VSI eswitch configuration. VF representor open/stop mutates `vf->link_forced` and `vf->link_up` and sends virtchnl notifications.

Stats use `u64_stats_sync` for lockless per-CPU reads. `ice_repr_destroy` releases per-CPU stats, netdev, and the representor object; callers must have already detached/unregistered via the `ops.rem` path where appropriate.

## Dependencies And Integration Points

The implementation depends on `ice.h`, `ice_lib.h`, `ice_eswitch.h`, devlink port helpers, SR-IOV, TC flower helpers, and DCB/ADQ state helpers. It is called by `ice_eswitch.c` for attach/detach, by bridge/eswitch code for repr lookup, by TxRx/eswitch datapaths for stats and xmit, and by ethtool representor ops through `ice_set_ethtool_repr_ops`.

## Risks And Edge Cases

The biggest risks are lifecycle ordering and unwind correctness. VF add must undo devlink port creation, netdev registration, LLDP policy, VSI eswitch config, and virtchnl mode in the right order. `ice_repr_get_stats64` returns early when `repr->ops.ready(repr)` is true, so the ready callback polarity must be understood by callers. `ice_is_port_repr_netdev` identifies representors by exact netdev ops pointer equality, so alternate ops tables would need explicit handling.

TC callback private data assumes `netdev_priv(dev)->repr` is valid for the duration of flow block registration. Stats code assumes `repr->stats` exists until no datapath users can update it.

## Test Signals

Useful signals include successful VF and SF representor creation/destruction under switchdev, correct devlink port publication, netdev open/stop updating carrier and VF link notification where expected, `tc flower` replace/destroy reaching the represented VSI, CPU-hit offload stats increasing under slow-path traffic, xmit drops counted when `ice_eswitch_port_start_xmit` fails, and clean error unwind under injected failures at devlink/netdev/LLDP/VSI configuration steps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_repr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_repr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_repr.h

## Purpose

`ice_repr.h` defines the representor data model and public API used by the `ice` eswitch, bridge, datapath, and ethtool integration. It is the shared contract for VF/SF port representor creation, lookup, stats accounting, and queue state control.

## Important APIs And Types

`struct ice_repr_pcpu_stats` stores synchronized per-CPU CPU-hit counters: Rx packets/bytes, Tx packets/bytes, and Tx drops. `enum ice_repr_type` distinguishes VF and SF representors. `struct ice_repr` carries the represented source VSI, netdev, metadata destination, bridge port, stats pointer, representor id, parent MAC, type, VF/SF union, and a small ops table for add/remove/ready behavior.

The header declares creation (`ice_repr_create_vf`, `ice_repr_create_sf`), destruction (`ice_repr_destroy`), queue control (`ice_repr_start_tx_queues`, `ice_repr_stop_tx_queues`), netdev conversion and type check (`ice_netdev_to_repr`, `ice_is_port_repr_netdev`), stats increments, and PF representor lookup (`ice_repr_get`).

## Control Flow Role

The ops table lets common eswitch code invoke family-specific representor lifecycle without checking whether the represented endpoint is a VF or SF at every call. `ice_repr_get` provides xarray-backed lookup by representor id, while `ice_netdev_to_repr` is the fast path for netdev callbacks.

## State And Persistence Behavior

The header declares runtime-only state. `struct ice_repr` owns pointers to objects whose lifetime is coordinated outside the header: VSI, netdev, metadata destination, bridge port, VF/SF, and per-CPU stats. No persistent storage is involved.

## Dependencies And Integration Points

It includes `<net/dst_metadata.h>` and depends on forward declarations/types from the broader `ice` driver through includers such as `ice.h`. The API is used by eswitch attach/detach, bridge forwarding/offload code, TxRx stats paths, TC setup, and ethtool representor operations.

## Risks And Edge Cases

The union requires `type` and ops to stay consistent with the active member. Callers must not use `vf` fields for SF representors or `sf` fields for VF representors. Stats updates require `stats` to be allocated and valid on all CPUs. The `dst` and `br_port` pointers imply integration with metadata and bridge offload lifetimes, so detach order matters.

## Test Signals

Compile-time users should agree on the structure layout and prototypes. Runtime signals include successful `ice_netdev_to_repr` in netdev callbacks, correct VF/SF-specific ops selected after creation, valid stats accounting, and representor lookup returning the expected object from `pf->eswitch.reprs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_repr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sbq_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sbq_cmd.h

## Purpose

`ice_sbq_cmd.h` defines the sideband queue command ABI used by software and firmware to read and write neighboring devices such as PHY and CGU blocks. In this work item it is directly consumed by `ice_ptp_hw.c` for PHY register access and by common code implementing `ice_sbq_rw_reg`.

## Important APIs And Types

`enum ice_sbq_opc` defines sideband queue admin opcodes for neighbor device request and event descriptors. `struct ice_sbq_cmd_desc` is the indirect, non-posted sideband command descriptor with flags, opcode, data length, return value, cookie fields, length union, reserved bytes, and address high/low fields. `struct ice_sbq_evt_desc` represents sideband events.

`enum ice_sbq_dev_id` names destination devices used by the driver: primary PHY, CGU, peer PHY, and peer CGU. `enum ice_sbq_msg_opcode` distinguishes register read and write messages. `ICE_SBQ_MSG_FLAGS` and `ICE_SBQ_MSG_SBE_FBE` define message flag defaults. `struct ice_sbq_msg_req` and `struct ice_sbq_msg_cmpl` describe request/completion payloads, while `struct ice_sbq_msg_input` is the internal normalized input consumed by `ice_sbq_rw_reg`.

## Control Flow Role

The header has no executable code. Runtime flow is: a caller fills `struct ice_sbq_msg_input` with destination device, opcode, split address, and data; `ice_sbq_rw_reg` builds a sideband descriptor and request; firmware completes the request and read data is returned through the same input structure. PTP code uses this repeatedly for E82x, E810, and ETH56G register access.

## State And Persistence Behavior

No persistent state is stored here. The structs define transient command and event buffers exchanged with firmware. Multi-byte fields are explicitly little-endian where they cross the firmware ABI, so callers and descriptor builders must preserve endian conversion rules.

## Dependencies And Integration Points

The header is included by `ice_type.h`, `ice_common.c`, and PTP hardware code through common driver headers. It is tightly coupled to `ice_sbq_rw_reg` in `ice_common.c`, firmware/admin queue conventions, and device IDs used by PTP and CGU access.

## Risks And Edge Cases

This is an ABI header, so field sizes, ordering, and endianness are critical. Incorrect destination device selection can send a valid transaction to the wrong PHY or CGU, especially on dual-complex E825C where peer device IDs matter. Read/write opcode confusion can corrupt hardware registers. Callers must split 32-bit addresses into low/high fields consistently.

## Test Signals

Test signals include successful sideband reads/writes to known PHY/CGU registers, correct error propagation from firmware command return values, validation that peer PHY/CGU IDs work on multi-PHY devices, and static build checks that descriptor sizes and field types match firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sbq_cmd.h -->
