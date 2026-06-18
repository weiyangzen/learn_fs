# Research Group: subset-b-004347

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_utils_fw2x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_utils_fw2x.c

## Purpose
This file implements the Atlantic firmware 2.x operations table (`aq_fw_2x_ops`) used by the Aquantia/Marvell Atlantic NIC hardware abstraction layer. It is a firmware mailbox adapter: it discovers firmware mailbox/RPC/settings addresses, translates driver link and power policy into MPI control bits, polls firmware state bits for completion, and exposes MACsec, SMBus module EEPROM, PTP, EEE, flow-control, WoL, statistics, and temperature hooks through `struct aq_fw_ops`.

## Important APIs, types, and functions
The exported integration point is `const struct aq_fw_ops aq_fw_2x_ops`. Key methods include `aq_fw2x_init`, `aq_fw2x_deinit`, `aq_fw2x_set_link_speed`, `aq_fw2x_set_state`, `aq_fw2x_update_link_status`, `aq_fw2x_update_stats`, `aq_fw2x_get_phy_temp`, `aq_fw2x_set_power`, `aq_fw2x_set_eee_rate`, `aq_fw2x_get_eee_rate`, `aq_fw2x_set_flow_control`, `aq_fw2x_get_flow_control`, `aq_fw2x_send_fw_request`, `aq_fw2x_set_phyloopback`, `aq_fw2x_set_downshift`, `aq_fw2x_set_media_detect`, `aq_fw2x_send_macsec_req`, and `aq_fw2x_read_module_eeprom`. `fw2x_msg_wol` and `fw2x_msg_wol_pattern` describe an older WoL RPC payload; the actual magic-packet path uses `hw_atl_utils_fw_rpc`.

## Control flow
Initialization polls `HW_ATL_FW2X_MPI_MBOX_ADDR` and `HW_ATL_FW2X_MPI_RPC_ADDR`, then reads the settings address from the mailbox. Link setup writes a firmware rate mask to `MPI_CONTROL`, then `MPI_INIT` updates `MPI_CONTROL2` with EEE and pause bits. Several commands follow a common pattern: write firmware-facing memory, toggle a capability/control bit, and poll `MPI_STATE` or `MPI_STATE2` until firmware mirrors the transition. Stats and temperature are requested by toggling `CAPS_HI_STATISTICS` or `CTRL_TEMPERATURE`; MACsec and SMBus requests toggle low capability bits in `MPI_CONTROL`.

## State and persistence
State is persisted in hardware registers and firmware-owned mailbox/RPC/settings memory, not in kernel files. The driver caches discovered mailbox addresses in `aq_hw_s` (`mbox_addr`, `rpc_addr`, `settings_addr`) and updates `aq_link_status` plus current stats. WoL programming writes firmware sleep proxy information so behavior persists while the host enters low-power states.

## Dependencies and integration points
The file depends on Atlantic common helpers (`aq_hw_read_reg`, `aq_hw_write_reg`, firmware dword download/write helpers), NIC configuration (`aq_nic_cfg_s`), and Linux polling macros. MACsec support flows into the `macsec` API via the firmware `send_macsec_req` operation, while module EEPROM reads are exposed to ethtool/SFP paths through `read_module_eeprom`. PTP enable/adjust uses firmware 3.x extension registers even though it is attached to the 2.x ops table.

## Risks
Most operations rely on magic register offsets and bit toggles; mismatched firmware versions can produce silent `-EIO`, `-ETIME`, or `-EOPNOTSUPP` paths. `aq_fw2x_get_mac_permanent` returns a zero MAC if the efuse pointer is absent, leaving callers to validate. SMBus trailing-byte reads cast response memory to dwords and require careful length handling. `aq_fw2x_set_wol` ignores the link-drop polling return for `WAKE_PHY`, so firmware failure there can be partially hidden.

## Test signals
Useful signals are successful firmware init polling, link speed changes reflected in `aq_link_status.mbps`, ethtool EEE and pause configuration round-trips, MACsec request success only when `CAPS_LO_MACSEC` is set, SFP EEPROM reads through SMBus-capable firmware, WoL wake tests, and timeout/error logs from `readx_poll_timeout_atomic`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_utils_fw2x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2.c

## Purpose
This file implements the ATL2/A2 hardware operations for newer Atlantic devices such as AQC113, AQC115C, and AQC116C. It publishes device capability records and `hw_atl2_ops`, combining the existing Atlantic B0 ring datapath with A2-specific QoS, traffic-class mapping, RSS redirection, action-resolver receive filtering, interrupt moderation, VLAN filtering, firmware setup, and reset behavior.

## Important APIs, types, and functions
The public symbols are `hw_atl2_caps_aqc113`, `hw_atl2_caps_aqc115c`, `hw_atl2_caps_aqc116c`, and `const struct aq_hw_ops hw_atl2_ops`. Important internal functions include `hw_atl2_hw_reset`, `hw_atl2_hw_init`, `hw_atl2_hw_qos_set`, `hw_atl2_hw_queue_to_tc_map_set`, `hw_atl2_hw_rss_set`, `hw_atl2_hw_init_tx_tc_rate_limit`, `hw_atl2_hw_init_tx_path`, `hw_atl2_hw_init_rx_path`, `hw_atl2_hw_init_new_rx_filters`, `hw_atl2_act_rslvr_table_set`, `hw_atl2_hw_multicast_list_set`, `hw_atl2_hw_packet_filter_set`, `hw_atl2_hw_vlan_set`, `hw_atl2_hw_vlan_ctrl`, and `hw_atl2_hw_interrupt_moderation_set`.

