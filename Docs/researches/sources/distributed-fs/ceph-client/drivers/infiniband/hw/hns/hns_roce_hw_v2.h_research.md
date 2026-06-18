# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hw_v2.h

## Purpose

`hns_roce_hw_v2.h` is the hardware ABI and private-definition header for `hns_roce_hw_v2.c`. It defines HNS RoCE v2/v3 constants, CMQ opcodes, command descriptor formats, hardware context structures, bitfield location macros, WQE/CQE/EQE-related layouts, private driver state, and the small public symbols exported between the v2 hardware implementation, bonding code, and common HNS RoCE code.

The header is the authoritative map from driver state to hardware register/mailbox/context fields. Most implementation functions in `hns_roce_hw_v2.c` are short sequences of `hr_reg_write()`/`hr_reg_read()` using macros defined here.

## Important APIs, Types, and Definitions

- Generation and sizing constants:
  - HNS RoCE v2/v3 context and entry sizes such as `HNS_ROCE_V2_MTT_ENTRY_SZ`, `HNS_ROCE_V3_SCCC_SZ`, `HNS_ROCE_V3_GMV_ENTRY_SZ`, `HNS_ROCE_V2_QPC_TIMER_ENTRY_SZ`, and `HNS_ROCE_V2_CQC_TIMER_ENTRY_SZ`.
  - Hop-number constants for QPC, SCCC, MTT, CQE, SRQWQE, PBL, IDX, SQWQE, extended SGE, RQWQE, and EQE tables.
  - Page-size support and base-address page-size constants, including 16K and 256K encodings.
  - Reset, command timeout, interrupt-vector, table chunk, free-MR, and EQ depth defaults.
- Command queue ABI:
  - `enum hns_roce_opcode_type` enumerates CMQ opcodes for firmware/version queries, global parameter config, PF/VF resources, SGID/SMAC/GMV tables, mailbox posting/status, BA-table attributes, function clear, SCCC commands, ECC queries, bond commands, and switch configuration.
  - `struct hns_roce_cmq_desc`, `struct hns_roce_cmq_req`, `struct hns_roce_v2_cmq_ring`, and `struct hns_roce_v2_cmq` describe command descriptors and the command submission queue.
  - `enum hns_roce_cmd_return_status` and `struct hns_roce_cmd_errcode` provide firmware return-code categories consumed by the implementation.
  - `HNS_ROCE_CMD_FLAG_*` macros define CMQ descriptor flags, including input, output/read, chained descriptor, write/read direction, and error interrupt.
- Capability and resource response layouts:
  - `struct hns_roce_query_version`, `struct hns_roce_query_fw_info`, and query PF caps structs A through F define CMQ response payloads.
  - `PF_CAPS_*`, `FUNC_RES_*`, and `PF_TIMER_RES_*` bitfield macros identify capability/resource fields inside CMQ payload words.
  - `struct hns_roce_congestion_algorithm` captures the selected congestion algorithm fields written into extended QPC context.
- Hardware context layouts:
  - `struct hns_roce_v2_cq_context` plus `CQC_*` macros define CQC fields: CQ state, arm state, CEQ, CQE size, hop/page sizes, base addresses, producer/consumer indices, record DB address, and moderation.
  - `struct hns_roce_srq_context` plus `SRQC_*` macros define SRQC fields: SRQ state/type, PD/XRCD/CQN, WQE and index queue base tables, hop/page sizes, DB record, producer/consumer indices, and limits.
  - `struct hns_roce_v2_qp_context` and `struct hns_roce_v2_qp_context_ex` plus the extensive `QPC_*` and `QPCEX_*` macros define QPC fields for transport type, WQE/SGE addresses, PD, queue shifts, GMV/GID, path attributes, MAC/GID/VLAN/UDP, error bits, retry state, RQ/SQ state, access flags, congestion, tokens, PSNs, timers, and extended HIP09 fields.
  - `struct hns_roce_v2_scc_context` represents SCCC flow-control context.
  - `struct hns_roce_eq_context` plus `EQC_*` macros define EQ context state, EQE base addresses, producer/consumer indices, coalescing, arm state, EQE size, and MSI index.
