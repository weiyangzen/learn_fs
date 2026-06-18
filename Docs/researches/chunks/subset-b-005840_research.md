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
