# sources/distributed-fs/ceph-client/include/linux/bnge/hsi.h lines 5194-12027

## Scope

This chunk covers a large generated ABI section of the Broadcom NetXtreme-E/BNGE HWRM hardware-software interface header. It starts at `hwrm_port_mac_cfg_output` and runs through the first part of `hwrm_nvm_install_update_output`, ending in the middle of that response's result-code definitions. The visible range defines wire-format request, response, statistics, error-detail, and helper payload structs for port, queue, VNIC, ring, classification/filtering, statistics, firmware management, monitoring, WoL, debug/coredump, and NVM operations.

There is no executable C control flow in this chunk. The "APIs" are packed firmware command layouts and constants that driver code fills, submits to firmware, and decodes from firmware-owned responses.

## Purpose

The chunk is the contract between the Linux BNGE driver and adapter firmware for several core device-management areas:

- Port MAC/PHY/PTP/statistics: port MAC config response, PTP timestamp capability/register query, standard and extended port counters, loopback, ECN, PFC advanced stats, timestamp query, PHY capabilities, I2C/MDIO access, LED control, FEC/FDR statistics, and MAC loopback capabilities.
- Queue and DCB/QoS configuration: port queue capabilities, queue length/profile configuration, PFC enable/watchdog configuration, priority-to-CoS mapping, CoS bandwidth weights and TSA policy, DSCP-to-priority tables, and PFC watchdog timeout.
- VNIC, RSS, TPA, placement, and ring lifecycle: VNIC allocation/update/free/config/caps, TPA/GRO config/query, RSS table/hash/key config/query, placement modes, RSS/COS/LB context allocation, ring allocation/free/reset, interrupt aggregation tuning, and ring group allocation/free.
- CFA classification and tunnel filters: L2 filter allocation/free/config, RX mask programming for multicast/VLAN/promiscuous modes, tunnel filter allocation/free, n-tuple filter output/free/config, and programmable tunnel destination port allocation/free.
- Statistics contexts and telemetry: context hardware stats, extended TPA stats, engine stats, stat context allocation/free/query/clear, PCIe stats, generic stats, doorbell error stats, and RoCE stats.
- Firmware lifecycle and structured data: firmware reset/status/time, structured LLDP/DCBX/RSS/peer-mmap/MSI-X/debug-token payloads, set/get structured data commands, IPC messages, ECN config, firmware health, livepatch, sync, quiesce/unquiesce, backup/restore, secure config, forwarded responses, environmental telemetry, power histograms, and PAX latency histograms.
- Wake-on-LAN, debug, and NVM: WoL filter management and reason query, debug capability/config/coredump list/initiate/retrieve, raw NVM write/read/dump, directory entry operations, device version info, NVM item write/modify/erase, and update verification/install.

## Important API Shapes

Almost every HWRM command in this range follows the same base layout:

- Input structs begin with `req_type`, `cmpl_ring`, `seq_id`, `target_id`, and `resp_addr`.
- Output structs begin with `error_code`, `req_type`, `seq_id`, and `resp_len`, and end with `valid`.
- Optional input fields are selected by an `enables` bitmask; behavioral switches are selected by `flags`.
- DMA payloads use host physical/DMA addresses such as `tx_stat_host_addr`, `rx_stat_host_addr`, `ring_grp_tbl_addr`, `hash_key_tbl_addr`, `dest_data_addr`, `src_data_addr`, `stats_dma_addr`, `host_dest_addr`, `host_src_addr`, `pattern_buf_addr`, `pattern_mask_addr`, `backup_page_dir`, and `restore_page_dir`.
- Firmware-owned resources are represented by IDs returned from allocation commands and later consumed by query/config/free commands: `vnic_id`, `ring_id`, `logical_ring_id`, `ring_group_id`, `rss_cos_lb_ctx_id`, `l2_filter_id`, `tunnel_filter_id`, `ntuple_filter_id`, `stat_ctx_id`, `tunnel_dst_port_id`, `wol_filter_id`, and NVM `dir_idx`.

The file uses Linux fixed-width endian types. Most command fields are little-endian (`__le16`, `__le32`, `__le64`), but protocol fields that are naturally network ordered can be big-endian, for example DCBX `protocol_id` and tunnel destination ports.

## Major Types and Constants

Port-related layouts include:

- `struct tx_port_stats`, `struct rx_port_stats`, `struct tx_port_stats_ext`, `struct rx_port_stats_ext`, `struct port_lpbk_stats`, `struct port_stats_ecn`, and `struct port_stats_ext_pfc_adv`.
- `hwrm_port_qstats_*`, `hwrm_port_qstats_ext_*`, `hwrm_port_qstats_ext_pfc_wd_*`, `hwrm_port_lpbk_qstats_*`, `hwrm_port_ecn_qstats_*`, `hwrm_port_clr_stats_*`, and `hwrm_port_lpbk_clr_stats_*`.
- `hwrm_port_mac_ptp_qcfg_*` advertises direct/HWRM PTP access, one-step TX timestamping, RTC configuration, 64-bit PHC time, and register offsets for RX/TX timestamp FIFOs and reference clocks.
- `hwrm_port_ts_query_*` queries TX/RX PTP message timestamps with optional timeout, sequence-id, and header-offset fields.
- `hwrm_port_phy_qcaps_*` exposes EEE, loopback, shared PHY config, cumulative counter behavior, FCS handling, port counts, forced/auto/EEE/PAM4 speeds, 1G through 800G speed2 bitmaps, pause/PFC support, bank-address support, and PFC advanced-stat support.
- `hwrm_port_phy_i2c_*` and `hwrm_port_phy_mdio_*` provide firmware-mediated module/PHY register access.
- `hwrm_port_led_cfg_*`, `hwrm_port_led_qcfg_*`, and `hwrm_port_led_qcaps_*` model up to four LEDs with speed/activity type, default/off/on/blink/blink-alt states, amber/green/combined colors, blink timings, and group IDs.
- `hwrm_port_phy_fdrstat_*` starts/stops/clears/queries FDR/FEC statistics windows and returns accumulated/current codeword and symbol-error histograms.

Queue and QoS layouts include:

- `hwrm_queue_qportcfg_*`, `hwrm_queue_qcfg_*`, and `hwrm_queue_cfg_*` for queue discovery and configuration. Queue service profiles distinguish lossy, lossless, RoCE, CNP, NIC, and unknown profiles.
- `hwrm_queue_pfcenable_*` for per-priority PFC and PFC watchdog enables.
- `hwrm_queue_pri2cos_*` for 802.1p priority to CoS queue mapping, including TX/RX/bidirectional path and inner VLAN selection.
- `hwrm_queue_cos2bw_qcfg_output` and `hwrm_queue_cos2bw_cfg_input` for eight CoS queues. Each queue has min/max bandwidth fields using value, scale, and unit bitfields, plus TSA assignment (`SP` or `ETS`), priority level, and bandwidth weight.
- `hwrm_queue_dscp_qcaps_*`, `hwrm_queue_dscp2pri_qcfg_*`, and `hwrm_queue_dscp2pri_cfg_*` expose DSCP table size/capability and transfer DSCP-to-priority entries through DMA buffers.
- `hwrm_queue_pfcwd_timeout_*` configures/queries PFC watchdog timeout.

VNIC/RSS/ring layouts include:

- `hwrm_vnic_alloc_*`, `hwrm_vnic_update_*`, `hwrm_vnic_free_*`, `hwrm_vnic_cfg_*`, and `hwrm_vnic_qcaps_*`. Capabilities cover VLAN strip, BD stall, RoCE-only/dual/mirroring VNICs, RSS defaults, outermost RSS, checksum/CQE modes, VNIC state, virtio allocation, metadata formats, strict/delta RSS hash behavior, ring select modes, IPv6 flow label and IPsec SPI hash types, trusted-VF outermost RSS, port-CoS mapping, RSS profile TCAM, tunnel TPA, and RE flush.
- `hwrm_vnic_tpa_cfg_*` and `hwrm_vnic_tpa_qcfg_*` configure TPA/GRO, encapsulated TPA, RSC window updates, ECN aggregation, GRE-sequence policy, IPID/TTL checks, and tunnel protocol enable bitmaps.
- `hwrm_vnic_rss_cfg_*` and `hwrm_vnic_rss_qcfg_*` manage RSS hash types, hash mode flags, ring group table DMA, hash key DMA or returned key array, RSS context index, include/exclude semantics, IPsec support, and ring selection mode.
- `hwrm_vnic_plcmodes_cfg_*` controls regular, jumbo, HDS, RoCE, and virtio placement settings.
- `hwrm_ring_alloc_*`, `hwrm_ring_free_*`, `hwrm_ring_reset_*`, `hwrm_ring_aggint_qcaps_*`, `hwrm_ring_cmpl_ring_qaggint_params_*`, and `hwrm_ring_grp_*` define TX/RX/completion/RoCE/NQ ring creation, page-table binding, completion coalescing, interrupt mode, scheduling, stat context attachment, CQ handle, push-buffer selection, reset consumer index, interrupt aggregation limits, and completion/ring-group relationships.

