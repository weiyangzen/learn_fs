# Research: sources/distributed-fs/ceph-client/include/linux/bnge/hsi.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005840`: lines 1-5193, `Docs/researches/chunks/subset-b-005840_research.md`
- `subset-b-005841`: lines 5194-12027, `Docs/researches/chunks/subset-b-005841_research.md`
- `subset-b-005842`: lines 12028-12609, `Docs/researches/chunks/subset-b-005842_research.md`

## Chunk Research

### subset-b-005840: lines 1-5193

# sources/distributed-fs/ceph-client/include/linux/bnge/hsi.h lines 1-5193

## Purpose

This chunk is the opening portion of Broadcom BNGE's generated HSI header for the HWRM firmware interface. It is not executable logic; it is the wire contract between the Linux client driver and BNGE/NetXtreme firmware. The definitions describe mailbox command headers, response headers, TLV wrapping, command IDs, return codes, completion records, asynchronous event records, and many request/response payloads for function management, backing-store registration, error recovery, PTP/time features, doorbell pacing, and early port PHY/MAC configuration.

The file is explicitly generated (`DO NOT MODIFY`) and uses fixed-width Linux endian types (`__le16`, `__le32`, `__le64`, `__be16`, `__be32`, `u8`, `__s32`) so host-side code can build exact DMA/mailbox layouts consumed by firmware. The source path matters because downstream driver code should include this header directly rather than redefining these ABI layouts.

## Important APIs, Types, And Constants

- Generic command framing starts with `struct hwrm_cmd_hdr`, `struct hwrm_resp_hdr`, generic aliases `struct input`/`struct output`, and `struct hwrm_short_input`. These establish the common request fields (`req_type`, completion ring, sequence ID, target ID, response DMA address) and common response fields (`error_code`, echoed request type, sequence ID, response length).
- TLV support is represented by `CMD_DISCR_TLV_ENCAP`, `struct tlv`, and `TLV_TYPE_*` constants. TLVs can carry normal HWRM requests/responses, RoCE congestion-control messages, and CKV/crypto-engine material such as IVs, auth tags, ciphertext, ECC public keys, algorithms, and ECDSA signatures. `TLV_FLAGS_MORE` and `TLV_FLAGS_REQUIRED` describe chaining and mandatory handling.
- `struct cmd_nums` is the central command-number namespace. The chunk includes command IDs across function, port, queue, VNIC, ring, CFA/flow, firmware, manufacturing, TruFlow/TFC, management-filter, debug, and NVM domains. `HWRM_LAST` is `HWRM_NVM_RAW_WRITE_BLK`.
- `struct ret_codes` and `struct hwrm_err_output` define firmware return semantics, including success, invalid parameters/flags/enables, resource errors, unsupported TLVs/options, reset/busy/locked conditions, secure SoC errors, TLV-encapsulated responses, unknown errors, and command-not-supported. Error responses may include an extra `cmd_err` byte for command-specific detail.
- Version and global size constants include `HWRM_VERSION_STR "1.15.1.1"`, `HWRM_MAX_REQ_LEN 128`, `HWRM_MAX_RESP_LEN 704`, target IDs for BONO/KONG/APE/tools, hash sizes, and `HWRM_RESP_VALID_KEY`.
- `hwrm_ver_get_input` and `hwrm_ver_get_output` are the handshake records. The output reports HWRM, management, network-controller, and RoCE firmware versions, device capability flags, chip identity/platform, default and maximum request/response lengths, timeout values, PSP/RoCE limits, extended version fields, and a final `valid` marker.
- Completion formats include `eject_cmpl`, `hwrm_cmpl`, `hwrm_fwd_req_cmpl`, and `hwrm_fwd_resp_cmpl`. They encode completion type bits, valid bits, forwarded request/response buffer addresses, lengths, source IDs, and buffer-error categories.
- `hwrm_async_event_cmpl` is the generic async event, followed by typed variants for link status, port connection policy, link speed config changes, reset notification, error recovery, ring monitor messages, VF config changes, default VNIC allocation/free, flow aging, EEM cache flush, deferred responses, echo requests, PHC/PPS events, error reports, debug-buffer producer notifications, and HWRM errors.
- Function-management request/response types cover reset, FID lookup, VF allocation/free/configuration, function capability/configuration query, function configuration, stats query/clear, VF resource release, driver register/unregister/query-version, request/response buffer registration, resource capabilities, VF resource configuration, backing-store capabilities/configuration, error-recovery configuration, echo responses, PTP pin/time configuration, timed-TX pacing profile/rate query, key-context allocation/free, backing-store v2 config/query/capability flows, doorbell pacing query, and driver interface up/down notification.
- Backing-store helpers include `struct tqm_fp_ring_cfg` and split-entry structs (`qpc_split_entries`, `srq_split_entries`, `cq_split_entries`, `vnic_split_entries`, `mrav_split_entries`, `ts_split_entries`, `ck_split_entries`, `mr_split_entries`, `av_split_entries`, `sq_split_entries`). These pack per-context sub-counts into the v2 backing-store split-entry fields.
- Port definitions in this chunk begin with `hwrm_port_phy_cfg_input`, `hwrm_port_phy_cfg_output`, `hwrm_port_phy_cfg_cmd_err`, `hwrm_port_phy_qcfg_input`, `hwrm_port_phy_qcfg_output`, and the start of `hwrm_port_mac_cfg_input`. They define link speed, autonegotiation, pause, EEE, FEC, PAM4, speeds2, link training, precoding, PHY type/media/module status, transceiver identity, link-down reason, active lanes, MAC QoS maps, timestamp-capture flags, and PTP load controls. This chunk stops before `hwrm_port_mac_cfg_input` is complete.

