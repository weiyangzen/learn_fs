# sources/distributed-fs/ceph-client/include/linux/bnxt/hsi.h lines 1-5291

## Purpose

This chunk is the first half of Broadcom NetXtreme-C/E `bnxt` hardware-software interface definitions. It is explicitly generated and is not executable driver logic. Its role is to freeze the HWRM firmware ABI layouts, command numbers, response codes, completion records, asynchronous event records, function/resource management messages, error-recovery messages, PTP controls, backing-store contracts, doorbell pacing metadata, port PHY/MAC configuration messages, and the beginning of port statistic blocks used by the Linux `bnxt` client code.

The dominant pattern is a packed-looking C structure contract using Linux fixed-width endian types (`__le16`, `__le32`, `__le64`, `__be16`, `__be32`, `u8`) plus adjacent bit masks and enumerated constants. Callers are expected to fill request structs, set `req_type` from `HWRM_*` command numbers, DMA or mailbox-submit them to firmware, and parse the matching response struct only after checking `error_code`, `resp_len`, and `valid`.

## Important APIs, Types, and Constants

- Common request/response framing appears at lines 17-107: `struct hwrm_cmd_hdr`, `struct hwrm_resp_hdr`, generic `struct input`/`struct output`, TLV encapsulation via `struct tlv`, and short-command indirection via `struct hwrm_short_input`. These are the base wire formats for all later HWRM messages in the chunk.
- `struct cmd_nums` at lines 108-591 defines the global HWRM command namespace. This range includes core function, port, queue, VNIC, ring, CFA, NVM, debug, firmware, TruFlow/TFC, crypto/key, engine, PTP, backing-store, and statistics operations. Even when a command's payload is outside this chunk, its numeric discriminator is established here.
- `struct ret_codes` and `struct hwrm_err_output` at lines 592-633 define firmware result codes, including success, invalid parameters, resource denial/allocation failure, unsupported TLV/command, reset-in-progress, busy/locked, secure SoC errors, encapsulated TLV response, and command-specific `cmd_err` detail.
- HWRM protocol constants at lines 635-648 set max default request/response sizes, target IDs, response valid key, and interface version `1.10.3.151`.
- `hwrm_ver_get_input/output` at lines 650-756 is the version and capability probe. The response exposes HWRM/management/network-controller/RoCE firmware versions, chip identity, max request/response lengths, timeouts, feature flags such as short-command support, secure firmware update, flow-handle width, CFA/TFLIB/TruFlow, secure boot/SoC, debug token support, and extended version fields.
- Completion layouts at lines 757-830 include `eject_cmpl`, `hwrm_cmpl`, `hwrm_fwd_req_cmpl`, and `hwrm_fwd_resp_cmpl`. They define completion type IDs, valid bits, sequence IDs, forwarded source IDs, and request/response buffer address encodings.
- Async event layouts at lines 831-1596 cover generic events and typed overlays for link status/speed/config changes, reset notification, error recovery, ring monitor, VF config, default VNIC changes, HW flow aging, EEM flush, deferred response, echo request, PHC/PPS timestamps, debug-buffer producer, HWRM error, and error-report subtypes such as pause storm, invalid signal, NVM, doorbell drop, thermal, and unsupported dual data rate.
- Function-management HWRM structs start at line 1597. This chunk covers reset/get-FID/VF alloc/free/config, function capabilities/configuration/statistics, driver registration/unregistration/version query, forwarded buffer registration, VF resource release, function resource caps/configuration, and interface-change commands.
- Resource and backing-store structs at lines 2799-4209 define min/max resource limits for VFs and the firmware-owned/driver-owned context memory layout for QP, SRQ, CQ, VNIC, STAT, TQM rings, MRAV, TIM, key contexts, shadow doorbells, table scopes, XID partitions, and debug trace buffers. Both legacy all-in-one backing-store config and v2 per-type config/query/caps formats are present.
- Error recovery, echo, and PTP structs at lines 3448-3839 expose firmware health polling registers, reset register arrays and delays, echo response payloads, PTP pin state/usage, PPS/PTM timestamp query, PHC failover configuration, and extended PTP query state.
- Port controls at lines 4289-5055 cover PHY configuration/query, MAC configuration, MAC PTP register-offset query, FEC/link-training/precoding flags, NRZ/PAM4/PAM4_112/PAM4_224 signaling, speeds through 800G, transceiver metadata, pause/EEE/loopback/autoneg, link down reasons, timestamp capture, and PTP frequency/phase adjustment.
- Port statistics begin at lines 5056-5291 with `tx_port_stats`, `rx_port_stats`, `hwrm_port_qstats_*`, `tx_port_stats_ext`, and a partial `rx_port_stats_ext`. These are host memory DMA statistic blocks and response metadata for size/clear state.