CFA/filtering layouts include:

- `DEFAULT_FLOW_ID`, `ROCEV1_FLOW_ID`, `ROCEV2_FLOW_ID`, and `ROCEV2_CNP_FLOW_ID` special flow IDs.
- `hwrm_cfa_l2_filter_alloc_*`, `hwrm_cfa_l2_filter_free_*`, and `hwrm_cfa_l2_filter_cfg_*` for MAC/VLAN/tunnel/source/destination/mirror L2 filters. Output `flow_id` splits value, internal/external type, and RX/TX direction.
- `hwrm_cfa_l2_set_rx_mask_*` for multicast, all-multicast, broadcast, promiscuous, outermost, and VLAN mask programming with multicast and VLAN DMA tables.
- `hwrm_cfa_tunnel_filter_alloc_*` and `hwrm_cfa_tunnel_filter_free_*` for tunnel-aware filters over VXLAN, NVGRE, GRE, GENEVE, MPLS, STT, IPIP, VXLAN-GPE, and wildcard tunnel types.
- `hwrm_cfa_ntuple_filter_alloc_output`, `hwrm_cfa_ntuple_filter_free_*`, and `hwrm_cfa_ntuple_filter_cfg_*` for n-tuple filter IDs, destination retargeting, mirroring, metering, and detailed allocation error codes.
- `hwrm_tunnel_dst_port_alloc_*` and `hwrm_tunnel_dst_port_free_*` for programmable tunnel ports, including custom GRE, eCPRI, SRv6, VXLAN-GPE, dynamic UPAR slots, and allocation/free status details.

Statistics and telemetry layouts include:

- `ctx_hw_stats`, `ctx_hw_stats_ext`, and `ctx_eng_stats` for host statistics buffers.
- `hwrm_stat_ctx_alloc_*`, `hwrm_stat_ctx_free_*`, `hwrm_stat_ctx_query_*`, `hwrm_stat_ext_ctx_query_*`, `hwrm_stat_ctx_eng_query_*`, and `hwrm_stat_ctx_clr_stats_*`.
- `hwrm_pcie_qstats_*`, `pcie_ctx_hw_stats`, and `pcie_ctx_hw_stats_v2`, with signal integrity, traffic, LTSSM, recovery, credit, completion timing/header, latency histogram, and packet counters.
- `hwrm_stat_generic_qstats_*`, `generic_sw_hw_stats`, and `hwrm_stat_db_error_qstats_*` for generic PCIe/credit/cache/doorbell recovery and doorbell-drop counters.
- `hwrm_stat_query_roce_stats_*`, `stat_query_roce_stats_data`, `hwrm_stat_query_roce_stats_ext_*`, and `stat_query_roce_stats_ext_data`, covering retransmits, NAKs, protection/memory/RDMA errors, QP counts, packet/byte counters, CNP/ECN, and DCN payload-cut counters.

Firmware and structured-data layouts include:

- `hwrm_fw_reset_*`, `hwrm_fw_qstatus_*`, `hwrm_fw_set_time_*`, and `hwrm_fw_get_time_*`.
- `hwrm_struct_hdr` and structured payloads for DCBX ETS/PFC/app/feature-state, LLDP state and TLVs, port description, RSS v2, power backup info, peer memory maps, MSI-X-per-VF, and debug token claims.
- `hwrm_fw_set_structured_data_*` and `hwrm_fw_get_structured_data_*`, transferring typed structured data through DMA buffers.
- `hwrm_fw_ipc_msg_*` and `hwrm_fw_ipc_mailbox_*` for firmware processor IPC and mailbox events.
- `hwrm_fw_ecn_*`, `hwrm_fw_health_check_*`, `hwrm_fw_livepatch_query_*`, `hwrm_fw_livepatch_*`, `hwrm_fw_sync_*`, `hwrm_fw_state_*`, and `hwrm_fw_secure_cfg_*`.
- `hwrm_exec_fwd_resp_*`, `hwrm_reject_fwd_resp_*`, `hwrm_fwd_resp_*`, and `hwrm_fwd_async_event_cmpl_*` for encapsulated request/response forwarding.
- `hwrm_temp_monitor_query_*`, `hwrm_reg_power_query_*`, `hwrm_core_frequency_query_*`, `hwrm_reg_power_histogram_*`, `hwrm_monitor_pax_histogram_start_*`, and `hwrm_monitor_pax_histogram_collect_*`.

