# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_roce_hsi.h lines 1-5906

## Purpose

This chunk is the generated hardware/software interface for the Broadcom `bng_re` RoCE driver. It defines the little-endian command queue, completion/event queue, doorbell, work queue, receive queue, completion queue, statistics, congestion-control, and notification record layouts that the kernel driver shares with firmware and device DMA rings. There is no executable control flow in this header; the operational behavior comes from other `bng_re` files that allocate these records, fill fields, post them to hardware, and decode returned completions.

The file is guarded by `_BNG_RE_HSI_H_`, carries a GPL-2.0 SPDX tag, includes `<linux/bnge/hsi.h>`, and warns that it is automatically generated. That generated status is important: local hand edits are high risk because every struct offset, size comment, enum value, and mask is part of a firmware ABI.

## Major ABI Families

### Doorbells and Command Queue Base

The first records define producer/consumer notifications:

- `struct tx_doorbell`, `rx_doorbell`, `cmpl_doorbell`, and `status_doorbell` are 32-bit MMIO doorbell payloads with a 24-bit index and a 4-bit key. Completion doorbells add valid and mask bits.
- `struct cmdq_init` describes command queue bootstrap state: command queue PBL address, queue level/size, CREQ ring id, and producer index.
- `struct cmdq_base` is the common 16-byte prefix for firmware commands. It carries `opcode`, `cmd_size`, `flags`, `cookie`, `resp_size`, and `resp_addr`.
- `struct creq_base` is the common 16-byte event/completion prefix with type, valid bit, and event code.

The opcode list in `cmdq_base` is the top-level firmware command namespace. It spans normal RDMA resource commands (`CREATE_QP`, `MODIFY_QP`, `CREATE_CQ`, `REGISTER_MR`, `ADD_GID`), function management (`INITIALIZE_FW`, `QUERY_FUNC`, `SET_FUNC_RESOURCES`), RoCE stats/congestion-control commands, link aggregation, mirror/global RoCE configuration, and PNO/path/tunnel opcodes.

### Firmware and Function Management

The firmware lifecycle ABI is represented by:

- `cmdq_query_version` / `creq_query_version_resp` for firmware and interface version discovery.
- `cmdq_initialize_fw` / `creq_initialize_fw_resp` for initial device setup. This is one of the largest early commands and supplies page-directory addresses for QPC, MRW, SRQ, CQ, TQM, and TIM contexts, resource counts, per-VF limits, stat context id, driver HSI version, and driver build version. Capability/behavior flags include MRAV split reservation, hardware requester retransmission, driver version reporting, optimized modify QP, L2 VF resource management, destroy context sideband support, UDCC session-data sideband support, and mirror-on-RoCE support.
- `cmdq_deinitialize_fw` / `creq_deinitialize_fw_resp` for teardown.
- `cmdq_query_func`, `creq_query_func_resp`, and `creq_query_func_resp_sb` for function capabilities and limits. The sideband includes maximum QP/CQ/MR/MW/SRQ/AH/PKEY/GID/DPI values, SGE and inline-data limits, TQM allocation requirements, supported congestion-control generation, CQE V2, optimized transmit, ping-pong push, hardware requester/responder retransmission, link aggregation, batch QP create/destroy, stats-ext context support, DCN support, PBL page size support, default RoCE CC params, rate limit range, and PNO/path capabilities.
- `cmdq_set_func_resources` / `creq_set_func_resources_resp`, `cmdq_read_context` / `creq_read_context`, and `cmdq_map_tc_to_cos` / `creq_map_tc_to_cos_resp` for allocation policy, debug/context readback, and traffic-class mapping.

### QP, SRQ, CQ, MRW, GID, QP1, and AH Commands

The resource command records follow a consistent request/response pattern with a `cmdq_*` request and a `creq_*_resp` response:

- QP operations: `cmdq_create_qp`, `cmdq_destroy_qp`, `cmdq_modify_qp`, `cmdq_query_qp`, and `cmdq_query_qp_extend`.
- SRQ operations: `cmdq_create_srq`, `cmdq_destroy_srq`, `cmdq_query_srq`.
- CQ operations: `cmdq_create_cq`, `cmdq_destroy_cq`, `cmdq_resize_cq`.
- MR/MW operations: `cmdq_allocate_mrw`, `cmdq_deallocate_key`, `cmdq_register_mr`, `cmdq_deregister_mr`.
- GID operations: `cmdq_add_gid`, `cmdq_delete_gid`, `cmdq_modify_gid`, `cmdq_query_gid`.
- Special queue-pair/address-handle operations: `cmdq_create_qp1`, `cmdq_destroy_qp1`, `cmdq_create_ah`, `cmdq_destroy_ah`.

Important QP fields include QP type (`RC`, `UD`, raw ethertype, `GSI`), SQ/RQ page size and page-level encoding, DPI, SQ/RQ sizes, SGE/FWO encodings, CQ/SRQ/PD ids, SQ/RQ PBL pointers, IRRQ/ORRQ addresses and sizes, steering tag, ext stats context id, scheduler queue id, eRoCE class/group/csig bits, and flags for SRQ use, force completion, reserved lkey, FR PMR, variable WQE, optimized transmit, UD responder CQE-with-CFA, express mode, read/atomic use, and explicit PBL page-size validity.

`cmdq_modify_qp` is the key QP state transition/configuration ABI. Its `modify_mask` gates fields for QP state, SQD async notify, access flags, P_Key/Q_Key, DGID/SGID, RoCE version, flow label, hop limit, traffic class, source/destination MAC, path MTU, timeout/retry/RNR retry, PSNs, RD atomic limits, queue sizes, SGE limits, inline data, destination QP id, VLAN, congestion control enablement, TOS ECN/DSCP, IRRQ/ORRQ addresses, ext stats context, scheduler queue, UDP source port, and rate limit. The QP states are RESET, INIT, RTR, RTS, SQD, SQE, and ERR.

The memory registration commands expose classic RDMA access bits: local write, remote read, remote write, remote atomic, memory window bind, and zero-based addressing. Page-size encodings appear in multiple forms: compact page-size enums for queue PBLs, log2 page sizes for MR PBLs, and very large page-size ranges in fast-register WQEs.

### RoCE Statistics and Congestion Control

The header defines both immediate query responses and persistent stats DMA-context records:

- `struct roce_stats_ext_ctx` is a 240-byte DMA stats context with transmit/receive RoCE packet, byte, CNP, ECN, retransmit, error, and ACK counters.
- `cmdq_query_roce_stats` and `creq_query_roce_stats_resp_sb` expose a broad error/stat counter block including retransmits, NAKs, local/remote errors, resource errors, invalid keys/domains/ranges, SRQ/CQ load errors, PCI errors, out-of-sequence drops, active QP counts, and SQ/RQ overflow errors.
- `cmdq_query_roce_stats_ext`, `creq_query_roce_stats_ext_resp_sb`, `cmdq_allocate_roce_stats_ext_ctx`, `cmdq_deallocate_roce_stats_ext_ctx`, `cmdq_query_roce_stats_ext_v2`, and `creq_query_roce_stats_ext_v2_resp_sb` support extended and per-context stats, including timestamp validity and offsets in the V2 sideband.

Congestion-control ABI is extensive:

- `cmdq_query_roce_cc`, `creq_query_roce_cc_resp_sb`, and TLV sidebands report base CC state such as enablement, ECN/DSCP, `g`, phase counts, initial/current rates, VLAN PCP, mode, queue, RTT, TCP CP, inactivity threshold, packets/time per phase.
- Generation-specific TLVs (`creq_query_roce_cc_gen1_resp_sb_tlv`, `creq_query_roce_cc_gen2_resp_sb_tlv`, and ext variants) cover gen1 rate/threshold/quota/rate-table parameters and gen2 DCN queue-level thresholds/actions.
- `cmdq_modify_roce_cc`, `cmdq_modify_roce_cc_tlv`, and the gen1/gen2/ext modify TLVs carry matching `modify_mask` fields so callers can alter only selected CC parameters.