## Control flow
Hardware prepare is delegated through `hw_atl2_utils_initfw`. Reset performs an A2 firmware soft reset, clears `struct hw_atl2_priv`, asks firmware for `MPI_RESET`, and checks hardware error flags. Initialization reads firmware action resolver table capabilities, computes a driver-owned ART base index, configures launch-time timing, initializes TX/RX paths, programs the MAC address, requests link up through firmware, applies QoS/RSS/hash settings, enables the new RPF block, snapshots counters, configures interrupts, and applies offloads. Runtime filtering updates go through ART records guarded by a firmware semaphore.

## State and persistence
Persistent driver state is minimal: `hw_atl2_priv` stores the last firmware statistics snapshot and the ART base index reserved by firmware. Hardware state resides in RX/TX scheduler registers, RPF filter tables, RSS tables, VLAN filter registers, interrupt moderation registers, and firmware-owned link settings. `aq_nic_cfg_s` drives traffic classes, priority mapping, flow control, RSS, VLAN filters, interrupt moderation, and rate limits.

## Dependencies and integration points
The implementation reuses many B0 helpers from `hw_atl_b0` and lower-level register helpers from `hw_atl_llh`, while A2-specific helpers come from `hw_atl2_llh.h` and `hw_atl2_utils.h`. The ops table is consumed by the Atlantic core driver through `aq_hw_ops`. Firmware provides ART capacity and link control through `aq_fw_ops`; the network stack reaches this file through netdev operations implemented in the shared Atlantic core.

## Risks
Traffic-class mapping assumes only 4-TC or 8-TC modes; invalid `tc_mode` returns `-EINVAL`. ART writes depend on semaphore acquisition and firmware-provided base indexes, so wrong capabilities can corrupt firmware-owned resolver entries. Rate-limit arithmetic uses link speed and configured min/max rates; zero or inconsistent rates may produce unexpected weights. Multicast programming uses unicast filter slots as multicast filters and rejects over-capacity lists with `-EBADRQC`.

## Test signals
Useful tests include probe on each advertised device capability, firmware reset/init success, RSS indirection across 4 and 8 traffic classes, VLAN filter routing to queues, promiscuous/all-multicast transitions, interrupt moderation in off/on/auto modes across link speeds, traffic-class max/min rate behavior, and counter updates through `hw_get_hw_stats`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2.h

## Purpose
This small public header declares the ATL2 hardware capability records and operations table. It is the include point used by PCI/device-selection code to bind supported A2 family devices to the ATL2 implementation.

## Important APIs, types, and functions
It includes `aq_common.h` and declares four external symbols: `hw_atl2_caps_aqc113`, `hw_atl2_caps_aqc115c`, `hw_atl2_caps_aqc116c`, and `hw_atl2_ops`. The capability symbols identify per-board limits and link masks, while `hw_atl2_ops` is the function-pointer table used by the Atlantic core hardware abstraction.

## Control flow
This file has no executable control flow. Its declarations let another translation unit select the correct `aq_hw_caps_s` and `aq_hw_ops` during device match/probe. The actual initialization, reset, rings, interrupts, filters, and firmware interactions live in `hw_atl2.c` and the ATL2 utility files.

## State and persistence
The header owns no state. It exposes immutable capability/ops objects defined elsewhere.

## Dependencies and integration points
The dependency on `aq_common.h` supplies declarations for `struct aq_hw_caps_s` and `struct aq_hw_ops`. Integration is outward-facing: PCI ID tables and core Atlantic setup code can include this header without including internal register maps.

## Risks
The main risk is declaration drift. If `hw_atl2.c` changes symbol names or capability coverage without updating this header, device binding will fail at build or link time. Because the header hides all internals, callers cannot validate feature assumptions from here alone.

## Test signals
Build coverage is the primary signal. A successful driver build with ATL2 enabled verifies that all externs resolve, and probe logs on AQC113/AQC115C/AQC116C confirm that the declared caps and ops are reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_internal.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_internal.h

## Purpose
This internal ATL2 header defines hardware limits, ring sizes, traffic-class/RSS constants, interrupt masks, action resolver tags, action encodings, RSS hash type masks, and the private ATL2 state structure used by `hw_atl2.c`.

## Important APIs, types, and functions
Key constants include MTU values, TX/RX ring counts, descriptor sizes, buffer sizes, maximum/minimum descriptors, maximum MAC filters, maximum TCs/RSS queues, interrupt moderation bounds, and ART semaphore ID `HW_ATL2_FW_SM_ACT_RSLVR`. The RPF tag offset/mask macros encode UC, all-multicast, VLAN, untagged, L3/L4, flexible, and PCP match fields. `HW_ATL2_ACTION*` macros encode drop, disable, assign-queue, and assign-TC actions. `enum HW_ATL2_RPF_ART_INDEX` defines driver-owned ART offsets, and `struct hw_atl2_priv` stores the last firmware stats snapshot and ART base index.

## Control flow
There is no executable code, but these constants shape the control flow in `hw_atl2.c`. For example, VLAN and promiscuous control writes ART entries at offsets from `art_base_index`, QoS maps PCP values to TCs using `HW_ATL2_ACTION_ASSIGN_TC`, and multicast/VLAN filters construct tags with the defined RPF masks.

## State and persistence
`struct hw_atl2_priv` is the only state definition. It persists in `aq_hw_s->priv` for the device lifetime and is reset by `hw_atl2_hw_reset`. The rest of the header describes hardware state layouts programmed into registers and resolver tables.

