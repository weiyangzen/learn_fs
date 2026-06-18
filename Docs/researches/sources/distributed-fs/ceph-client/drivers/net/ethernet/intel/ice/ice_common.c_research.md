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