## Control Flow And Firmware Protocol Shape

Driver-side control flow is implied by the ABI rather than implemented here:

1. Populate an input struct with a command number from `HWRM_*`, a sequence ID, target ID, completion ring, and response DMA address.
2. Set request-specific `flags` and `enables` bits before filling optional fields. Most configuration records use `enables` masks so firmware can distinguish "leave unchanged" from "set to zero".
3. Submit the command through the BNGE HWRM transport implemented elsewhere.
4. Read the response header, validate matching `req_type`/`seq_id`, check `error_code`, and only trust command-specific response fields after firmware sets the trailing `valid` byte.
5. Process completion-ring entries and async events using the low type bits and valid bit. Typed async-event structs overlay the same 16-byte base shape and reinterpret `event_data1`/`event_data2` according to `event_id`.

Forwarding adds a second path: `hwrm_fwd_req_cmpl` and `hwrm_fwd_resp_cmpl` describe firmware-delivered request/response buffers for PF/VF or management forwarding. Driver registration (`hwrm_func_drv_rgtr_input`) advertises forwarding masks and supported modes, so the firmware can decide which events or VF requests are delivered to this driver.

Backing-store control flow is two-stage. The legacy path queries aggregate limits via `hwrm_func_backing_store_qcaps_output` and configures all backing stores in one large `hwrm_func_backing_store_cfg_input`. The v2 path queries/configures a single backing-store `type`/`instance` at a time, with page directory, entry count, entry size, page size, PBL level, split entries, and an "all done" flag. Capability flags indicate driver-managed memory, context-kind initialization, physical PBL preference, exact split counts, and next backing-store offsets.

## State And Persistence Behavior