WoL, debug, coredump, and NVM layouts include:

- `hwrm_wol_filter_alloc_*`, `hwrm_wol_filter_free_*`, `hwrm_wol_filter_qcfg_*`, and `hwrm_wol_reason_qcfg_*` for magic-packet and bitmap-pattern wake filters.
- `hwrm_dbg_qcaps_*`, `hwrm_dbg_qcfg_*`, `hwrm_dbg_crashdump_medium_cfg_*`, `coredump_segment_record`, `hwrm_dbg_coredump_list_*`, `hwrm_dbg_coredump_initiate_*`, `coredump_data_hdr`, and `hwrm_dbg_coredump_retrieve_*`.
- Shared `HWRM_NVM_COMMON_CMD_ERR_*` codes and NVM commands for raw block writes, directory-indexed reads, raw dumps, directory listing/info, NVM writes/modifies, directory entry find/erase/modify, device info, update verification, and update installation.

## Control Flow and Resource Lifecycle

Although this header contains no functions, the command lifecycle encoded by the structs is clear:

1. Driver code allocates and zeroes a command input struct matching the HWRM request type.
2. It fills the common request header, sets `resp_addr` to a DMA-accessible response buffer, and sets optional `flags`/`enables` bits for fields it wants firmware to consume.
3. If the command transfers large data, the driver allocates DMA buffers and passes their address and size fields. Examples include statistics buffers, RSS ring/hash tables, DSCP maps, multicast/VLAN tables, structured data, crashdump buffers, WoL patterns, firmware livepatch payloads, firmware-state backup/restore page directories, and NVM read/write buffers.
4. Firmware writes the output struct and sets `valid` when the response is complete. The driver must not treat the body as stable until response completion is observed by the HWRM transport.
5. For allocator commands, the driver stores returned IDs and later passes them to config/query/free commands. Ring/VNIC/filter/stat/WoL/NVM directory lifecycles all follow this pattern.

Important encoded lifecycles:

- VNICs: `hwrm_vnic_alloc_output.vnic_id` feeds update/config/query/free, TPA, RSS, placement, RX-mask, and filter commands.
- Rings: `hwrm_ring_alloc_output.ring_id` feeds free/reset/aggregation config; `logical_ring_id`, `push_buffer_index`, and `cq_handle` bind the firmware resource to the driver's ring bookkeeping.
- Ring groups: `hwrm_ring_grp_alloc_input` binds completion, RX, aggregation, and stat-context IDs into one group used by VNIC defaults.
- Filters: L2, tunnel, and n-tuple allocation outputs produce filter IDs and flow IDs; later config/free calls require those IDs.
- Stats: `hwrm_stat_ctx_alloc_input.stats_dma_addr` and returned `stat_ctx_id` establish persistent firmware updates into host memory until free/clear.
- Firmware state: quiesce, backup, restore, and unquiesce are staged commands with completion/status bits and page-directory DMA.
- NVM update: raw writes/read/dump and directory operations prepare or inspect NVM items; verify/install commands validate and activate staged items. The visible install response begins reporting `installed_items`, detailed `result`, `problem_item`, and reset requirement, with the response continuing in the next chunk.

## State and Persistence Behavior

Most structs are transient command or response buffers, but they control persistent hardware/firmware state:

- Port PHY/MAC settings, LEDs, PFC, DSCP maps, CoS bandwidth, queue profiles, VNIC settings, RSS keys/tables, ring resources, filters, tunnel ports, stat contexts, WoL filters, debug crashdump destinations, secure firmware settings, firmware structured data, livepatch state, firmware backup/restore images, and NVM contents can outlive a single HWRM request.
- Counter query commands may optionally clear counters via `COUNTER_MASK` flags or explicit clear commands, so reads are not always side-effect free.
- Firmware reset, sync, livepatch, NVM install, secure config, and state restore can require PCI or power resets and may alter firmware execution or persistent flash contents.
- Debug token claims and secure config structures encode authorization/security-sensitive state such as NVM/GRC/UART access and debug privilege claims.