## Dependencies and integration points
The header includes `hw_atl2_utils.h` for `struct statistics_s`, tying private state to the firmware stats ABI. It also depends on shared Atlantic configuration constants such as `AQ_CFG_SKB_FRAGS_MAX`, `AQ_HW_RXD_MULTIPLE`, and `HW_ATL_VLAN_MAX_FILTERS` through included headers.

## Risks
Incorrect tag offsets, ART indexes, or action encodings can misroute or drop packets. The private ART index plan assumes firmware reserves entries before the driver base; if firmware capabilities differ, driver entries could overlap reserved resolver records. Ring and descriptor constants must match hardware and B0 helper assumptions.

## Test signals
Exercise promiscuous, VLAN, PCP-to-TC, queue assignment, and RSS flows. Resolver table readback on supported hardware, if available, can confirm that action encodings and masks produce expected filter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh.c

## Purpose
This file is the ATL2 low-level hardware helper implementation. It wraps specific A2 register and bitfield writes/reads behind typed helper functions used by `hw_atl2.c`, `hw_atl2_utils.c`, and `hw_atl2_utils_fw.c`.

## Important APIs, types, and functions
The helpers cover RPF/RSS controls (`hw_atl2_rpf_redirection_table2_select_set`, `hw_atl2_rpf_rss_hash_type_set`, `hw_atl2_rpf_new_enable_set`, `hw_atl2_new_rpf_rss_redir_set`), L2/VLAN tag programming (`hw_atl2_rpfl2_uc_flr_tag_set`, `hw_atl2_rpfl2_bc_flr_tag_set`, `hw_atl2_rpf_vlan_flr_tag_set`), TX scheduler and interrupt moderation (`hw_atl2_tpb_tx_tc_q_rand_map_en_set`, `hw_atl2_tpb_tx_buf_clk_gate_en_set`, `hw_atl2_reg_tx_intr_moder_ctrl_set`, `hw_atl2_tps_tx_pkt_shed_*`), launch-time setup, action resolver records, and firmware shared-buffer/boot/interrupt registers.

## Control flow
Most functions perform a single `aq_hw_write_reg_bit`, `aq_hw_write_reg`, or `aq_hw_read_reg_bit`. `hw_atl2_init_launchtime` reads the hardware version and selects a clock ratio based on version thresholds. Shared-buffer helpers loop across dword offsets to transfer structures between host and firmware input/output buffers. Action resolver record setup writes tag, mask, and action words to adjacent resolver-memory registers.

## State and persistence
All state is hardware or firmware shared state. Writes persist in device registers, resolver table memory, shared input buffers, boot registers, or interrupt clear registers until hardware, firmware, or reset changes them.

## Dependencies and integration points
The file depends on `hw_atl2_llh_internal.h` register addresses and masks plus `aq_hw_utils.h` register accessors. Higher-level ATL2 code relies on this file to avoid embedding raw offsets in policy logic.

## Risks
These helpers do little validation. Bad queue, TC, index, filter, offset, or length values can address unintended registers or shared-buffer dwords. Shared-buffer `int` offsets and lengths assume caller already computed dword counts correctly. Launch-time version thresholds are hard-coded and must track hardware revisions.

## Test signals
Register write/read tracing, hardware filter behavior, successful firmware shared-buffer transactions, boot register transitions, and interrupt moderation behavior provide coverage. Static review should verify every helper uses the matching address, mask, and shift from the internal register header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh.h

## Purpose
This public low-level ATL2 header declares the A2 register helper functions implemented in `hw_atl2_llh.c`. It separates higher-level ATL2 policy code from raw register addresses and bitfield macros.

## Important APIs, types, and functions
The declarations cover TX interrupt moderation, RSS redirection selection and hash type, new RPF enable, L2 unicast/broadcast filter tags, RSS redirection rows, VLAN filter tags, TX queue-to-TC random mapping, TX buffer clock gating, TX scheduler data arbiter/credit/weight programming, hardware version and launch-time initialization, action resolver record/section programming, firmware shared input/output buffer access, host-finished/MCP-finished handshake bits, MCP boot register access, and host request interrupt get/clear.

## Control flow
The header has no executable control flow. It defines the callable surface that `hw_atl2.c` uses for datapath/filter setup and that `hw_atl2_utils*.c` use for firmware boot/shared-buffer protocol.

## State and persistence
No local state is defined. The declared functions operate on `struct aq_hw_s` and mutate or read device registers and firmware shared buffers.

## Dependencies and integration points
Only `linux/types.h` and a forward declaration of `struct aq_hw_s` are needed, keeping the API lightweight. This file is included by ATL2 implementation files that need hardware access without pulling in the complete internal register map directly.

## Risks
The header exposes low-level functions without parameter range documentation beyond names. Callers must know valid queue, TC, filter, resolver, and shared-buffer ranges from `hw_atl2_internal.h`, `hw_atl2_llh_internal.h`, and firmware ABI structures.

## Test signals
Compile-time coverage ensures declarations match definitions. Runtime coverage comes indirectly through ATL2 init, firmware boot, RSS, VLAN, ART, and interrupt moderation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh_internal.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh_internal.h

## Purpose
This internal register-map header defines ATL2/A2 register addresses, masks, shifts, widths, defaults, and address-calculation macros used by the low-level hardware helpers.