The TLV records share a small header of `cmd_discr`, `tlv_flags`, `tlv_type`, and `length`; some also include `total_size`. `tlv_flags` encode whether more TLVs follow and whether the TLV is required.

### Link Aggregation and Global RoCE Configuration

`cmdq_set_link_aggr_mode_cc` configures aggregation enablement, active/member port maps, aggregation mode (`active-active`, `active-backup`, `balance-xor`, `802.3ad`), and per-port stat context ids. `cmdq_roce_mirror_cfg` controls mirror enablement. `cmdq_roce_cfg` controls feature bits such as ICRC check disable and forced mirror enable, with `creq_roce_cfg_resp` returning current feature state.

### CREQ Event Records

`creq_func_event` and `creq_qp_event` are generic event wrappers. Function events cover TX/RX WQE/data errors, CQ/TQM/CFC/TIM errors, VF communication requests, and resource exhaustion. QP events mirror the command opcode namespace and add asynchronous `QP_ERROR_NOTIFICATION` and `CQ_ERROR_NOTIFICATION`.

`creq_qp_error_notification` is the detailed async QP fault record. It separates requester and responder slow-path state/reason and includes many requester causes, including opcode error, timeout/retry limit, RNR timeout, NAK arrival, memory errors, illegal bind/fast-register/invalidate, completion/WQE/ORRQ format errors, invalid AV/domain, CQ load, service type, PCI errors, producer WQE mismatch, PSN range, retransmission setup, and SQ overflow. Responder reasons include excessive payload, opcode/PSN/key/domain/permission/range errors, IRRQ overflow/format, unsupported opcode, unaligned atomic, remote invalidate, SRQ/CQ load, PCI errors, PSN not found, and RQ overflow. `creq_cq_error_notification` reports CQ invalid, overflow, and load errors from requester/responder paths.

### Send Queue, Receive Queue, and Retransmission Records

The SQ WQE area begins with `sq_base`, which enumerates legacy and V3 WQE types:

- Legacy send-like WQEs: `sq_send`, `sq_send_hdr`, `sq_send_raweth_qp1`, `sq_send_raweth_qp1_hdr`.
- Legacy RDMA and atomic WQEs: `sq_rdma`, `sq_rdma_hdr`, `sq_atomic`, `sq_atomic_hdr`.
- Legacy key-management WQEs: `sq_localinvalidate`, `sq_fr_pmr`, `sq_bind` and their header-only variants.
- V3 WQEs: `sq_send_v3`, `sq_rawqp1send_v3`, `sq_udsend_v3`, `sq_rdma_v3`, `sq_atomic_v3`, `sq_localinvalidate_v3`, `sq_fr_pmr_v3`, `sq_bind_v3`, and `sq_change_udpsrcport_v3`, again with header variants where appropriate.

Common SQ flags include signal completion, RD/atomic fence, UC fence, solicited event, inline payload, WQE timestamp enable, and debug trace. Legacy full WQEs are often 128 bytes with payload/SGE space in `data[]`; header forms are 16, 32, or 40 bytes. V3 WQEs add an `opaque` field, compact `wqe_size`, and explicit inline-length fields for send/RDMA/UD/raw paths.

`sq_sge` defines one SGE as address, lkey, and size. `sq_psn_search`, `sq_psn_search_ext`, `sq_msn_search`, and `sq_msn_search_v3` are retransmission/search helper records that encode PSNs, MSNs, start indices, WQE size, signal state, and opaque values.

RQ receive descriptors are represented by `rq_wqe`, `rq_wqe_hdr`, `rq_wqe_v3`, and `rq_wqe_hdr_v3`. Legacy RQ descriptors carry a 20-bit WR id and 24 words of data; V3 carries `opaque` and a much larger 512-byte full descriptor with 124 data words.

