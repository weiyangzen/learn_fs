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