## Important APIs, types, and functions
Important macro groups include RPF redirection and RSS hash controls, new RPF enable, L2 unicast/broadcast request tags, RSS redirection table addressing, VLAN request tags, RX/TX queue-to-TC map addressing, TX buffer and scheduler controls, TX interrupt moderation register addresses, launch-time control, FPGA version encoding, action resolver request tag/mask/action addresses, resolver section enable, firmware shared input/output buffer addresses, host/MCP shared-buffer handshake registers, MCP boot register, and host request interrupt set/clear addresses.

## Control flow
No functions execute here, but address macros are used to generate the control flow in `hw_atl2_llh.c`. Queue and TC address macros choose register blocks and bit shifts based on indices, so loop bounds in higher-level code must match their supported ranges.

## State and persistence
The header defines hardware state layout only. Values written through these definitions persist in NIC registers, resolver SRAM, firmware shared buffers, or interrupt status registers.

## Dependencies and integration points
This file is included by `hw_atl2_llh.c` and indirectly underpins ATL2 filtering, QoS, firmware, and boot flows. It intentionally remains internal so policy code uses named helper functions rather than raw offsets.

## Risks
Register-map headers are high blast-radius: a wrong address, mask, or shift can break traffic steering, firmware communication, or boot handling. Several address macros return zero for out-of-range queues; callers that pass invalid indices may write address zero. Naming/comments show generated-register style and should be kept in sync with hardware documentation.

## Test signals
Hardware bring-up, RSS distribution, VLAN filter hits, ART behavior, firmware boot/handshake, and interrupt moderation are practical runtime signals. Static tests can compare macro names and masks against vendor register specifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_llh_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils.c

## Purpose
This file handles ATL2 firmware selection and A2 firmware reboot/soft-reset sequencing. It chooses the A2 firmware ops table, records the firmware version, marks chip features, and performs low-level MCP boot restart polling.

## Important APIs, types, and functions
The exported functions are `hw_atl2_utils_initfw` and `hw_atl2_utils_soft_reset`. Internal helper `hw_atl2_mcp_boot_complete` checks the MCP boot register and host request interrupt. Boot state bits include `AQ_A2_BOOT_STARTED`, `AQ_A2_CRASH_INIT`, `AQ_A2_BOOT_CODE_FAILED`, `AQ_A2_FW_INIT_FAILED`, and `AQ_A2_FW_INIT_COMP_SUCCESS`; request bits include reboot, host boot, MAC fast boot, and PHY fast boot.

## Control flow
`hw_atl2_utils_initfw` reads the firmware version through the shared-buffer firmware ops, accepts version 1.x as expected, logs but continues for other versions, assigns `aq_a2_fw_ops`, calls firmware init, and sets `ATL_HW_CHIP_ANTIGUA`. `hw_atl2_utils_soft_reset` clears host request interrupt, writes a reboot request to the MCP boot register, polls for boot start, polls for boot complete or host-boot request, checks failure bits, rejects dynamic firmware load requests, and reinitializes firmware ops if available.

## State and persistence
The code updates `self->fw_ver_actual`, `self->aq_fw_ops`, and `self->chip_features`. It also writes MCP boot and interrupt-clear registers. No filesystem persistence exists.

## Dependencies and integration points
It depends on `hw_atl2_llh` boot/interrupt helpers, `hw_atl2_utils_fw.c` for `aq_a2_fw_ops` and version reading, Linux `iopoll`, and common Atlantic utility logging/version matching. `hw_atl2.c` calls this through `hw_prepare` and reset paths.

## Risks
Unsupported firmware versions are logged but still use `aq_a2_fw_ops`; this favors compatibility but can hide ABI drift. Dynamic host firmware load is explicitly not implemented and returns `-EIO`. Poll timeouts are long enough for boot but can delay probe/reset failure paths. `AQ_CFG_FAST_START` changes reboot request behavior at compile time.

## Test signals
Probe/reset logs should show detected firmware, boot start, boot complete, and no failure bits. Fault injection or hardware logs can validate timeout and failed boot paths. Builds with and without `AQ_CFG_FAST_START` should be checked if that option is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils.h

## Purpose
This header defines the A2 firmware shared-buffer ABI used by the ATL2 driver. It describes host-to-firmware input structures, firmware-to-host output structures, link and capability bitfields, stats formats, health monitors, sleep proxy data, cable diagnostics, filter capabilities, and firmware ops declarations.

## Important APIs, types, and functions
Major input-side types include `link_options_s`, `link_control_s`, `thermal_shutdown_s`, `mac_address_aligned_s`, `sleep_proxy_s`, `pause_quanta_s`, `request_policy_s`, and `fw_interface_in`. Output-side types include `transaction_counter_s`, `version_s`, `link_status_s`, `wol_status_s`, health monitors, `device_link_caps_s`, `sleep_proxy_caps_s`, `lkp_link_caps_s`, `statistics_s` with A0/B0 variants, `filter_caps_s`, `management_status_s`, and `fw_interface_out`. It also declares `hw_atl2_utils_initfw`, `hw_atl2_utils_soft_reset`, `hw_atl2_utils_get_fw_version`, `hw_atl2_utils_get_action_resolve_table_caps`, and `aq_a2_fw_ops`.

## Control flow
The header has no executable flow, but its layout drives the shared-buffer macros in `hw_atl2_utils_fw.c`. Offsets in `fw_interface_in` and `fw_interface_out` are used as dword indexes into firmware shared memory, and the transaction counter fields provide consistent multiword reads.

## State and persistence
These structures represent firmware-persistent and hardware-shared state: link policy, MTU, MAC address, sleep proxy/WoL, pause quanta, cable diagnostics, firmware version, link status, health, caps, management status, stats, and trace/core-dump data. The driver reads/writes them through MMIO windows rather than storing them on disk.