## Control Flow and Message Flow

There are no functions or branches in this chunk, but the ABI implies repeated driver flows:

1. Capability discovery: allocate a response buffer, issue `HWRM_VER_GET` with `hwrm_ver_get_input`, check `hwrm_ver_get_output.valid`, then gate driver behavior on version, max request/response length, short-command requirement, timeout, and capability flags.
2. Command dispatch: populate a concrete request struct whose first fields match `hwrm_cmd_hdr`, set `req_type` to the matching `HWRM_*` value, select completion ring/target/response address, and submit through the bnxt HWRM transport. The response begins with the common response header and ends with `valid`.
3. Asynchronous handling: completion-ring consumers inspect `type` masks, then cast/interpret the 16-byte completion as generic or typed async-event overlays. Event-specific `event_data1`/`event_data2` masks drive link updates, reset coordination, VF notifications, deferred-response matching, PTP timestamp harvesting, and error reporting.
4. Function bring-up/configuration: query function caps/config (`hwrm_func_qcaps_*`, `hwrm_func_qcfg_*`), configure MTU/MRU/resources/MAC/VLAN/bandwidth/PTP/KTLS/QUIC/RDMA-related limits through `hwrm_func_cfg_input`, register the driver (`hwrm_func_drv_rgtr_input`) with OS/version/event-forwarding masks, and register request/response/error buffers with `hwrm_func_buf_rgtr_input`.
5. Backing-store setup: query legacy or v2 backing-store capabilities, allocate/page-map context memory with page size plus page-table level encodings, then submit either the large legacy `hwrm_func_backing_store_cfg_input` or one v2 type at a time. The `*_qcfg_v2` and split-entry structs support verification and resource partitioning.
6. Runtime monitoring: query error recovery to learn health/heartbeat/reset registers and poll timings, consume async reset/error events, query doorbell pacing registers, and collect function/port stats through response counters or host-addressed statistic blocks.
7. Port operations: configure PHY and MAC state by combining `flags` and `enables` bitmaps with speed, pause, FEC, loopback, timestamp, and PTP fields; query PHY/MAC/PTP state to drive netdev link mode reporting and timestamping support.

## State and Persistence Behavior

The header itself persists no runtime state. It defines the binary representation for state owned elsewhere:

- Firmware-visible state includes function configuration, VF allocations and resource reservations, backing-store registrations, driver registration, PTP/PHC settings, PHY/MAC state, error-recovery register state, and doorbell pacing state.
- Host-visible state includes response buffers, request/response/error buffer pages registered through `hwrm_func_buf_rgtr_input`, context/backing-store pages whose DMA addresses are passed to firmware, and statistic DMA buffers passed to `hwrm_port_qstats_input`.
- Many config structs use `enables` fields to make updates partial. A zeroed field is not necessarily written unless the corresponding enable bit is set; tests and callers must preserve this distinction.
- Many response structs reserve the last byte as `valid`; callers should not consume data until firmware writes the valid marker/key through the HWRM transport contract.
- Endianness is part of persistence: all multi-byte fields are little-endian except explicitly big-endian IP/TPID fields. In-memory direct interpretation without conversion is only correct on little-endian hosts and still should use the kernel endian helpers.

## Dependencies and Integration Points