- This header itself has no mutable runtime state or persistence. It is a generated compile-time ABI description.
- The structs describe persistent or semi-persistent device state held by firmware/hardware: function resources, VF allocations, MAC addresses, VLAN/MTU settings, bandwidth limits, driver registration state, backing-store DMA page directories, key-context partitions, PTP/PHC configuration, error-recovery register locations, doorbell pacing registers, and port PHY/MAC settings.
- DMA addresses and page directories (`resp_addr`, request/response buffer pages, backing-store page dirs, host key-context DMA buffers) are host-memory contracts. Their lifetime and DMA mapping correctness are managed by driver code outside this header, but firmware may retain them until an unregister/free/reconfigure command or reset.
- Statistics queries expose firmware-maintained counters and clear-sequence markers. Clear commands mutate firmware counters, while query commands may optionally filter or mask L2/RoCE counters.
- Async events model firmware-originated state changes: reset, link state/config, PHC failover, doorbell threshold, debug-buffer production, VF config, VNIC lifecycle, flow aging, and error reports. Consumers must handle them as asynchronous updates to local driver state.

## Dependencies And Integration Points

- Depends on Linux kernel integer and endian typedefs already available to headers that include this file.
- Integrates with the BNGE HWRM mailbox/transport layer, completion-ring parser, async-event dispatcher, resource allocator, PTP/PHC support, devlink/debug/NVM tooling, SR-IOV management, RoCE/TLS/QUIC key-context provisioning, and port PHY/MAC configuration paths.
- `cmd_nums` values are the dispatch keys used by every HWRM request builder. Any mismatch between a request struct and its `HWRM_*` constant would cause firmware to decode the wrong payload.
- `valid` bytes and `HWRM_RESP_VALID_KEY` are synchronization points between DMA-written firmware responses and host polling/completion handling.
- Target IDs route commands to device processors or tools endpoints (`BONO`, `KONG`, `APE`, `TOOLS`), so transport code must preserve them exactly.
- Many structures expose hardware register address-space encodings (`PCIE_CFG`, `GRC`, `BAR0`, `BAR1`) for error recovery and doorbell pacing. Integration code must decode address-space bits before reading/writing registers.

## Risks And Edge Cases

- ABI drift is the main risk. The header is generated and should not be hand-edited; stale generated layouts or command numbers can break firmware communication even when C compilation succeeds.
- Structure packing must remain exactly as generated. The file relies on field ordering and fixed-size types rather than local helper accessors. Any compiler, include, or manual wrapping change that alters alignment would be high risk.
- Endianness handling is explicit. Host code must use the proper little-endian/big-endian conversion helpers when filling or reading multi-byte fields; default integer assignments can be wrong on non-little-endian hosts.
- `flags` and `enables` often contain paired enable/disable bits. Setting both sides, omitting an enable bit for a populated field, or setting an enable bit with an uninitialized field can produce firmware rejections or unintended configuration.
- DMA address fields are firmware-visible. Incorrect mapping, insufficient alignment/page-size encoding, stale mappings, or early unmap can cause data corruption or firmware errors.
- Response validity must be honored. Reading response payloads before `valid` is set or ignoring mismatched `seq_id` risks consuming stale DMA data.
- Some outputs are large (`hwrm_func_ttx_pacing_rate_query_output` is 528 bytes; `hwrm_ver_get_output` is 184 bytes; function/backing-store outputs are similarly broad). Callers must allocate buffers compatible with firmware-reported maximum response lengths and not assume `HWRM_MAX_RESP_LEN` if version negotiation reports different limits.
- Async event variants share the same base layout. Dispatch must check `event_id` before using a typed overlay; otherwise `event_data1`/`event_data2` masks will be misinterpreted.
- This chunk ends at line 5193 in the middle of `hwrm_port_mac_cfg_input`; subsequent fields and the corresponding output struct are outside this chunk and should be reconciled by the later merge lane.

## Test Signals