- Work/completion descriptor layouts:
  - `enum` groups define HNS v2 WQE opcodes, receive opcodes, doorbell command types, and CQE status values.
  - `struct hns_roce_v2_ud_send_wqe`, `struct hns_roce_v2_rc_send_wqe`, `struct hns_roce_wqe_frmr_seg`, `struct hns_roce_v2_wqe_data_seg`, and `struct hns_roce_wqe_atomic_seg` define WQE payload layouts.
  - `UD_SEND_WQE_*`, `RC_SEND_WQE_*`, and `FRMR_*` macros define WQE bitfields.
  - `struct hns_roce_v2_cqe` and `CQE_*` macros define completion fields: opcode, owner, status, WQE index, QPNs, byte count, immediate/rkey, SL, port, VLAN, GRH, and network header type.
- Memory protection table:
  - `struct hns_roce_v2_mpt_entry` plus `MPT_*` and legacy `V2_MPT_*` masks describe MPT state, PD/access flags, key, VA/length, PBL base, direct PA slots, persistence, and page sizes.
- Doorbells and EQ doorbells:
  - `struct hns_roce_v2_db` plus `DB_*` and `EQ_DB_*` macros describe 64-bit doorbell payloads for SQ/RQ/SRQ/CQ/CQ notify and EQ updates.
  - `hns_roce_write64()` wraps common 64-bit doorbell MMIO with reset/doorbell-disable checks.
- Table/config command payloads:
  - `struct hns_roce_func_clear`, `struct hns_roce_vf_switch`, `struct hns_roce_post_mbox`, `struct hns_roce_mbox_status`, `struct hns_roce_cfg_sgid_tb`, `struct hns_roce_cfg_smac_tb`, `struct hns_roce_cfg_gmv_tb_a`, `struct hns_roce_cfg_gmv_tb_b`, `struct hns_roce_sccc_clr`, `struct hns_roce_sccc_clr_done`, and `struct hns_roce_bond_info`.
  - Associated field macros define function clear done, LLM table config, global UDP/time config, BA-table attributes, entry size config, GMV base table config, ECC query fields, SGID/SMAC/GMV table fields, VF switch behavior, and bond command payload.
- Private state:
  - `struct hns_roce_link_table` holds the extended LLM data/config tables.
  - `struct hns_roce_v2_free_mr` holds HIP08 reserved PD/CQ/QPs and a mutex for MR free workaround traffic.
  - `struct hns_roce_v2_priv` attaches HNAE3 handle, CMQ state, link table, and free-MR state to `hr_dev->priv`.
  - `struct hns_roce_dip` tracks DGiD-to-DIP congestion context slots.
  - `struct fmea_ram_ecc` carries ECC query results used by the recovery work item.
- Cross-file declarations:
  - `hns_roce_bond_init_client()`, `hns_roce_bond_uninit_client()`, `hns_roce_v2_destroy_qp()`, and `hns_roce_cmd_bond()` are declared for use outside the C file.

## Control Flow Supported by the Header

This header has no executable control flow beyond `hns_roce_write64()`, but it structures all control flow in the implementation:

- CMQ operations are driven by `enum hns_roce_opcode_type` and descriptor flag macros. The implementation prepares `struct hns_roce_cmq_desc`, treats `data[6]` as typed payloads, then submits through the CSQ.
- Context modification follows a context/mask protocol. The QP/CQ/SRQ modification code allocates the relevant context structure, initializes a mask to all ones, writes fields with `hr_reg_write()`, clears matching mask fields, then passes both halves to mailbox commands.
- HEM and BA programming uses hop-number and page-size constants to calculate base address tables and fill fields such as `CFG_BT_ATTR_*`, `CQC_CQE_*`, `QPC_WQE_SGE_*`, and `SRQC_*`.
- WQE posting fills `hns_roce_v2_rc_send_wqe` or `hns_roce_v2_ud_send_wqe`, optional `hns_roce_v2_wqe_data_seg`, atomic, and FRMR segments, then writes owner bits using the `*_OWNER` fields.
- CQ polling reads `hns_roce_v2_cqe` with `CQE_*` fields, maps hardware opcodes/status constants to RDMA work completions, and advances CQ doorbells using `struct hns_roce_v2_db`.
- EQ interrupt handling reads EQ contexts configured by `EQC_*` macros and updates EQ doorbells through `EQ_DB_*` fields.
- Generation-specific branches in the C file key off constants and struct sizes here, especially HIP08 vs HIP09 behavior for QPC/CQE/EQE size, GMV support, timeout scaling, free-MR workaround, and SGID/SMAC vs GMV table programming.

