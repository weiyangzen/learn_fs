# Research: subset-b-003933

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hw_v2.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hw_v2.c

## Purpose

`hns_roce_hw_v2.c` is the hardware-version provider for Huawei/HiSilicon HNS RoCE v2/v3 devices in the Linux RDMA stack. It binds the generic `hns_roce_dev` core to HNAE3 NIC-client lifecycle callbacks, programs RoCE hardware contexts through CMQ/mailbox commands, implements the `ib_device_ops` fast paths for QP/CQ/SRQ work, and handles reset, interrupts, completion queues, memory translation, GID/MAC configuration, bonding, and HIP08/HIP09 generation differences.

The file is not a standalone filesystem component, but in this source tree it is part of a Ceph-client distributed-filesystem kernel snapshot. Its relevance is as an RDMA transport provider that upper storage/networking code can use indirectly through RDMA core APIs.

## Important APIs, Types, and Functions

- Provider registration:
  - `hns_roce_hw_v2_init()` initializes debugfs and registers `hns_roce_hw_v2_client` with HNAE3.
  - `hns_roce_hw_v2_exit()` unregisters the HNAE3 client, releases bond groups, and cleans debugfs.
  - `hns_roce_hw_v2_ops` exposes `.init_instance`, `.uninit_instance`, `.link_status_change`, and `.reset_notify` to HNAE3.
  - `hns_roce_hw_v2` is the hardware-operation vtable used by the common HNS RoCE core.
  - `hns_roce_v2_dev_ops` and `hns_roce_v2_dev_srq_ops` expose RDMA core operations: post send/recv, poll CQ, modify/query QP/CQ/SRQ, drain queues, and destroy QPs.
- Work queue entry construction:
  - `to_hr_opcode()` maps RDMA core send opcodes to HNS v2 WQE opcodes.
  - `set_data_seg_v2()`, `set_extend_sge()`, `fill_ext_sge_inl_data()`, and `set_rwqe_data_seg()` build WQE data segments, including inline and extended-SGE payloads.
  - `set_rc_wqe()` builds RC send WQEs for send, RDMA read/write, atomics, send-with-invalidate, and fast-reg MR.
  - `set_ud_wqe()` builds UD send WQEs and address-vector fields.
  - `hns_roce_v2_post_send()`, `hns_roce_v2_post_recv()`, and `hns_roce_v2_post_srq_recv()` are the RDMA-core posting entry points.
- Doorbells and direct WQEs:
  - `update_sq_db()`, `update_rq_db()`, `update_srq_db()`, `update_cq_db()`, and `update_eq_db()` write hardware doorbells or record-doorbell memory.
  - `hns_roce_write64()` is defined in the header and used throughout; it suppresses MMIO when the device is in reset or doorbells are disabled.
  - `write_dwqe()` and `hns_roce_write512()` implement the direct-WQE fast path for single send WQEs.
- CMQ and mailbox command path:
  - `hns_roce_v2_cmq_init()` and `hns_roce_v2_cmq_exit()` allocate/free the command submission queue.
  - `hns_roce_cmq_setup_basic_desc()`, `__hns_roce_cmq_send_one()`, `__hns_roce_cmq_send()`, and `hns_roce_cmq_send()` submit CMQ descriptors and translate firmware return codes.
  - `v2_post_mbox()` and `v2_poll_mbox_done()` implement mailbox command posting and completion polling on top of CMQ.
  - Reset-aware helpers `v2_chk_mbox_is_avail()`, `check_aedev_reset_status()`, and `check_device_is_in_reset()` avoid issuing commands while HNAE3 reset is active.
- Capability/profile/init flow:
  - `hns_roce_v2_profile()` queries hardware and firmware versions, then calls PF or VF profile setup.
  - `hns_roce_query_caps()`, `load_func_res_caps()`, `load_pf_timer_res_caps()`, `apply_func_caps()`, and `set_hem_page_size()` populate `hr_dev->caps`.
  - `hns_roce_v2_pf_profile()` configures global parameters, VF switch behavior, capabilities, resource partitions, BA table attributes, and context entry sizes.
  - `hns_roce_v2_vf_profile()` performs the reduced VF capability/resource setup.
  - `hns_roce_v2_init()` performs hardware runtime initialization, including HIP08 free-MR resources, clearing extended doorbell lists, HEM table allocation, and PF link-table setup.
  - `hns_roce_v2_exit()` performs the reverse cleanup and function clear.
