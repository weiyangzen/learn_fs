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