- Compile coverage for all users that include `include/linux/bnge/hsi.h`; generated struct names and constants should resolve without local redefinition.
- Static size/layout checks in driver tests or build-time assertions, if present, should confirm important wire sizes such as 16-byte headers/completions, 16-byte generic outputs, 184-byte version output, 336-byte legacy backing-store config, and 64-byte backing-store v2 config.
- HWRM version negotiation should return a supported interface version, coherent max request/response lengths, and a valid byte set.
- Function capability/configuration tests should exercise `hwrm_func_qcaps`, `hwrm_func_qcfg`, and `hwrm_func_cfg` with optional fields gated by `enables`.
- SR-IOV tests should allocate/free VFs, configure VF resources, and verify async VF config-change events decode correctly.
- Backing-store tests should cover both legacy and v2 paths, including page-size/PBL-level encodings, split-entry fields, all-done signaling, and command-specific error codes.
- Error-recovery tests should verify register address-space decoding and reset-notification/error-recovery async events.
- PTP/PHC tests should query/config pins, timestamps, PHC failover state, PPS timestamp async events, and MAC timestamp-capture flags.
- Port link tests should configure/query PHY speeds, autoneg, FEC, PAM4/speeds2, EEE, link training, precoding, and validate link-status/link-speed async events.
- Negative tests should cover unsupported command IDs, invalid flags/enables, invalid backing-store type/instance, conflicting PHY/MAC enable/disable bits, and timeout/busy/reset-progress return codes.

### subset-b-005841: lines 5194-12027

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

### subset-b-005842: lines 12028-12609

# sources/distributed-fs/ceph-client/include/linux/bnge/hsi.h lines 12028-12609

## Scope

This chunk is the final section of the Broadcom NetGExreme (`bnge`) HSI header. It starts in the middle of `hwrm_nvm_install_update_output`, then defines the remaining NVM command error/result contracts, NVM variable/profile/VPD command payloads, firmware self-test command payloads, doorbell record formats, firmware status bits, the host-communication status locator, and the header guard close.

The file is a firmware ABI definition, not executable driver logic. All structs are packed-by-layout C declarations with little-endian integer fields where the HWRM protocol crosses the host/firmware boundary. The surrounding BNGE driver includes this header from HWRM helper, netdev, TX/RX, resource, and devlink code; closely matching BNXT code in the same source tree shows the same HWRM contracts being used for devlink NVM parameters, ethtool self-tests, firmware package update defrag, and firmware health status mapping.

## Purpose

The chunk provides the typed ABI surface for late-stage firmware management and low-level runtime signaling:

- NVM install/update result tails communicate why a firmware package install failed, which package item was responsible, and whether PCI or power reset is required afterward.
- NVM flush, get/set variable, defrag, VPD field, and profile commands define the request/response buffers sent through HWRM for persistent firmware configuration and package maintenance.
- Self-test query/execute/IRQ commands expose firmware diagnostics to host tools such as ethtool-style self tests.
- `dbc_dbc`, `db_push_start`, `db_push_end`, and `db_push_info` define 64-bit doorbell and doorbell-push record bit layouts for queue notification, queue arming, and debug tracing paths.
- `fw_status_reg` and `hcomm_status` define the firmware-health status register bits and a discoverable host-communication structure used to locate that status register in PCI config, GRC, BAR0, or BAR1 space.

Because these definitions sit in an exported kernel include path under `include/linux/bnge`, they are the source of truth for BNGE's binary contract with Broadcom firmware. The driver code should not reinterpret these fields with independent constants unless those constants are deliberately mirrored for convenience, as `bnge_db.h` does for doorbell writes.

## Important APIs, Types, and Constants

### NVM install/update tail

The chunk begins with the final result constants in `struct hwrm_nvm_install_update_output`. These include unsupported subsystem/platform result codes, duplicate and zero-length item failures, checksum/data/authentication failures during install, item-not-found, and item-locked. The following fields complete the response:

- `problem_item`: reports no problem item or the package as the problem item.
- `reset_required`: reports none, PCI reset, or power reset.
- `valid`: firmware-owned response-valid marker common to HWRM outputs.

`struct hwrm_nvm_install_update_cmd_err` is the command-error side channel for install/update failures. It distinguishes generic unknown errors from fragmentation, no-space, anti-rollback, missing voltage-regulator support, defrag failure, and unknown directory errors. In the older BNXT ethtool path, matching install result codes are mapped into user-visible extack errors such as invalid image, authentication error, unsupported device, no space, or internal error; BNGE can use the same HSI meanings when adding or reviewing firmware update paths.