- Depends on Linux integer/endian typedefs from the surrounding kernel include environment. The header does not include those definitions itself in this chunk.
- Integrates with the `bnxt` HWRM command path, completion-ring polling, async event worker paths, netdev link-state reporting, SR-IOV/VF management, devlink/ethtool statistics, PTP/PHC support, firmware reset/error recovery, RDMA/RoCE resource setup, and newer offload features such as KTLS, QUIC, TruFlow/TFC, doorbell pacing, and hardware coalescing/timestamping.
- The `HWRM_*` command numbers are the glue between high-level driver operations and firmware dispatch. Mismatched numbers or stale generated headers can cause firmware to parse a request as a different operation.
- The backing-store layouts integrate tightly with DMA mapping and page table/page directory construction in the driver. Page size, PBL level, entry size, and split-entry counts must match firmware capabilities.
- Port PHY/MAC structures are consumed by link-mode translation code. The extended speed masks and signal-mode fields need mapping to Linux ethtool link mode bits and advertised/supported/autoneg state.

## Risks and Sharp Edges

- Generated-file drift is the primary risk. Manual edits, stale firmware schemas, or partial regeneration can silently break ABI layouts.
- Structure size and field ordering are contract-critical. Compiler padding assumptions, missing packing controls elsewhere, or changing typedef widths would corrupt the on-wire/DMA ABI.
- Bitmask families repeat similar names across request, response, qcfg, cfg, v1, and v2 structures. Accidentally using a response mask with a request field, or a v1 backing-store type with a v2 field, can compile but produce wrong firmware behavior.
- `enables` and `flags` have different semantics. Some flags are mutually exclusive enable/disable pairs; others request tests, capability modes, or reset behavior. Setting conflicting bits can trigger command-specific errors.
- Statistics structs are large DMA-visible layouts. Size mismatches between the host buffer and firmware-reported `tx_stat_size`/`rx_stat_size` can truncate counters or expose stale memory.
- Async event overlays all share the same 16-byte base shape. Dispatch must key off `event_id` and sometimes error subtype before interpreting `event_data1`/`event_data2`.
- Error recovery and doorbell pacing register descriptors encode address space in low bits and address in upper bits. Callers must mask/shift correctly before MMIO/config/GRC access.
- Newer high-speed PHY fields use multiple generations of masks (`support_speeds`, PAM4 masks, `support_speeds2`, `support_speeds2_ext`). Link-mode code that only reads legacy masks will under-report 200G/400G/800G and PAM4 variants.
- The chunk ends in the middle of `rx_port_stats_ext`; the complete per-file merge must include the next chunk before making final claims about the full extended RX stat block.

## Test Signals

- Compile-time checks should validate struct sizes against the generated comments for representative records: common headers, `hwrm_ver_get_output`, async completions, `hwrm_func_cfg_input`, backing-store configs, PHY qcfg, and port stats.
- HWRM transport tests should verify every request initializes the common header fields, response DMA address, sequence ID, and valid byte handling, and that timeout sizing respects `hwrm_ver_get_output`.
- Capability-gating tests should simulate `hwrm_ver_get_output`, `hwrm_func_qcaps_output`, and `hwrm_func_qcfg_output` combinations for short command required/supported, backing-store v2 required, PTP, KTLS/QUIC, doorbell pacing, error recovery, and high-speed PHY capabilities.
- Async event tests should feed representative 16-byte completions for link change, reset notify, error recovery, deferred response, echo request, PHC/PPS timestamp, and HWRM error, then assert the driver dispatches to the expected recovery/link/PTP paths.
- Resource setup tests should compare requested VF/function resources against qcaps min/max fields and assert command-specific errors from `hwrm_func_cfg_cmd_err` are surfaced.
- Backing-store tests should verify page-size/PBL-level encoding, v2 type iteration, split-entry counts, and qcfg readback for each allocated context type.
- Port tests should cover speed/FEC/autoneg translation for legacy speeds and extended PAM4 200G/400G/800G masks, plus MAC timestamp capture and PTP register capability flags.
- Stats tests should validate host buffer lengths, clear/counter-mask flags, little-endian counter conversion, and partial availability of extended stat blocks across chunk boundaries.