- HEM/context programming:
  - `hns_roce_v2_set_bt()`, `hns_roce_v2_set_hem()`, and `hns_roce_v2_clear_hem()` configure or clear HEM base-address tables.
  - `hns_roce_v2_write_mtpt()`, `hns_roce_v2_rereg_write_mtpt()`, and `hns_roce_v2_frmr_write_mtpt()` fill memory protection table entries.
  - `hns_roce_v2_write_cqc()` fills completion queue contexts.
  - `hns_roce_v2_write_srqc()` and `hns_roce_v2_write_srqc_index_queue()` fill SRQ contexts.
- QP lifecycle:
  - `hns_roce_v2_modify_qp()` is the central QP state/configuration update path.
  - `modify_qp_reset_to_init()`, `modify_qp_init_to_rtr()`, and `modify_qp_rtr_to_rts()` fill transition-specific QPC fields.
  - `hns_roce_v2_query_qp()` reads hardware QPC state back into `ib_qp_attr`.
  - `hns_roce_v2_destroy_qp()` stops flush work, releases DIP congestion references, removes the QP from tracking, cleans CQs, and destroys resources.
  - `hns_roce_v2_qp_flow_control_init()` clears/query SCC context for HIP08 flow-control support.
- CQ/completion handling:
  - `hns_roce_v2_poll_cq()` polls hardware CQEs until reset state requires software completions.
  - `hns_roce_v2_poll_one()` maps CQE ownership/status/opcode into `ib_wc`.
  - `get_cqe_status()`, `fill_send_wc()`, and `fill_recv_wc()` translate hardware completion status and opcode to RDMA core semantics.
  - `hns_roce_v2_req_notify_cq()` arms CQs or reports software missed events after reset.
  - `hns_roce_v2_cq_clean()` removes CQEs associated with a destroyed/reset QP and frees SRQ WQEs when needed.
- Interrupt and EQ handling:
  - `hns_roce_v2_init_eq_table()` allocates EQ contexts, workqueues, and IRQs.
  - `hns_roce_v2_cleanup_eq_table()` disables interrupts and tears down EQs.
  - `hns_roce_v2_aeq_int()` consumes asynchronous EQEs, dispatches QP/SRQ/CQ/command events, and queues work.
  - `hns_roce_ceq_work()` consumes completion EQEs and notifies CQs.
  - `hns_roce_v2_msix_interrupt_abn()` handles abnormal interrupts, including AEQ overflow reset requests and HIP09 ECC recovery work.
- GID/MAC/congestion/bond integration:
  - `hns_roce_v2_set_gid()` programs SGID or HIP09 GMV entries depending on revision.
  - `hns_roce_v2_set_mac()` programs SMAC entries.
  - `fill_cong_field()`, `get_dip_ctx_idx()`, and `put_dip_ctx_idx()` manage congestion-control mode and DIP context indices.
  - `hns_roce_cmd_bond()`, `hns_roce_bond_init_client()`, and `hns_roce_bond_uninit_client()` integrate with the HNS RoCE bond layer.

## Control Flow

Initialization starts in the HNAE3 client `.init_instance` callback. `hns_roce_hw_v2_init_instance()` marks the instance as initializing, rejects work during HNAE3 reset, matches the PCI ID, skips unsupported HIP08 VF cases, then calls `__hns_roce_hw_v2_init_instance()`. That allocates an RDMA device object, allocates v2 private state, pulls HNAE3 configuration into `hr_dev` with `hns_roce_hw_v2_get_cfg()`, and delegates to common `hns_roce_init()`. The common core then calls this file's hardware vtable methods: CMQ init, profile discovery, hardware init, EQ init, and context writers.

The profile sequence is command-driven. `hns_roce_v2_profile()` queries hardware version and firmware version, records IDs, then dispatches to PF or VF flow. PF flow queries function count, configures global UDP/timer parameters, allows VF switching/loopback policy, queries capability descriptors, queries PF resource slices and timer resources, applies generation-specific defaults, allocates VF resources, programs BA table attributes, and configures entry sizes on HIP09+. VF flow queries capabilities and its allocated resources, applies defaults, then programs BA table attributes.

Posting a send WR enters `hns_roce_v2_post_send()`. Under the SQ lock it checks QP and device state, verifies SQ space and SGE count, computes the WQE index and owner bit, stores `wr_id`, clears shared WQE header bits, then builds either RC or UD WQE content. RC setup maps opcodes, fills RDMA/atomic/MR fields, handles inline data and extended SGEs, and writes owner bit only after the rest of the WQE and SGEs are visible. UD setup fills qkey, remote QPN, address-vector, PD, and extended SGEs. On success the SQ head and next SGE index advance; a single eligible WQE can use direct-WQE MMIO, otherwise the SQ doorbell is updated.