### NVM flush and variable commands

`struct hwrm_nvm_flush_input/output/cmd_err` define a small no-payload HWRM command that asks firmware to flush pending NVM state. The error extension only distinguishes unknown from fail, so callers must rely on the main HWRM `error_code` for most transport/status handling.

`struct hwrm_nvm_get_variable_input` and `struct hwrm_nvm_set_variable_input` are 40-byte requests for persistent option variables. Their common fields are:

- HWRM header fields: `req_type`, `cmpl_ring`, `seq_id`, `target_id`, and `resp_addr`.
- DMA payload address: `dest_data_addr` for reads and `src_data_addr` for writes.
- `data_len`: the option data length, represented by the HWRM contract for the selected option.
- `option_num`: the NVM option identifier, with only reserved sentinels defined in this header chunk.
- `dimensions` and `index_0` through `index_3`: selectors for scalar or array-like option instances, such as per-port or per-function configuration.
- `flags`: get supports factory-default reads and option-value validation; set supports force-flush, encryption/authentication modes, and factory-default writes.

`struct hwrm_nvm_get_variable_output` returns `data_len`, `option_num`, validation flags, and `valid`; set only returns the standard HWRM output header plus `valid`. Their command-error structs enumerate variable-not-found, corrupt variable, short length, invalid index, access denied, callback failure, invalid data length, and no-memory cases; set additionally reports unsupported action.

In the matching BNXT devlink implementation, `HWRM_NVM_GET_VARIABLE` and `HWRM_NVM_SET_VARIABLE` allocate an HWRM DMA slice, set `dest_data_addr`, `data_len`, `option_num`, `index_0`, and `dimensions`, and translate `NVM_GET_VARIABLE_CMD_ERR_CODE_VAR_NOT_EXIST` to `-EOPNOTSUPP`. That is a useful integration model for BNGE because the same field semantics determine how devlink parameters should persist in firmware NVM.

### NVM defrag, VPD, and profile commands

`struct hwrm_nvm_defrag_input/output/cmd_err` define a 24-byte request with `NVM_DEFRAG_REQ_FLAGS_DEFRAG`. The error extension distinguishes unknown, fail, and check-fail. In the matching BNXT firmware package resize flow, a failed update-area resize caused by `-ENOSPC` triggers `HWRM_NVM_DEFRAG` once before retrying the resize, so this ABI is part of firmware update reliability and space recovery.

`struct hwrm_nvm_get_vpd_field_info_input/output/cmd_err` and `struct hwrm_nvm_set_vpd_field_info_input/output` provide tag-based VPD field access. Get accepts a two-byte `tag_id` and returns up to 256 bytes plus `data_len`; set provides `host_src_addr`, `tag_id`, and `data_len`. Get-specific command errors cover not-cached, VPD parse failure, and invalid tag ID. BNGE devlink currently reads board part number and serial number through PCI VPD helper APIs, but these HWRM VPD definitions are the firmware-managed alternative for VPD keyword access.

`struct hwrm_nvm_set_profile_input/output/cmd_err` and `struct hwrm_nvm_set_profile_sb` describe profile writes composed of option sub-blocks. The request points to a DMA block at `src_data_addr`, provides total `data_len`, `option_count`, flags, and `profile_type`. Defined flags support force-flush, validate-only, and factory-default behavior. The only named profile type in this chunk is `EROCE`, tying profile provisioning to RDMA/RoCE capability. The command-error payload includes `err_index`, allowing firmware to report which sub-block failed, and adds `PROVISION_ERROR` beyond the ordinary NVM variable errors. Each `hwrm_nvm_set_profile_sb` contains one option's data length, option number, dimensional selectors, and reserved flags.

### Self-test commands

`struct hwrm_selftest_qlist_input/output` lets the host ask firmware which tests are available. The output includes:

- `num_tests`.
- `available_tests` and `offline_tests` bitmasks for NVM, link, register, memory, PCIe SerDes, and Ethernet SerDes tests.
- `test_timeout`, eight fixed-width test names, and `eyescope_target_BER_support` levels from BER 1e8 through 1e12.

`struct hwrm_selftest_exec_input/output` executes a selected test mask and returns `requested_tests` and `test_success` bitmasks using the same six firmware test bits. `struct hwrm_selftest_irq_input/output` verifies interrupt delivery for a supplied completion ring.

The matching BNXT ethtool path queries `HWRM_SELFTEST_QLIST` at initialization to size and name test entries, uses `resp->test_timeout` for `HWRM_SELFTEST_EXEC`, and copies `resp->test_success` into ethtool results. It also loops over completion rings and sends `HWRM_SELFTEST_IRQ` with each ring's firmware ID. BNGE has the same HWRM command definitions available if it wires equivalent ethtool diagnostics.

### Doorbell records

`struct dbc_dbc` is an 8-byte doorbell completion/debug record split into:

- `index`: a 24-bit producer/consumer index plus epoch and toggle bits.
- `type_path_xid`: a 20-bit queue XID, path selector (`ROCE`, `L2`, or `ENGINE`), valid/debug-trace flags, and a 4-bit doorbell type.

The doorbell types include SQ, RQ, SRQ, SRQ arm variants, CQ, CQ arm variants, CQ cutoff ack, NQ, NQ arm, CQ reassign, NQ mask, and null.

`struct db_push_start` and `struct db_push_end` are 64-bit packed MMIO payload formats for push-start and push-end doorbells. They carry a 24-bit index, split producer index low/high bits, 20-bit XID, type, and for push-end also path and debug-trace fields. `struct db_push_info` records a 24-bit push index and 5-bit push size.

BNGE driver doorbell helpers mirror these layouts in `bnge_db.h` and `bnge_netdev` code with `DBR_*` constants. Ring allocation builds `db_key64` from path, ring type, XID, and valid bit; TX/RX and completion paths then OR in `DB_RING_IDX()` and issue 64-bit writes to the doorbell BAR. On 32-bit hosts, `bnge_writeq()` serializes the split 64-bit write under `bd->db_lock`, matching the ABI requirement that doorbell writes be atomic from firmware's perspective.

### Firmware status and host-communication locator

`struct fw_status_reg` defines a 32-bit firmware health word. The low 16 bits carry the status code, with `FW_STATUS_REG_CODE_READY` as the named ready value. Higher bits indicate degraded image, recoverable condition, crashdump ongoing/complete, shutdown, crashed-with-no-master, recovering, and manufacturing debug status.

`struct hcomm_status` defines an 8-byte discovery record:

- `sig_ver`: version in the low byte and signature in the upper 24 bits. The signature value is `0x484353 << 8`.
- `fw_status_loc`: a packed location whose low two bits select address space (`PCIE_CFG`, `GRC`, `BAR0`, or `BAR1`) and whose upper bits give the aligned offset.

`HCOMM_STATUS_STRUCT_LOC` is the fixed GRC address `0x31001F0` used to find the `hcomm_status` record. Matching BNXT health code maps this address, checks the signature, reads `fw_status_loc`, and falls back to a known P5 BAR0 status register when the signature is absent on supported chips. It then uses `FW_STATUS_REG_CRASHED_NO_MASTER` to trigger OP-TEE firmware reset. BNGE should preserve the same interpretation when adding or auditing firmware health handling.

## Control Flow and Data Flow

These declarations do not execute by themselves; their control flow is imposed by HWRM request helpers:

1. Driver code allocates a typed request with an HWRM helper and command ID such as `HWRM_NVM_GET_VARIABLE`, `HWRM_NVM_DEFRAG`, or `HWRM_SELFTEST_EXEC`.
2. The helper initializes common header fields and points `resp_addr` at a DMA response buffer.
3. The caller fills command-specific fields from this chunk: DMA data addresses, option selectors, flags, tag IDs, profile metadata, test masks, completion ring IDs, or defrag flags.
4. The request is sent to firmware, usually synchronously.
5. The driver reads the typed output only after successful HWRM completion and valid response ownership, then maps `error_code`, command-specific `cmd_err`, and result/status fields into kernel errors or user-visible diagnostics.

Doorbell flow is MMIO rather than HWRM:

1. Ring setup assigns each queue/ring an XID and a doorbell BAR address.
2. The driver precomputes the stable `db_key64` fields: path, type, XID, and valid bit.
3. Runtime TX/RX/CQ/NQ code ORs in the ring index, epoch/toggle fields, and arm/mask type as needed.
4. A 64-bit MMIO write notifies hardware/firmware of new producer index or interrupt-arm state.

Firmware health flow is register-based:

1. The host maps `HCOMM_STATUS_STRUCT_LOC`.
2. It validates the `hcomm_status` signature/version.
3. It decodes the real firmware status register address space and offset.
4. Periodic or recovery code reads `fw_status_reg` bits and decides whether firmware is healthy, recovering, crashed, or requesting an out-of-band reset path.

## State and Persistence Behavior

Most structs in this chunk are transient command or MMIO formats, but several operations affect persistent device state:

- NVM variable writes persist firmware options across driver reload and device reset unless sent as validate-only or factory-default operations.
- `FORCE_FLUSH` on NVM set/profile requests and explicit `HWRM_NVM_FLUSH` control when staged NVM changes are committed to nonvolatile storage.
- NVM defrag reorganizes persistent NVM directory/storage layout to recover space; failure can block firmware package updates.
- VPD field writes update device identity/configuration fields that can be observed by firmware, PCI VPD tooling, or inventory systems.
- NVM install/update result fields report whether the newly installed package requires a PCI function reset or full power cycle before becoming active.
- Self-test commands are diagnostic and should not normally persist state, but offline tests can disrupt link or device operation while running.
- Doorbell writes update hardware-visible queue producer/arm state and are not persistent beyond queue lifetime.
- Firmware status and host-communication records are device runtime state; they survive long enough for crash/recovery coordination but are not normal configuration storage.

## Dependencies and Integration Points

This chunk depends on kernel fixed-width and endian types such as `u8`, `u32`, `u64`, `__le16`, `__le32`, and `__le64`. It also depends on the HWRM command ID namespace defined earlier in the same header, including `HWRM_SELFTEST_QLIST`, `HWRM_SELFTEST_EXEC`, `HWRM_SELFTEST_IRQ`, `HWRM_NVM_SET_PROFILE`, `HWRM_NVM_GET_VPD_FIELD_INFO`, `HWRM_NVM_SET_VPD_FIELD_INFO`, `HWRM_NVM_DEFRAG`, `HWRM_NVM_FLUSH`, `HWRM_NVM_GET_VARIABLE`, `HWRM_NVM_SET_VARIABLE`, and `HWRM_NVM_INSTALL_UPDATE`.

Driver integration points include:

- `drivers/net/ethernet/broadcom/bnge/bnge_hwrm.c` and `bnge_hwrm_lib.c`, which allocate/send HWRM requests and include this HSI header.
- `drivers/net/ethernet/broadcom/bnge/bnge_db.h`, `bnge.h`, `bnge_netdev.c`, and `bnge_txrx.c`, which mirror the doorbell layouts and issue 64-bit doorbell writes.
- `drivers/net/ethernet/broadcom/bnge/bnge_devlink.c`, which already consumes nearby NVM device-info HWRM structs and could use the variable/VPD/profile definitions for additional persistent devlink controls.
- Matching `drivers/net/ethernet/broadcom/bnxt` code, which is not BNGE code but is a strong in-tree reference for the same Broadcom HWRM ABI: devlink NVM get/set variable handling, NVM defrag during firmware package resize, ethtool self-test qlist/exec/irq, and firmware health status discovery through `hcomm_status`.
- RDMA/RoCE integration through the `EROCE` profile type and the doorbell path selector values for `ROCE` versus `L2`.