### Completion Queue Records Through Line 5906

The chunk includes the base CQE family and most legacy/V2 completions:

- `cq_base` identifies CQE type through `cqe_type_toggle` and carries a status and `opaque`.
- `cq_req` is requester completion with QP handle, SQ consumer index, push bit, and request status.
- `cq_res_rc` is RC responder completion with length, immediate or invalidate key, QP/MR handles, SRQ/RQ source, immediate/invalidate/RDMA flags, and RQ/SRQ WR id.
- `cq_res_ud` and `cq_res_ud_v2` are UD responder completions with length, immediate data, QP handle, source MAC/QP, RoCE IP version, meta format, optional VLAN/TPID metadata, and SRQ/RQ WR id. V2 repacks CFA metadata and TPID selection.
- `cq_res_ud_cfa` and `cq_res_ud_cfa_v2` are UD responder completions carrying CFA code/qid and CFA metadata.
- `cq_res_raweth_qp1` and the beginning of `cq_res_raweth_qp1_v2` cover raw Ethernet QP1 completions. They report packet length, packet classification (`IP`, `TCP`, `UDP`, `FCoE`, `RoCE`, `ICMP`, PTP), checksum and tunnel/packet parse errors, CFA metadata, checksum-calculation flags, payload offset, QP handle, status, SRQ/RQ selection, and WR id.

Although the requested chunk ends at line 5906 in the middle of `cq_res_raweth_qp1_v2`, the surrounding file continues with terminal/cutoff CQEs, V3 CQEs, notification queue records, XRRQ IRRQ/ORRQ records, and PTU page-table entries. Those later layouts are part of the same generated ABI and will matter to any merged per-file analysis.

## Control Flow and State Behavior

This header does not perform control flow directly. The implied flow is:

1. The driver initializes RCFW command infrastructure with `cmdq_init` and posts `cmdq_initialize_fw`.
2. The driver queries firmware/interface/function capabilities, then uses returned limits and feature flags to decide which command variants, WQE formats, CQE formats, stats contexts, and CC TLVs it may use.
3. Resource requests are written into DMA-visible command queue entries. Each request sets an opcode, command/response sizes, cookie, response DMA address, and resource-specific fields.
4. Firmware completes requests by writing CREQ records. The driver uses the type, valid bit, event/opcode, cookie, and status to match the completion to an outstanding command.
5. Data-path queue state progresses through SQ/RQ doorbell indices, WQE producer/consumer indices, CQ toggle bits, and CQ status/type fields.
6. Asynchronous errors are reported via CREQ/NQ records rather than synchronous command responses.

Persistent state is external to this header but represented by its layouts: firmware context pages (`qpc_page_dir`, `mrw_page_dir`, `srq_page_dir`, `cq_page_dir`, `tqm_page_dir`, `tim_page_dir`), queue PBLs, MR PBLs, SQ/RQ/CQ/SRQ CIDs, QP XIDs, GID indices, stat context ids, extended stats DMA memory, PSN/MSN tracking tables, and doorbell/CQ toggle state. All multi-byte fields use Linux little-endian types, so callers must use the normal `cpu_to_le*`/`le*_to_cpu` discipline.

## Dependencies and Integration Points

Primary local integrations found in the driver tree:

- `bng_fw.h` uses `struct cmdq_base`, `struct creq_base`, and `struct creq_qp_event` in RCFW message/cookie helpers. Inline helpers prepare command headers and compute command slots.
- `bng_fw.c` includes this header, processes `creq_base` events, dispatches `creq_qp_event` and `creq_func_event`, posts `cmdq_init`, and issues initialize/deinitialize firmware commands.
- `bng_sp.c` builds `cmdq_query_version` and `cmdq_query_func`, then decodes `creq_query_version_resp`, `creq_query_func_resp`, and `creq_query_func_resp_sb`.
- `bng_res.h` and `bng_res.c` include this header for resource setup, sizing, and HSI constants.
- `bng_tlv.h` includes this header and wraps access to `cmdq_base` fields for both plain and TLV-encapsulated commands.