## Dependencies and integration points
The header includes `aq_hw.h` and is used by ATL2 firmware utilities and internal hardware code. It is the ABI contract between driver and A2 firmware; layout, packing, alignment, and bitfield order must match firmware expectations.

## Risks
C bitfield layout is compiler- and endian-sensitive, so this ABI assumes the kernel/compiler layout used by the target driver. The shared-buffer macros enforce dword alignment for many fields, but not semantic validity. Any firmware ABI revision that changes field order or size can break link, stats, WoL, or filter capability handling.

## Test signals
Version reads, link speed/EEE/pause round-trips, stable multiword stats reads, ART capability retrieval, WoL programming, and health temperature reads validate the ABI. Build-time `BUILD_BUG_ON_MSG` checks in the C file catch unaligned shared-buffer accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils_fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils_fw.c

## Purpose
This file implements the A2 firmware operations table `aq_a2_fw_ops`. It translates Atlantic driver firmware hooks into reads and writes of the A2 shared-buffer ABI, including link control, EEE, pause, link status, stats, MAC address, WoL sleep proxy, temperature, loopback, downshift, firmware version, and ART capability queries.

## Important APIs, types, and functions
The exported symbols are `hw_atl2_utils_get_fw_version`, `hw_atl2_utils_get_action_resolve_table_caps`, and `const struct aq_fw_ops aq_a2_fw_ops`. Important internal helpers are the shared-buffer access macros, `hw_atl2_shared_buffer_read_block`, `hw_atl2_shared_buffer_finish_ack`, `aq_a2_fw_init`, `aq_a2_fw_deinit`, `aq_a2_fw_set_link_speed`, `aq_a2_fw_set_state`, `aq_a2_fw_update_link_status`, `aq_a2_fw_update_stats`, `aq_a2_fill_a0_stats`, `aq_a2_fill_b0_stats`, `aq_a2_fw_set_wol_params`, `aq_a2_fw_set_eee_rate`, `aq_a2_fw_get_eee_rate`, `aq_a2_fw_renegotiate`, `aq_a2_fw_set_flow_control`, `aq_a2_fw_get_flow_control`, `aq_a2_fw_set_phyloopback`, and `aq_a2_fw_set_downshift`.

## Control flow
Single-dword reads use `hw_atl2_shared_buffer_read`; multiword reads use transaction counters and retry until both counters match before and after the read. Writes update `fw_interface_in` fields, then set the host-finished bit and poll for MCP acknowledgement. Init sets host mode active and jumbo MTU; deinit switches to shutdown. Link setup writes `link_options`, while `MPI_INIT` also sets EEE and pause bits. Stats read firmware version to choose A0 or B0 stats layout, compute deltas against `priv->last_stats`, then combine firmware stats with DMA hardware counters.

## State and persistence
The file updates firmware shared input state and driver state in `aq_link_status`, `curr_stats`, and `hw_atl2_priv.last_stats`. WoL programming changes MAC address, sleep proxy wake flags, and host mode. Firmware output state is treated as authoritative for link partner caps, flow control, device caps, and temperature.

## Dependencies and integration points
It depends on `hw_atl2_utils.h` ABI structs, `hw_atl2_llh` shared-buffer helpers, B0 stats register helpers, `aq_nic_cfg_s`, and the generic `aq_fw_ops` interface consumed by ATL2 hardware ops.

## Risks
Multiword reads can return `-ETIME` if firmware transaction counters keep changing or never stabilize. Stats deltas are ignored when a negative/corrupt delta is detected, and stats only accumulate while link is up. `hw_atl2_utils_get_fw_version` ignores the return from `read_safe`. The sleep proxy write uses a nested `wake_on_lan_s` object with the `sleep_proxy` field macro, so layout assumptions are especially important.

## Test signals
Exercise link up/down, advertised speeds including 10M through 10G, EEE set/get, pause set/get, renegotiation bit clearing, loopback modes, downshift programming, WoL wake on magic/link, stable stats under traffic, temperature reads, firmware version reporting, and ART capability retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/MSS_Egress_registers.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/MSS_Egress_registers.h

## Purpose
This header defines MACsec egress register addresses and C bitfield views for top-level egress control and LUT access registers.

## Important APIs, types, and functions
Address macros include `MSS_EGRESS_CTL_REGISTER_ADDR`, egress SA expired and threshold status registers, egress LUT address/control registers, and egress LUT data control base. Structs include `mss_egress_ctl_register`, `mss_egress_lut_addr_ctl_register`, and `mss_egress_lut_ctl_register`.

## Control flow
There is no executable flow. `macsec_api.c` uses the LUT address/control structs to select egress MAC control filter, classifier, SC/SA/key, and MIB tables, then triggers read or write operations. Counter-clear and expiry code uses the egress control/status addresses.

## State and persistence
The described state lives in MACsec hardware registers. `mss_egress_ctl_register` includes soft reset, drop policy, GCM start/test, classification, counter clear, global time clear, and explicit SecTAG ethertype fields.

## Dependencies and integration points
The file is included only by the MACsec API implementation. It complements `MSS_Ingress_registers.h` and the record definitions in `macsec_struct.h`.

## Risks
C bitfield layout must match the 16-bit MDIO register layout. Several fields are documented as reserved or required zero; callers must preserve them when modifying control registers. Wrong LUT select/address encodings can write security policy into the wrong MACsec table.