The header itself stores no runtime state. It is compile-time ABI metadata; state exists in firmware, hardware tables, DMA buffers owned by the driver, and persistent NVM.

## Dependencies and Integration Points

This chunk depends on the wider BNGE HWRM transport and driver code to:

- Provide definitions for `u8`, `__le16`, `__le32`, `__le64`, `__be16`, and `__s32`.
- Serialize command structs exactly as declared and with firmware-compatible alignment and sizes.
- Allocate coherent or DMA-mapped buffers for request/response bodies and host-address fields.
- Convert endian-tagged fields correctly with kernel endian helpers.
- Poll or wait for HWRM completion and `valid` semantics.
- Map high-level kernel subsystems to firmware commands: netdev port stats and ethtool stats, PTP hardware clock support, DCB/PFC/ETS, RSS/indirection table programming, ring allocation and NAPI interrupt moderation, Rx mode and VLAN/multicast filtering, tunnel offload, devlink health/flash/update/debug operations, WoL, and RoCE telemetry.

The source path is under a Ceph client tree snapshot, but the file itself is a network-driver hardware interface header; no Ceph filesystem control path is visible in this chunk.

## Risks and Edge Cases

- ABI drift is the main risk. Any size, field order, endian type, bit value, or reserved padding mismatch can make firmware interpret driver commands incorrectly.
- `enables` bits must match populated fields. Setting an enable without a valid value, or filling a field without its enable bit, changes command semantics.
- Several bitfields reuse similar names across request and response structs but have different masks or shifts. Copy/paste mistakes in driver code can silently program wrong units, paths, or modes.
- DMA buffer fields carry strong lifetime and size requirements. Passing an unmapped, undersized, misaligned, or wrong-direction buffer can cause firmware DMA failures or memory corruption.
- Counter queries with clear flags are destructive from an observability perspective; tests and tools must distinguish read-only queries from read-and-clear queries.
- Allocation/free lifecycles can leak firmware resources if errors or resets skip cleanup, especially VNICs, rings, ring groups, filters, stat contexts, tunnel ports, and WoL filters.
- NVM, livepatch, firmware sync, secure config, and state restore commands are high-risk because they can alter persistent firmware, require resets, trigger anti-rollback/security checks, or fail partway through an update.
- Debug and coredump paths expose large DMA transfers and potentially restricted register/coredump data; capability flags such as `REG_ACCESS_RESTRICTED` and component disable masks must be honored.
- The chunk ends mid-definition of `hwrm_nvm_install_update_output`, so any generated analysis of install-result handling must include the next chunk for the complete result enum, `problem_item`, reset requirement, and following command error struct.

## Test and Validation Signals

Useful validation for this chunk is ABI and integration oriented:

- Compile the BNGE driver against this header with warnings enabled; incompatible type names, duplicate constants, or incomplete struct references should fail quickly.
- Add or run static assertions in driver code for selected HWRM struct sizes that firmware expects, especially large or DMA-facing structs such as queue CoS bandwidth, ring alloc, CFA filters, stats buffers, coredump records, and NVM commands.
- Exercise HWRM request/response paths on supported hardware or firmware simulation for representative commands: port stats, PHY caps, queue caps, VNIC/RSS config, ring allocation, L2 filter allocation, stat context allocation/query, firmware health, WoL query, coredump list, and NVM get-dir-info.
- Validate endian conversions in command builders and response parsers; raw use of `__le*` fields in arithmetic or conditionals is a review signal.
- Validate DMA size reporting: firmware-returned `*_stat_size`, `data_len`, `entry_cnt`, `total_segments`, and `resp_len` should be bounded by the host buffer length the driver supplied.
- Run reset/error-injection tests around allocation lifecycles to confirm frees are issued or resources are reclaimed after partial failures.
- For NVM/update commands, test negative result codes such as no space, anti-rollback, invalid signature/checksum, item locked, and reset-required handling without writing unintended flash regions.
- For interrupt aggregation and ring commands, confirm timer/count values are within capability min/max ranges returned by `hwrm_ring_aggint_qcaps_output`.

## Cross-Chunk Notes

This chunk begins immediately after the input side of `hwrm_port_mac_cfg_input` from an earlier chunk and includes only the output response. It ends inside `hwrm_nvm_install_update_output`; the next chunk must complete that response's result constants and the following `hwrm_nvm_install_update_cmd_err`/flush structures. The final merged per-file research should treat this file as a generated HWRM ABI catalog rather than ordinary handwritten driver logic.