External dependencies are kernel integer/endian types (`u8`, `__le16`, `__le32`, `__le64`) and Broadcom network HSI definitions from `<linux/bnge/hsi.h>`. The records are consumed by firmware and hardware rings, so the real ABI dependency is firmware version compatibility rather than only C compilation.

## Risks and Sharp Edges

- Struct layout drift is the largest risk. This file is generated and comments declare exact bit/byte sizes; adding fields, reordering fields, changing types, or compiling under unexpected packing assumptions can break firmware communication.
- Masks and shifts encode many subfields inside little-endian integers. Callers must apply masks after endian conversion on reads and before conversion on writes, and must not mix host-endian bit operations with already-converted values casually.
- `cmd_size`/`resp_size` and sideband `size` fields must match the actual command/response variant, especially for TLV commands and extended query responses.
- Feature gating is mandatory. Capabilities from `creq_query_func_resp_sb` determine whether V3 WQEs, CQE V2/V3 layouts, optimized modify QP, hardware retransmission modes, stats-ext contexts, PBL page-size options, rate limiting, and PNO/path features are legal.
- Some command namespaces advertise opcodes for PNO/path/tunnel operations, but this chunk does not define matching request structures for every advertised opcode. Callers must not assume an opcode in `cmdq_base` means this header chunk contains a complete command payload layout.
- Several similarly named layouts differ subtly across legacy, V2, and V3 variants. Examples include UD/CFA CQ metadata packing, raw QP1 checksum flags, request status numeric values, and V3 `opaque` handling.
- The requested line range cuts through `cq_res_raweth_qp1_v2`; using only this chunk as a standalone ABI reference would miss the rest of that struct and later CQ/NQ/PTU layouts.
- Queue/toggle handling is easy to get wrong. CQEs and NQEs use valid/toggle bits to distinguish fresh entries from old ring contents, while doorbells use index/key encodings.
- Access-control fields for MR/MW/QP and fast-register WQEs are security-sensitive. A bad mask or stale key can expose memory, reject valid operations, or cause remote access faults.

## Test and Validation Signals

Useful validation signals for code using this header:

- Build-time checks that generated struct sizes match the size comments for command, CREQ, WQE, RQ, and CQE layouts. Static assertions would catch accidental ABI drift.
- Firmware init smoke test: `cmdq_initialize_fw` completes with `CREQ_QP_EVENT_STATUS_SUCCESS`, then `cmdq_query_version` and `cmdq_query_func` return expected firmware/interface versions and sane resource limits.
- Resource lifecycle tests: create/modify/query/destroy QP; create/query/destroy SRQ; create/resize/destroy CQ; allocate/register/deregister/deallocate MRW; add/query/modify/delete GID; create/destroy AH and QP1.
- Data-path tests per WQE/CQE family: send, send-with-immediate, send-with-invalidate, RDMA write/read, atomics, local invalidate, fast register PMR, bind MW, raw QP1, UD send, and V3 variants where capability flags allow them.
- Error-path tests that force malformed WQEs, protection faults, invalid keys, CQ overflow, retry exhaustion, RNR retry exhaustion, and CQ load errors, then verify CREQ/CQE status and async notification decoding.
- Stats tests that compare queried RoCE counters and extended stats DMA contexts against expected packet/error activity, including CNP/ECN and retransmission counters.
- Congestion-control tests that query and modify base/gen1/gen2 TLVs only when advertised and verify unchanged fields remain stable when modify masks omit them.
- Endianness and bitfield tests on representative masks: doorbell index/key, QP state/network type, VLAN/TPID, path MTU, CQE type/toggle, PSN/MSN fields, and PTE/PDE page/valid bits.