## Test signals
MACsec egress table reads/writes, egress counter clearing, SA expired/threshold status get/set, and packet classification/encryption behavior validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/MSS_Egress_registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/MSS_Ingress_registers.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/MSS_Ingress_registers.h

## Purpose
This header defines MACsec ingress register addresses and bitfield views for ingress control and LUT access.

## Important APIs, types, and functions
Address macros cover `MSS_INGRESS_CTL_REGISTER_ADDR`, ingress LUT address/control registers, and ingress LUT data control base. Structs include `mss_ingress_ctl_register`, `mss_ingress_lut_addr_ctl_register`, and `mss_ingress_lut_ctl_register`.

## Control flow
The header has no executable code. `macsec_api.c` uses it to select ingress pre-control, pre-classification, SA key, SC/SA, post-classification, post-control, and MIB tables, then triggers LUT read/write operations. Counter clearing toggles `clear_count` in the ingress control register.

## State and persistence
The described state persists in MACsec ingress hardware registers. Control fields include soft reset, point-to-point mode, SCI creation, drop policy, ICV checking, SecTAG removal, global validation mode, counter/global-time clear bits, and ICV length mode.

## Dependencies and integration points
This file is paired with egress register definitions and consumed by the MACsec API layer. It relies on the caller to perform MDIO access under the shared MDIO semaphore.

## Risks
Reserved fields and bitfield ordering must be preserved. Incorrect `lut_select` values can target the wrong ingress table. The control register has security-sensitive validation/drop/remove-SecTAG behavior, so any future writer must avoid accidental read-modify-write loss.

## Test signals
Ingress table programming, validation/drop behavior, SecTAG removal behavior, ingress counter reads/clears, and MDIO traces confirm correct use of these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/MSS_Ingress_registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_api.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_api.c

## Purpose
This file implements the Atlantic MACsec Security Subsystem API. It exposes typed get/set functions for ingress and egress MACsec LUT records, SA/SC/key records, counters, counter clearing, and egress SA expiry status while hiding the 16-bit MDIO/LUT packing format.

## Important APIs, types, and functions
Public functions are the `aq_mss_get_*` and `aq_mss_set_*` APIs declared in `macsec_api.h`: ingress pre/post control filters, ingress pre/post classifiers, ingress SC/SA/SA key, egress control filter/classifier/SC/SA/SA key, egress and ingress counters, clear operations, and egress SA expired/threshold status accessors. Internal core helpers are `AQ_API_CALL_SAFE`, `aq_mss_mdio_sem_get/put`, `aq_mss_mdio_read/write`, `set_raw_ingress_record`, `get_raw_ingress_record`, `set_raw_egress_record`, and `get_raw_egress_record`.

## Control flow
Every public API zeroes output records where applicable, then runs the private worker under the MDIO semaphore using `AQ_API_CALL_SAFE`. Raw setters write packed record words as adjacent MDIO register pairs, clear unused data-buffer words, select LUT table and row, then issue a write command. Raw getters select table and row, issue a read command, and read adjacent word pairs. Many odd-row ingress/egress reads first read the previous even row as a hardware workaround. Each typed setter/getter manually packs or unpacks fields across 16-bit words.

## State and persistence
State persists in MACsec hardware LUTs and MIB/status registers. Key setters temporarily hold SAK material in stack arrays and scrub packed key buffers with `memzero_explicit` after writes. Counter-clear functions toggle clear bits 0->1->0 in ingress or egress control registers.

## Dependencies and integration points
The API uses `aq_mdio_read_word` and `aq_mdio_write_word`, Linux MDIO MMD constants, Atlantic MDIO semaphore helpers, register definitions from `MSS_Ingress_registers.h` and `MSS_Egress_registers.h`, and record definitions from `macsec_struct.h`. Higher-level Atlantic MACsec netdev code can use these routines to program 802.1AE policy.

## Risks
The manual bit packing is dense and security-sensitive; a shift or mask error changes classification, key, PN, replay, or validation behavior. MDIO read returns `0xffff` are treated as timeout, which can conflict with legitimate all-ones data if used in unsupported contexts. Odd-row read workarounds do not work for all hardware according to comments. Some setters warn on error, others just return it, so observability is inconsistent.

## Test signals
Unit-style pack/unpack round-trips for every record type would be valuable. Hardware tests should program ingress and egress SAs/SCs, keys, classifiers, replay windows, and validation modes; send protected/validated/dropped traffic; check MIB counters; clear counters; and verify SA expired/threshold status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_api.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_api.h

## Purpose
This header declares the Atlantic MACsec API and table sizing constants. It is the public contract for programming MACsec ingress/egress tables and reading counters/status from other driver components.

## Important APIs, types, and functions
Constants define row counts and row offsets for ingress pre-control, pre-class, post-class, SC, SA, SA key, post-control, egress control, egress class, egress SC, egress SA, and egress SA key tables. Declarations cover typed get/set APIs for all record tables, egress SC/SA/common counters, ingress SA/common counters, counter clear functions, and egress SA expired/threshold get/set functions.

## Control flow
No code executes here. The header organizes MACsec hardware access around record structs from `macsec_struct.h`; callers fill a struct and table index, then call a setter, or call a getter to unpack raw hardware state into a struct.

## State and persistence
The header itself owns no state. The APIs it declares mutate or read persistent MACsec hardware table rows, MIB counters, and expiry status bits.

## Dependencies and integration points
It includes `aq_hw.h` for `struct aq_hw_s` and `macsec_struct.h` for the record/counter types. It is implemented by `macsec_api.c` and used by the Atlantic MACsec integration layer.