## State and Persistence Behavior

The header defines volatile runtime and hardware state descriptions rather than durable persistence.

- Runtime-private state persists for the lifetime of one RoCE device instance in `struct hns_roce_v2_priv`.
- CMQ descriptors and context buffers are DMA-coherent command payloads used to program hardware and read back firmware results.
- Context structs represent hardware-persistent state while the device is initialized: QPC, CQC, SRQC, MPT, SCCC, GMV, and EQC contents are programmed into hardware tables by mailbox/CMQ commands.
- Doorbell records and DB payloads are transient producer/consumer updates. The inline `hns_roce_write64()` prevents doorbell MMIO while reset is active or the driver has disabled DBs.
- Free-MR reserved resources, DIP entries, and link-table data are in-memory kernel structures that must be explicitly released on device exit/reset.

## Dependencies and Integration Points

- Includes `linux/bitops.h`, `hnae3.h`, and `hns_roce_bond.h`.
- Relies on common HNS RoCE helpers/macros from other included C-side headers, especially `FIELD_LOC`, `hr_reg_read`, `hr_reg_write`, `hns_roce_write64_k`, HEM type constants, page-shift conversions, and hardware size constants not defined in this header.
- Uses Linux endian types (`__le16`, `__le32`, `__le64`), DMA addresses, spinlocks, mutexes, Ethernet address length, PCI revision constants, and HNAE3 reset/handle operations.
- Exposes symbols that couple the hardware implementation to the bond layer and common QP destruction path.
- Mirrors firmware and hardware ABI. Any mismatch with actual device firmware descriptors or context layouts directly affects command submission and packet/completion behavior.

## Risks and Edge Cases

- Bitfield macro mistakes are high impact because most fields are written indirectly through `hr_reg_write()` using these `FIELD_LOC` definitions.
- Struct packing/layout must match firmware and hardware expectations. Adding fields, changing types, or assuming compiler padding would corrupt command/context payloads.
- Multiple constants encode hardware generation differences. Accidentally applying v3 sizes or GMV fields to HIP08 paths, or vice versa, can break initialization or traffic.
- `hns_roce_write64()` depends on `hr_dev->priv` being initialized and on a valid HNAE3 handle. It must only be used after configuration has been attached.
- Some command payload structs are overlaid onto `desc.data[6]`. They must not exceed the descriptor payload size used by the implementation.
- Free-MR constants define internal reserved queue sizes and timeout. If too small, HIP08 MR deregistration cleanup can stall or time out under load.
- `HNS_AEQ_POLLING_BUDGET` must remain smaller than AEQ depth, as noted in the comment; the implementation rejects insufficient AEQ depth.
- Hardware return-code mapping is only as complete as `enum hns_roce_cmd_return_status`; unknown codes become generic I/O errors in the implementation.
- Several macros use raw shifts for DMA addresses, such as MPT PBL and QPC retry table bases. These must stay aligned with hardware address units.

## Test Signals

- Compile-time validation is important: build with warnings enabled and ensure all context structs and bitfield macros are accepted across supported architectures.
- Runtime initialization tests should validate CMQ query responses populate `hr_dev->caps` consistently with expected field definitions.
- Hardware smoke tests should exercise every structure family defined here: QPC transitions, CQC creation/modification, SRQC creation/modification/query, MPT registration/reregistration/FRMR, DB updates, EQ creation, and SGID/SMAC/GMV programming.
- Generation coverage should include HIP08 and HIP09+ devices or emulation to confirm size constants, GMV path, timeout scaling, and EQE/CQE formats.
- Error-injection tests should validate CMQ return-code conversion, mailbox status bits, function clear done bits, ECC query fields, and abnormal interrupt masks.
- Static review should compare descriptor payload struct sizes against `struct hns_roce_cmq_desc::data` and hardware documentation.