Posting receives is similar but uses the RQ or SRQ lock. `hns_roce_v2_post_recv()` validates device/QP state, checks RQ space and SGE limits, writes RQ WQE SGEs, records `wr_id`, advances the RQ head, and updates an RQ doorbell or record DB. `hns_roce_v2_post_srq_recv()` additionally allocates a free SRQ WQE index from a bitmap, fills the SRQ WQE, writes the index queue entry, stores `wr_id`, advances the SRQ index head, and updates the SRQ doorbell/record DB.

Polling a CQ enters `hns_roce_v2_poll_cq()` under the CQ lock. If the device state is `UNINIT`, polling switches to software completions for queued WRs. Otherwise `hns_roce_v2_poll_one()` checks the CQE owner bit, advances `cons_index`, resolves the QP, consumes SQ/RQ/SRQ tail state, fills send or receive `ib_wc` fields, maps the CQE status, and flushes the QP on most non-success/non-flush errors. Polled CQEs cause a CQ consumer-index doorbell update.

QP state changes use a context/mask protocol. `hns_roce_v2_modify_qp()` allocates a QPC context and an all-ones mask, fills transition-specific absolute fields, optionally marks SQ/RQ producer indices for flush on transition to ERR, fills optional fields from `attr_mask`, always writes `QPC_QP_ST`, then sends the context/mask through `HNS_ROCE_CMD_MODIFY_QPC`. Reset-to-init initializes PD, WQ sizes, CQ numbers, SRQ flags, record DB addresses, owner-mode flags, and stash. Init-to-RTR configures RQ buffers, retry-resource tables, path attributes, MAC/GID/VLAN/UDP source port, congestion fields, MTU, ACK request frequency, and receive-side state. RTR-to-RTS configures SQ/SGE buffer addresses and clears retry/head fields.

Reset control flows are split between command gating and HNAE3 notifications. All CMQ/mailbox users pass through `v2_chk_mbox_is_avail()` or related checks, which update `hr_dev->dis_db` and `hr_dev->is_reset` and return busy or success according to HNAE3 reset counters/state. HNAE3 reset callbacks mark the RoCE device down, disassociate user mmap regions, disable doorbells, uninitialize the instance, then reinitialize it when requested. Function clear and free-MR logic contain extra reset-aware fallbacks so cleanup does not hang against a resetting device.

Interrupt handling is two-tiered. MSI-X EQ interrupts call `hns_roce_v2_msix_interrupt_eq()`. CEQ interrupts queue bottom-half work to poll CEQEs and notify CQs. AEQ interrupts poll up to `HNS_AEQ_POLLING_BUDGET`, perform immediate command or flush side effects for some event types, queue work for normal event dispatch, increment counters, and update the EQ doorbell. The abnormal interrupt path handles AEQ overflow by requesting HNAE3 reset, and on HIP09+ treats a no-status abnormal interrupt as an ECC recovery signal.

## State and Persistence Behavior

All persistent state is in kernel memory, DMA-coherent command/context buffers, HEM/MTR allocations, and hardware context tables; this file does not write disk state.

Important in-memory state includes:

- `hr_dev->caps`: populated from firmware capability descriptors and post-processed for HIP08/HIP09 differences.
- `hr_dev->state`, `hr_dev->active`, `hr_dev->dis_db`, `hr_dev->is_reset`, and `hr_dev->reset_cnt`: drive reset safety and command/doorbell suppression.
- `hns_roce_v2_priv`: holds the HNAE3 handle, CMQ ring, extended link table, and HIP08 free-MR helper resources.
- QP SQ/RQ producer/consumer state: `head`, `tail`, `wrid[]`, `next_sge`, state, SL, access flags, response depth, DIP reference, and free-MR marker.
- SRQ bitmap/index-queue state: allocated WQE bitmap, head/tail counters, WQE `wrid[]`, and optional record DB.
- CQ state: `cons_index`, armed state, CQE size, completion lists, record DB address, and associated QP lists.
- EQ state: EQN, entries, EQE size, consumer index, arm/coalesce settings, IRQ vector, and work item.
- HEM/MTR tables: base address pages for QPC, CQC, MPT, SRQC, SCCC, GMV, timer resources, EQE, CQE, and WQE buffers.
- XArray DIP context tracking for HIP09 congestion mode, with `qp_cnt` reference counts and `dgid` keys.

Hardware persistence is through mailbox/CMQ commands that program contexts and base-address tables. Reinitialization after HNAE3 reset rebuilds the RDMA device and hardware state rather than relying on durable on-disk persistence. User mappings are explicitly disassociated on reset down.

## Dependencies and Integration Points