## Risks
Row count constants are part of bounds checking. If hardware variants expose different capacities, these constants must be revised or made capability-aware. API users must provide valid record fields; the setters mostly mask fields into hardware width rather than validating semantic combinations.

## Test signals
Compile coverage verifies declaration/definition agreement. Runtime tests should cover first, last, and out-of-range table indexes for each API, plus counter and expiry status calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_struct.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_struct.h

## Purpose
This header defines the typed MACsec record and counter structures used by the Atlantic MACsec API. It maps 802.1AE/MSS concepts such as control filters, classifiers, secure channels, secure associations, keys, replay/validation policy, and MIB counters into driver-facing C structs.

## Important APIs, types, and functions
Egress types include `aq_mss_egress_ctlf_record`, `aq_mss_egress_class_record`, `aq_mss_egress_sc_record`, `aq_mss_egress_sa_record`, `aq_mss_egress_sakey_record`, and egress SC/SA/common counter structs. Ingress types include pre-control and post-control filter records, pre-class and post-class records, `aq_mss_ingress_sc_record`, `aq_mss_ingress_sa_record`, `aq_mss_ingress_sakey_record`, and ingress SA/common counters. Fields cover MAC addresses, ethertypes, SCI, TCI, PN, VLAN, byte comparators, masks, action modes, validation/replay, AN rollover, key material, and 64-bit counters represented as two u32 words.

## Control flow
There is no executable flow. `macsec_api.c` uses these structures as the semantic input/output shape for its packing and unpacking routines. Higher-level code can reason in terms of MACsec records instead of 16-bit LUT words.

## State and persistence
Instances of these structures are transient in driver memory, but their contents represent persistent hardware MACsec LUT rows or counters once written. Key records contain sensitive SAK material and should be handled carefully by callers.

## Dependencies and integration points
The header assumes Linux integer typedefs are available through inclusion context. It is included by `macsec_api.h`, making these types public within the Atlantic driver.

## Risks
The structures are not packed hardware overlays; they are logical records. Adding, reordering, or resizing fields requires matching changes in `macsec_api.c` pack/unpack code. Many fields are security policy controls with limited valid ranges, but the type system uses `u32` broadly and does not enforce constraints.

## Test signals
Pack/unpack round-trip tests, MACsec traffic tests for protect/encrypt/validate/replay/drop modes, key programming tests, and counter checks are the best evidence that these logical structs match hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/Kconfig

## Purpose
This Kconfig file defines configuration entries for ARC EMAC-family Ethernet support, including a vendor menu gate, a shared core driver symbol, and Rockchip SoC glue support.

## Important APIs, types, and functions
`NET_VENDOR_ARC` is a bool vendor selector defaulting to yes. `ARC_EMAC_CORE` is a tristate internal/shared core depending on `ARC`, `ARCH_ROCKCHIP`, or `COMPILE_TEST`, and it selects `MII`, `PHYLIB`, and `CRC32`. `EMAC_ROCKCHIP` is the user-visible tristate for RK3036/RK3066/RK3188 EMAC support; it selects `ARC_EMAC_CORE` and depends on OF IRQ and regulator support plus Rockchip or compile-test builds.

## Control flow
Kconfig controls build visibility and dependency resolution. If `NET_VENDOR_ARC` is disabled, ARC Ethernet questions are skipped. Enabling Rockchip EMAC pulls in the core ARC EMAC object and required PHY/MII/CRC dependencies.

## State and persistence
The persistent output is the kernel `.config`, which determines whether the core and platform glue are built in, modular, or omitted.

## Dependencies and integration points
The symbols integrate with the drivers/net/ethernet Kconfig hierarchy and the local Makefile. `ARC_EMAC_CORE` builds `arc_emac.o`, while `EMAC_ROCKCHIP` builds `emac_rockchip.o`.

## Risks
Because `ARC_EMAC_CORE` is not user-described, platform glue must select it correctly. Missing dependency selections would surface as build failures in PHY, MII, CRC, OF, IRQ, or regulator paths. The vendor gate default y follows kernel vendor-menu convention but can hide prompts when disabled.

## Test signals
Run configuration coverage for built-in, module, and disabled cases; compile-test on non-ARC/non-Rockchip; and verify Rockchip selection pulls the core object and dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/Makefile

## Purpose
This Makefile builds the ARC EMAC core and Rockchip glue objects according to Kconfig selections.

## Important APIs, types, and functions
`arc_emac-objs := emac_main.o emac_mdio.o` combines the core netdev implementation and MDIO bus support into one composite object. `obj-$(CONFIG_ARC_EMAC_CORE) += arc_emac.o` builds that core. `obj-$(CONFIG_EMAC_ROCKCHIP) += emac_rockchip.o` builds the Rockchip platform wrapper.

## Control flow
Build control is entirely Kbuild-driven. Enabling `ARC_EMAC_CORE` compiles and links `emac_main.o` and `emac_mdio.o` into `arc_emac.o`; enabling `EMAC_ROCKCHIP` additionally compiles the SoC-specific wrapper.

## State and persistence
No runtime state exists. Build artifacts are generated by Kbuild according to `.config`.

## Dependencies and integration points
This Makefile is the build companion to `arc/Kconfig`. The core object exports `arc_emac_probe` and `arc_emac_remove` for glue drivers such as `emac_rockchip.c`.

## Risks
Object composition must stay in sync with exported symbols. If MDIO support moved or the core gained more source files, `arc_emac-objs` would need updates. The glue object depends on the selected core at link/load time.