## Risks

- ABI drift is the main risk. Field offsets, sizes, endian annotations, and bit masks must exactly match firmware; changing a struct member or constant can silently break firmware commands.
- The chunk starts mid-struct, so merge/reconciliation should include the preceding `hwrm_nvm_install_update_input/output` fields to give complete install/update semantics.
- NVM write/profile/VPD commands can permanently alter device state. Callers need privilege checks, accurate `data_len` units, correct DMA direction, and careful handling of `FORCE_FLUSH`, factory-default, validation, and encryption/authentication flags.
- `dimensions` and `index_0..index_3` are easy to misuse. A wrong index can read or modify a different port/function/profile instance than intended.
- Command-specific error codes must not be flattened too early. For example, variable-not-found often means unsupported option, while access-denied means an admin/privilege issue.
- Defrag and install/update operations can be long-running and disruptive. Callers need suitable HWRM timeouts and must handle no-space, anti-rollback, voltage-regulator, authentication, and reset-required outcomes distinctly.
- Self-tests may require PF privileges and offline state. Running offline diagnostics while RDMA, traffic, or auxiliary devices are active can cause false failures or operational disruption.
- Doorbell bit composition must remain synchronized with the HSI definitions. Incorrect XID, path, type, epoch, toggle, valid, or mask bits can stall queues, drop completions, or arm interrupts incorrectly.
- Atomicity of 64-bit doorbell writes matters on 32-bit systems; bypassing `bnge_writeq()` can expose torn writes.
- Firmware status location decoding requires validating `hcomm_status` signature/version and address space before reading; otherwise recovery code may read the wrong register and misclassify firmware health.

## Test and Validation Signals

Useful validation for this chunk is ABI and integration oriented:

- Build BNGE and any code including `<linux/bnge/hsi.h>` with warnings enabled; this catches missing type definitions and incompatible struct references.
- Add or run compile-time layout checks if available for generated HSI headers, especially the documented sizes: 16-byte flush outputs, 40-byte variable requests, 272-byte VPD get output, 280-byte selftest qlist output, and 8-byte doorbell/status records.
- Exercise HWRM NVM get/set variable paths on hardware or firmware simulation with valid, nonexistent, access-denied, invalid-index, and short-length options, verifying command-error translation.
- Test NVM defrag as part of a firmware package update flow where update-area resize first returns no space, then succeeds after one defrag retry.
- Validate VPD get with known two-byte tags and invalid tags; confirm returned `data_len` never exceeds the 256-byte output buffer.
- Validate profile set in both `VALIDATE_ONLY` and real write modes, including error-index reporting for a deliberately invalid sub-block.
- Run firmware self-test query and execution paths, checking that available/offline bitmasks, timeout, test names, requested tests, and success masks remain consistent.
- Run IRQ self-test against all completion rings and verify failures identify ring allocation or interrupt mapping issues rather than generic HWRM transport failure.
- Stress TX/RX/CQ/NQ doorbells under traffic and interrupt moderation; watch for queue stalls, missed completions, or unexpected debug/doorbell drop events.
- Simulate or observe firmware health transitions: ready, recovering, crashdump ongoing/complete, shutdown, and crashed-no-master. Confirm the host-communication locator maps the intended address space and recovery code chooses the correct reset path.

## Cross-Chunk Notes

The first visible lines belong to `hwrm_nvm_install_update_output`, whose request and initial output fields start in the previous chunk. Earlier chunks also define the HWRM command IDs and generic input/output header conventions used by every command here. The final per-file research pass should merge this tail with the earlier NVM directory/update sections and with BNGE driver usage notes so the complete report distinguishes BNGE-specific consumers from matching BNXT reference integrations.