- Linux kernel infrastructure: PCI, DMA coherent memory, MMIO, spinlocks, mutexes, xarray, workqueues, IRQs, completions, bitmaps, `read_poll_timeout`, and atomic counters.
- RDMA core: `ib_device_ops`, `ib_qp`, `ib_cq`, `ib_srq`, `ib_wc`, `ib_send_wr`, `ib_recv_wr`, GID attributes, AH helpers, uverbs user context, mmap disassociation, and IB/RoCE constants.
- HNAE3 NIC framework: `hnae3_handle`, `hnae3_client`, reset notifications, vector allocation, netdev, DSCP-priority lookup, hardware reset state, and reset event requests.
- HNS RoCE common modules: device/core definitions, command mailbox helpers, HEM/MTR allocation, QP/CQ/SRQ common lifecycle helpers, tracepoints, debugfs, and bond helpers.
- Ethernet/IP helpers: MAC address handling, VLAN extraction, RoCE UDP source-port calculation, IPv4-mapped IPv6 GID detection, and netdev link-state dispatch.
- Hardware ABI from `hns_roce_hw_v2.h`: all bitfield names, context layouts, command opcodes, WQE/CQE/EQE layouts, and generation constants used here.

## Risks and Edge Cases

- The WQE/CQE/QPC context bitfields are hardware contracts. Incorrect field location, endian conversion, or generation-specific size selection can corrupt hardware state.
- Owner-bit ordering is critical. Send WQE paths use `dma_wmb()` when owner-mode DB is enabled; moving owner writes earlier can let hardware fetch partially initialized WQEs.
- Reset gating is subtle. Missing a `dis_db`/reset check before CMQ, mailbox, or doorbell traffic can hang or fault during HNAE3 reset. Overly broad suppression can silently drop legitimate commands.
- HIP08 and HIP09 paths diverge in QPC/CQE/EQE sizes, GMV vs SGID/SMAC tables, timeout scaling, free-MR behavior, VLAN bits, SCCC handling, and VF support. Regression risk is high when changing shared helpers.
- The CMQ ring is single-CSQ and spinlock protected. Timeout recovery resets the producer head to hardware CI; incorrect error handling can desynchronize command descriptors.
- The inline-data copy path uses pointer arithmetic across user-provided SGEs and page-aligned extended SGE buffers. Bounds are checked by total inline length, but off-by-one or zero-length cases are high-risk.
- CQ cleanup rewrites CQEs while preserving owner bits. Bugs here can lose completions, double-consume SRQ WQEs, or expose stale CQEs.
- Software completion mode after `UNINIT` depends on QP queue head/tail state being consistent when reset/uninit happens.
- DIP congestion context references are xarray-backed and manually reference counted. Missing `put_dip_ctx_idx()` on destruction can leak DIP slots or retain stale DGiDs.
- Abnormal interrupt handling requests reset on AEQ overflow. Changes must avoid interrupt storms and must keep interrupt mask re-enable semantics correct.
- Free-MR helper QPs are internal RDMA objects with manually set `ib_*` fields and use counts. They are necessary for HIP08 MR cleanup and are sensitive to normal object lifecycle assumptions.

## Test Signals

- Build coverage with `CONFIG_INFINIBAND_HNS` and both HIP08/HIP09-relevant compile paths enabled where possible.
- RDMA verbs smoke tests on HNS hardware: create/destroy PD/CQ/QP/SRQ/MR, transition QPs RESET->INIT->RTR->RTS, post RC send/recv, RDMA read/write, atomics, UD send, inline sends, and FRMR registration on HIP09+.
- CQ behavior tests: signaled and unsignaled sends, solicited notifications, missed-event reporting, CQ moderation changes, CQ cleanup after QP destroy, and software flush completions during reset/uninit.
- SRQ tests: post/consume SRQ receives, limit changes, XRC SRQ contexts, bitmap reuse, and SRQ last/limit events.
- Reset tests: HNAE3 down/uninit/init reset notifications during active traffic, mmap disassociation, command suppression, reinitialization, and direct-return path when instance is not initialized.
- Capability/profile tests across PF/VF and HIP08/HIP09: verify resource counts, entry sizes, GMV/SGID table programming, link-table setup, and unsupported HIP08 VF skip.
- Error injection: CMQ timeout/retval mapping, mailbox busy/timeout, AEQ overflow, ECC recovery, CQE error status mapping, and HEM allocation failure unwind.
- Bonding/link tests: RoCE bond init/uninit, active-port change, clear/set bond commands, and link-down port-state dispatch only when not masked by bond semantics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hw_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hw_v2.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_hw_v2.h -->