## Test signals
Kernel builds with `CONFIG_ARC_EMAC_CORE=m/y` and `CONFIG_EMAC_ROCKCHIP=m/y` validate object composition. Module dependency inspection should show Rockchip glue depending on the ARC EMAC core when modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac.h

## Purpose
This header defines ARC EMAC register IDs, bit masks, descriptor layout, ring sizes, private driver state, MMIO helpers, and exported probe/remove/MDIO hooks shared by the ARC EMAC core and platform glue.

## Important APIs, types, and functions
Register masks cover interrupt status/enables, control bits, descriptor ownership/status, and MDIO completion. `enum` register IDs map logical names to MMIO offsets. `struct arc_emac_bd` is the hardware buffer descriptor with `info` and DMA data pointer. `struct buffer_state` tracks skb and DMA mapping metadata. `struct arc_emac_mdio_bus_data` stores reset GPIO timing. `struct arc_emac_priv` holds device, MDIO bus, MMIO base, clock, NAPI, RX/TX rings, DMA handles, skb states, ring indices, link state, speed/duplex, and missed-error tracking. Inline helpers `arc_reg_set/get/or/clr` wrap MMIO access.

## Control flow
The header has only inline register helpers. `emac_main.c` uses them throughout probe, open, stop, interrupt, TX/RX, filtering, and restart paths. Platform glue initializes fields such as `drv_name`, `set_mac_speed`, and `clk` before calling `arc_emac_probe`.

## State and persistence
`arc_emac_priv` is per-netdev runtime state. RX/TX descriptors and skb mapping arrays persist for the device lifetime, with buffers allocated on open and freed on stop. Hardware state persists in MMIO registers and DMA rings.

## Dependencies and integration points
It includes Linux device, DMA, netdevice, PHY, and clock headers. It declares `arc_mdio_probe/remove` from `emac_mdio.c` and `arc_emac_probe/remove` exported by `emac_main.c` for SoC glue.

## Risks
Descriptor and DMA address fields assume hardware can consume the stored address width; the capability is for older ARC EMAC hardware. Ring sizes are fixed at 128. Register helper offsets multiply enum IDs by `sizeof(int)`, so enum ordering is the hardware ABI.

## Test signals
Build coverage across core and glue, probe on revision 5/7 hardware, DMA ring operation, PHY MDIO operation, and interrupt/TX/RX traffic validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_main.c

## Purpose
This file implements the ARC EMAC 10/100 net_device core: probe/remove, open/stop, DMA ring setup, NAPI RX/TX completion, interrupt handling, PHY link adjustment, multicast/promiscuous filtering, statistics, transmit, MAC address programming, and a recovery restart path for RX stalls.

## Important APIs, types, and functions
The exported APIs are `arc_emac_probe` and `arc_emac_remove`. Netdev operations include `arc_emac_open`, `arc_emac_stop`, `arc_emac_tx`, `arc_emac_set_address`, `arc_emac_stats`, and `arc_emac_set_rx_mode`. Runtime helpers include `arc_emac_tx_avail`, `arc_emac_adjust_link`, `arc_emac_tx_clean`, `arc_emac_rx`, `arc_emac_rx_miss_handle`, `arc_emac_rx_stall_check`, `arc_emac_poll`, `arc_emac_intr`, `arc_free_tx_queue`, `arc_free_rx_queue`, and `arc_emac_restart`.

## Control flow
Probe reads DT PHY/register/IRQ resources, maps MMIO, enables clock or reads `clock-frequency`, validates hardware ID revision 5 or 7, sets poll rate, clears interrupt status, requests IRQ, sets MAC address, allocates coherent RX/TX descriptor rings, probes MDIO, connects PHY, adds NAPI, and registers the netdev. Open allocates/maps RX skbs, initializes descriptors and ring pointers, enables interrupts/control bits/NAPI/PHY/queue. Interrupts acknowledge status, schedule NAPI for RX/TX, and account error-counter rollovers. NAPI cleans TX, handles missed packets, receives up to budget, reenables interrupts, and checks RX stalls. TX maps one skb into one descriptor and forces EMAC polling with `TXPL_MASK`.

## State and persistence
Runtime state lives in `arc_emac_priv`, DMA descriptors, skb mapping arrays, PHY state, and `ndev->stats`. There is no filesystem persistence. Hardware state includes MAC address registers, logical address filter registers, ring base registers, enable/status/control registers, and error counters.

## Dependencies and integration points
The file depends on Linux netdevice, DMA, NAPI, PHYLIB, OF, IRQ, clock, CRC32 multicast hashing, and the local MDIO implementation. SoC glue allocates the net_device, fills private glue fields, and calls `arc_emac_probe`; `emac_rockchip.c` is one such user.

## Risks
RX open error paths can return after partially allocated/mapped RX buffers; cleanup depends on caller/device teardown. The hardware supports single-buffer packets only; fragmented/chained RX packets are counted as length errors. Stats reads add hardware counters into cumulative stats, so repeated `ndo_get_stats` calls may double-count if counters are not clear-on-read. RX stall recovery is heuristic and restarts EMAC when missed errors rise while the current RX descriptor is still owned by hardware.

## Test signals
Probe/remove with DT resources, PHY link changes, full/half duplex register changes, TX queue stop/wake at ring full, RX traffic under NAPI budget, multicast filter programming, error counter rollover interrupts, netpoll if enabled, RX stall recovery, stop/open cycles, and DMA mapping failure paths are relevant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_main.c -->
