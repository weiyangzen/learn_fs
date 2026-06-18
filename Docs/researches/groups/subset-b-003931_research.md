# Research Group: subset-b-003931

This grouped report covers the hfi1 InfiniBand/OPA verbs, user SDMA, expected receive, UC/UD transport, and tracepoint files listed for subset `subset-b-003931`. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_tid.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_tid.h

## Purpose
`trace_tid.h` defines the Linux tracepoint surface for hfi1 TID and TID RDMA behavior. It is observability-only code: it does not drive packet handling, but it captures expected receive TID registration/unregistration/invalidation, OPFN negotiation, TID RDMA flow/request state, responder and sender queue state, receive errors, SGE alignment checks, write responder/sender state, TID ACKs, and KDETH eflags errors. It is included through the kernel `TRACE_EVENT` mechanism and finishes with `TRACE_INCLUDE_FILE trace_tid`.

## Important APIs, Types, and Events
The file declares helper decoders `hfi1_trace_get_tid_ctrl()`, `hfi1_trace_get_tid_len()`, and `hfi1_trace_get_tid_idx()` for compact TID entry fields. Important event classes include `hfi1_exp_tid_reg_unreg`, `hfi1_opfn_state_template`, `hfi1_opfn_data_template`, `hfi1_opfn_param_template`, `hfi1_msg_template`, `hfi1_tid_flow_template`, `hfi1_tid_node_template`, `hfi1_tid_entry_template`, `hfi1_responder_info_template`, `hfi1_sender_info_template`, `hfi1_tid_rdma_request_template`, `hfi1_rc_rcv_err_template`, `hfi1_sge_template`, `hfi1_tid_write_rsp_template`, `hfi1_tid_write_sender_template`, `hfi1_tid_ack_template`, and `hfi1_kdeth_eflags_error_template`. Concrete events are named by lifecycle points such as `hfi1_exp_tid_reg`, `hfi1_exp_tid_unreg`, `hfi1_exp_tid_inval`, `hfi1_tid_flow_alloc`, `hfi1_tid_req_rcv_write_data`, `hfi1_tid_write_sender_retry_timeout`, and `hfi1_eflags_err_write`.

## Control Flow
Tracepoint control flow is declarative. Call sites in expected receive and TID RDMA code pass QP, flow, request, node, SGE, or scalar state into the trace macros. The trace classes use `TP_fast_assign` to snapshot state from `struct rvt_qp`, `struct hfi1_qp_priv`, `struct tid_rdma_flow`, and `struct tid_rdma_request`, then format stable strings via shared `*_PRN` macros. The event family is organized so one template covers several state-machine transitions, which makes probe output comparable across allocation, build, receive, retry, timeout, and ACK paths.

## State, Persistence, and Dependencies
The file persists no runtime state of its own. It snapshots live state from QP private fields such as `s_tid_cur`, `r_tid_head`, `flow_state.generation`, `sync_pt`, retry flags, ACK queues, TID offsets, and page-set counts. Dependencies include `linux/tracepoint.h`, `linux/trace_seq.h`, `hfi.h`, and structures from `tid_rdma.h` and `verbs.h` that are reachable through `hfi.h`. The trace helpers are an integration contract: changing TID field encodings or QP private structures must keep these events compiling and meaningful.

## Integration Points
Expected receive code uses `hfi1_exp_tid_reg`, `hfi1_exp_tid_unreg`, `hfi1_put_tid`, and `hfi1_exp_tid_inval`. TID RDMA sender/responder implementation uses the request, flow, responder, sender, write, ACK, and eflags events to diagnose protocol progress. OPFN negotiation code uses the OPFN state/data/param/message events. Debug and performance investigations rely on these event names and field order, so they are part of the driver's diagnostic ABI even though they are not userspace uAPI.

## Risks and Test Signals
Risks are compile-time drift from structure layout changes, dereferencing trace arguments that are invalid at call time, and misleading diagnostics if fields are sampled before or after state updates. Test signals include successful kernel tracepoint compilation, `trace-cmd`/ftrace visibility for the `hfi1_tid` system, expected events during user expected receive setup/clear/invalidation, TID RDMA read/write traffic showing monotonic flow/request progress, and error injection producing receive-error or eflags traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_tid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_tx.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_tx.h

## Purpose
`trace_tx.h` defines tracepoints for hfi1 transmit-side behavior: PIO buffer availability, QP sleep/wakeup, SDMA descriptor/engine progress, user SDMA request lifecycle, AHG updates, buffer-control-table programming, verbs send completion, send-loop activity, and accelerated IPoIB transmit queues. Like `trace_tid.h`, it is observability infrastructure rather than packet logic.

## Important APIs, Types, and Events
The file declares `parse_sdma_flags()` and `print_u32_array()` formatting helpers. Major trace families include `hfi1_piofree`, `hfi1_wantpiointr`, `hfi1_qpwakeup`, `hfi1_qpsleep`, `hfi1_sdma_descriptor`, `hfi1_sdma_engine_select`, `hfi1_sdma_user_free_queues`, `hfi1_sdma_user_process_request`, `hfi1_sdma_user_reqinfo`, `hfi1_sdma_user_header`, `hfi1_sdma_user_completion`, `hfi1_usdma_defer`, `hfi1_usdma_activate`, `hfi1_usdma_we`, `hfi1_sdma_user_header_ahg`, `hfi1_sdma_state`, `bct_set`, `bct_get`, `hfi1_qp_send_completion`, `hfi1_rc_do_send`, `hfi1_rc_do_tid_send`, and many `hfi1_txq_*`/`hfi1_tx_*` IPoIB queue events.

## Control Flow
Callers trace queue transitions and descriptor construction at specific TX lifecycle points. User SDMA call sites emit request metadata, data length, computed packet lengths, TID offsets, header templates, AHG descriptor arrays, waits, activations, and final completion states. SDMA engine code emits descriptor words, status, sequence numbers, and queue head/tail positions. PIO and verbs code trace QP waits, wakeups, and completions.

## State, Persistence, and Dependencies
The header stores no runtime data. It snapshots fields from `struct send_context`, `struct sdma_engine`, `struct hfi1_user_sdma_pkt_q`, `struct hfi1_pkt_header`, `struct buffer_control`, `struct rvt_qp`, `struct rvt_swqe`, `struct hfi1_ipoib_txq`, and `struct ipoib_txreq`. It depends on `hfi.h`, `mad.h`, `sdma.h`, `ipoib.h`, and `user_sdma.h`. The conditional `CONFIG_HFI1_DEBUG_SDMA_ORDER` path adds sequence-number detail for ordering investigations.

## Integration Points
`user_sdma.c` relies heavily on this file for `hfi1_sdma_user_*` and `hfi1_usdma_*` events. `verbs.c` and `verbs_txreq.c` use QP sleep/wakeup and completion traces. SDMA core code traces descriptor and progress state. IPoIB transmit code uses the queue and ring events to debug netdev stop/wake behavior and descriptor pressure.

## Risks and Test Signals
Risks include tracepoint format drift, copying too many AHG elements into the fixed trace array if callers pass an unexpected length, and diagnostic ambiguity when events are emitted before memory barriers or state publication. Test signals include compile coverage with and without `CONFIG_HFI1_DEBUG_SDMA_ORDER`, ftrace visibility for `hfi1_tx`, SDMA stress producing defer/activate/completion transitions, PIO pressure producing `hfi1_qpsleep`/`hfi1_qpwakeup`, and IPoIB traffic producing ring head/tail progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/uc.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/uc.c

## Purpose
`uc.c` implements Unreliable Connected transport packet construction and receive processing for hfi1. It handles UC SEND and RDMA WRITE work requests, segments them by PMTU, advances QP send state, builds 9B or 16B RUC headers through shared verbs helpers, and processes incoming UC packets without ACK/retry semantics.

## Important APIs and Functions
The exported entry points are `hfi1_make_uc_req(struct rvt_qp *, struct hfi1_pkt_state *)` and `hfi1_uc_rcv(struct hfi1_packet *)`. `hfi1_make_uc_req()` consumes SQ WQEs, handles local invalidation/registration completions, chooses UC opcodes (`UC_OP(SEND_FIRST)`, `SEND_MIDDLE`, `RDMA_WRITE_ONLY_WITH_IMMEDIATE`, etc.), sets immediate data or RETH fields, initializes `ps->s_txreq`, and calls `hfi1_make_ruc_header()`. `hfi1_uc_rcv()` validates headers with `hfi1_ruc_check_hdr()`, handles ECN, checks PSN sequencing with `cmp_psn()`, copies SEND payload into receive WQEs, performs RDMA WRITE rkey checks through `rvt_rkey_ok()`, and reports receive completions through `rvt_recv_cq()`.

## Control Flow
Send flow starts by allocating a verbs tx request. If the QP cannot send but is flushing, it completes pending WQEs with `IB_WC_WR_FLUSH_ERR` when no DMA is pending. Normal flow chooses a header layout from `priv->hdr_type`, fetches the current WQE, initializes SGE cursors, then enters an opcode/state switch. First packets set base state and optional RETH/immediate headers; middle packets reuse remaining length; last packets attach immediate data and advance `s_cur`. The receive flow first drops invalid RUC headers and processes ECN, then compares incoming PSN to `qp->r_psn`. Sequence or opcode errors rewind/clear receive SGEs and drop or restart at a valid first/only opcode. Valid SEND packets consume a receive WQE and post `IB_WC_RECV`; valid RDMA WRITE packets validate access and write to the remote MR, posting `IB_WC_RECV_RDMA_WITH_IMM` only for WRITE_WITH_IMM.

## State, Persistence, and Dependencies
UC state lives in `struct rvt_qp`: `s_cur`, `s_head`, `s_last`, `s_state`, `s_psn`, `s_len`, `s_sge`, `s_wqe`, `r_psn`, `r_state`, `r_sge`, `r_rcv_len`, and `r_aflags`. hfi1-private fields provide header type, SDMA engine, send context, AHG state, and iowait status. The file depends on `hfi.h`, `verbs_txreq.h`, `qp.h`, rdmavt queue/SGL helpers, and common verbs header builders.

## Integration Points
`verbs.c` dispatches UC opcodes to `hfi1_uc_rcv()` and calls `hfi1_make_uc_req()` from the send engine. `verbs_txreq.c` supplies tx request allocation and wait-list behavior. Shared RC/UC helpers provide RUC header building and header validation. CQ completions and MR/rkey checks are delegated to rdmavt.

## Risks and Test Signals
Key risks are off-by-one PSN transitions, incorrect SGE rewind after malformed multi-packet messages, length/padding mismatch between 9B and 16B paths, flushing while DMA is pending, and accepting RDMA writes without proper remote-write permissions. Test signals include UC SEND/WRITE single and multi-packet transfers at PMTU boundaries, immediate-data completions, forced packet loss/reordering with silent drops and no retry, invalid rkey/access drops, flush behavior in error state, and ECN/CNP interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/uc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ud.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ud.c

## Purpose
`ud.c` implements Unreliable Datagram send construction, local loopback delivery, receive validation, pkey lookup, and CNP response construction for hfi1. It supports both 9B InfiniBand-style and 16B OPA-style headers, including special 16B fabric-management packets for QP0/QP1.

## Important APIs and Functions
Core send APIs are `hfi1_make_ud_req()`, `hfi1_make_ud_req_9B()`, and `hfi1_make_ud_req_16B()`. Receive and utility APIs include `hfi1_ud_rcv()`, `hfi1_lookup_pkey_idx()`, `return_cnp()`, and `return_cnp_16B()`. Internal helpers include `ud_loopback()` for same-port delivery, `hfi1_make_bth_deth()` for BTH/DETH setup, and `opa_smp_check()` for OPA SMP management packet validation.

## Control Flow
`hfi1_make_ud_req()` allocates a tx request, handles flushes, fetches the current WQE, computes the destination header type, and detects local loopback. Loopback bypasses hardware after DMA ordering checks, delivers through `ud_loopback()`, and completes the send. Non-loopback sends populate SGE state, static rate, header fields, SDMA engine, send context, and reset AHG state. The 9B builder creates LRH/BTH/DETH, optional GRH, SL/SC, permissive LID handling, and P_Key insertion. The 16B builder handles management versus regular datagram headers, OPA LIDs, optional multicast GRH, bypass padding, and 16B length-in-flits.

Receive flow extracts pkey, L4 type, permissive-LID status, source QP, and solicited state. It validates packet length, permissive LIDs, qkey, pkeys, and management-packet constraints. It then consumes or reuses an RWQE, ensures the posted buffer can hold the mandatory GRH plus payload, copies a real, synthesized, or skipped GRH, copies payload, and posts `IB_WC_RECV`.

## State, Persistence, and Dependencies
UD send state lives in QP send indices, WQE SGEs, `hfi1_qp_priv` header type/SC/SDE/send context/AHG, and port SL-to-SC mappings. Receive state uses QP receive SGEs and `RVT_R_REUSE_SGE` for oversized packets. Port state includes LID, LMC, pkeys, counters, partition enforcement, and management capability flags. Dependencies include rdmavt QP/CQ helpers, `mad.h`, `trace_ibhdrs.h`, `verbs_txreq.h`, and OPA/IB header helper functions.

## Integration Points
`verbs.c` dispatches UD opcodes to `hfi1_ud_rcv()` and calls `hfi1_make_ud_req()` for send progress. MAD/SMA behavior integrates with management QPs and `hfi1_process_mad()`. P_Key failures integrate with `hfi1_bad_pkey()` and port constraint counters. CNP return paths use PIO send contexts and congestion-processing helpers.

## Risks and Test Signals
Risks include incorrect permissive-LID handling on QP0 versus other QPs, qkey mismatches leaking packets, pkey table corner cases for full/limited management keys, 16B GRH/GID transformation errors, loopback ordering relative to pending DMA, and wrong completion metadata for GSI/SMI pkey indexes. Test signals include UD send/receive with and without immediate data, GSI/SMI MAD traffic, multicast with required GRH, loopback traffic, invalid qkey/pkey/permissive-LID drops, 16B management packets, CNP generation, and counters for `n_pkt_drops`, `n_vl15_dropped`, and `n_loop_pkts`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_exp_rcv.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_exp_rcv.c

## Purpose
`user_exp_rcv.c` manages user expected-receive TID mappings. It pins user receive pages, groups physically contiguous pages into hardware-supported TID page sets, programs hfi1 RcvArray entries, tracks each programmed entry in file-private state, reacts to MMU invalidations, returns invalidated TIDs to userspace, and clears mappings on user request or file teardown.

## Important APIs and Functions
Exported APIs are `hfi1_user_exp_rcv_init()`, `hfi1_user_exp_rcv_free()`, `hfi1_user_exp_rcv_setup()`, `hfi1_user_exp_rcv_clear()`, and `hfi1_user_exp_rcv_invalid()`. Internal helpers include `pin_rcv_pages()`, `unpin_rcv_pages()`, `find_phys_blocks()`, `program_rcvarray()`, `set_rcvarray_entry()`, `unprogram_rcvarray()`, `__clear_tid_node()`, `clear_tid_node()`, `unlock_exp_tids()`, `tid_rb_invalidate()`, `tid_cover_invalidate()`, and `cacheless_tid_rb_remove()`.

## Control Flow
Initialization allocates `entry_to_rb` for RcvArray entry-to-node lookup and, when the TID unmap capability is absent, allocates an invalid-TID ring and enables MMU notifier mode. Setup validates page alignment and nonzero length, creates a `tid_user_buf`, optionally installs a cover interval notifier, pins pages subject to memlock/cache limits, finds physically contiguous page sets, reserves the per-file TID share, and under the context expected-receive mutex programs full and partial TID groups. Each programmed entry allocates a `tid_rb_node`, DMA maps the pages, optionally installs an interval notifier for the exact pages, records the node in `entry_to_rb`, writes the hardware TID via `hfi1_put_tid()`, and adds encoded TID info to the returned list. Failures unprogram and unpin partial work.

Clear copies the user TID list, unprograms each entry under `exp_mutex`, removes interval notifiers, clears hardware, unmaps DMA, releases pages, updates group allocation state, and decrements `tid_used`. MMU invalidation immediately clears the hardware entry and queues the encoded TID into `fd->invalid_tids`, setting the per-subcontext user event bit. `hfi1_user_exp_rcv_invalid()` copies and clears that invalidation list without holding the lock during `copy_to_user()`.

## State, Persistence, and Dependencies
Persistent state is per open file/context: `fd->entry_to_rb`, `fd->invalid_tids`, `fd->invalid_tid_idx`, `fd->tid_used`, `fd->tid_limit`, `fd->tid_n_pinned`, locks, and event bits. Context state includes free/used/full `tid_group` lists, `expected_count`, `expected_base`, `exp_mutex`, and receive-entry group size. Nodes retain DMA address, page array, notifier, RcvArray entry, group pointer, and a `freed` guard. Dependencies include `mmu_interval_notifier`, DMA mapping, `user_pages.c` pin helpers, `exp_rcv.h`, `mmu_rb.h`, and TID tracepoints.

## Integration Points
The user ioctl/file layer calls setup, clear, invalid, init, and free. User SDMA expected sends consume TID values produced here and validate TID offset/length in `user_sdma.c`. Hardware receive programming uses `hfi1_put_tid()` and RcvArray group helpers. The event mechanism exposes MMU invalidations to PSM/user libraries.

## Risks and Test Signals
Risks include notifier races during setup, incorrect accounting when partially programming groups, clearing a node twice during user clear versus MMU invalidation, stale user TID values after invalidation, DMA unmap/unpin ordering, and memlock/cache-limit bypass. Test signals include partial setup under limited RcvArray resources, page unmap while TIDs are active, invalid list delivery and event-bit clearing, setup failure cleanup with no pinned-page leaks, repeated clear/free, subcontext TID-limit enforcement, and trace events for register/unregister/invalidate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_exp_rcv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_exp_rcv.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_exp_rcv.h

## Purpose
`user_exp_rcv.h` declares the data structures and public driver entry points for user expected receive support. It describes pinned user buffers, programmed TID nodes, page-set decomposition, and setup/clear/invalidation APIs used by the file/ioctl layer and user SDMA.

## Important APIs and Types
`struct tid_pageset` records a physically contiguous page run as an index and count. `struct tid_user_buf` tracks a setup request: cover interval notifier, mutex, virtual address, length, page count, page array, and flexible page-set list. `struct tid_rb_node` tracks one programmed hardware receive entry: interval notifier, filedata owner, invalidation mutex, physical address, TID group, RcvArray entry, DMA address, freed flag, page count, and flexible page array. `num_user_pages()` computes the number of pages spanned by an address/length range. Public functions are `hfi1_user_exp_rcv_init()`, `hfi1_user_exp_rcv_free()`, `hfi1_user_exp_rcv_setup()`, `hfi1_user_exp_rcv_clear()`, and `hfi1_user_exp_rcv_invalid()`. `mm_from_tid_node()` returns the notifier-owned `mm_struct`.

## Control Flow
The header is consumed by expected receive implementation and by user SDMA for shared TID concepts. A caller initializes per-file expected receive state, submits `hfi1_tid_info` mappings through setup, later clears explicit TIDs, polls invalidated TIDs, and frees all per-file mappings at close.

## State, Persistence, and Dependencies
The header itself stores no state, but its structs define the lifetime contract. `tid_user_buf` is transient during setup, while `tid_rb_node` persists for as long as a TID remains programmed. Dependencies include `hfi.h` for file/context/device types and `exp_rcv.h` for TID encoding and group definitions. MMU interval notifiers are embedded in both transient and persistent structures to detect unmap races.

## Integration Points
`user_exp_rcv.c` owns all function implementations. `user_sdma.h` includes this header because expected SDMA requests carry and validate TID entries. Filedata and context structures in `hfi.h` point to arrays and counters manipulated through these APIs.

## Risks and Test Signals
Risks are ABI-sensitive structure assumptions inside C implementation, flexible-array allocation size errors, and misuse of `num_user_pages()` with zero length or overflowed address ranges. Test signals include compiling with flexible-array bounds checks, setup/clear/invalidation API coverage, and expected SDMA requests using TID lists produced by setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_exp_rcv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_pages.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_pages.c

## Purpose
`user_pages.c` centralizes long-term user page pinning policy for hfi1 send/receive caches. It enforces RLIMIT_MEMLOCK and a driver cache-size module parameter, pins pages with long-term GUP, updates `mm->pinned_vm`, and releases pages with dirty tracking.

## Important APIs and Functions
`hfi1_can_pin_pages(struct hfi1_devdata *, struct mm_struct *, u32 nlocked, u32 npages)` decides whether a cache may pin additional pages. `hfi1_acquire_user_pages(struct mm_struct *, unsigned long vaddr, size_t npages, bool writable, struct page **pages)` calls `pin_user_pages_fast()` with `FOLL_LONGTERM` and optional `FOLL_WRITE`, then increments `pinned_vm` by the actual pin count. `hfi1_release_user_pages(struct mm_struct *, struct page **, size_t npages, bool dirty)` calls `unpin_user_pages_dirty_lock()` and decrements `pinned_vm` when an `mm` is available. The `cache_size` module parameter defaults to 256 MB.

## Control Flow
Expected receive or SDMA cache code first calls `hfi1_can_pin_pages()` with its current locked-page count. Non-`CAP_IPC_LOCK` callers must fit both the process RLIMIT and a per-user-context quarter-RLIMIT share. All callers must fit the driver cache-size cap. If allowed, pages are pinned and accounted. Release reverses pinning and accounting; close paths may pass `mm == NULL` after signal teardown.

## State, Persistence, and Dependencies
State is global module parameter `cache_size` and per-mm `pinned_vm`; callers retain their own `nlocked` counters. Dependencies are Linux mm, capabilities, rlimits, and long-term GUP APIs. The policy assumes one process per context and one cache per context, as noted by comments.

## Integration Points
`user_exp_rcv.c` calls these functions when programming expected receive TIDs. User SDMA pinning code also uses the same policy through pinning helpers. Correct accounting is essential for MMU notifier cleanup and memory pressure behavior.

## Risks and Test Signals
Risks include partial GUP success requiring caller cleanup, mismatch between actual pinned count and requested count, stale `nlocked` accounting in callers, RLIMIT division by user-context count assumptions, and long-term pins on memory types that GUP rejects. Test signals include memlock-limit failures, CAP_IPC_LOCK bypass, cache-size-limit failures, partial pin cleanup, dirty release on receive buffers, and no `pinned_vm` leak after process exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_sdma.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_sdma.c

## Purpose
`user_sdma.c` implements the userspace SDMA submission path. It allocates per-file packet and completion queues, validates user-provided packet templates and iovecs, constructs one or more SDMA tx requests, handles expected-receive TID offsets, uses AHG when available, submits descriptors to SDMA engines, and publishes completion-ring status.

## Important APIs and Functions
Public APIs are `hfi1_user_sdma_alloc_queues()`, `hfi1_user_sdma_free_queues()`, and `hfi1_user_sdma_process_request()`. Core internal functions are `defer_packet_queue()`, `activate_packet_queue()`, `flush_pq_iowait()`, `user_sdma_send_pkts()`, `compute_data_length()`, `user_sdma_txadd_ahg()`, `check_header_template()`, `set_pkt_bth_psn()`, `set_txreq_header()`, `set_txreq_header_ahg()`, `user_sdma_txreq_cb()`, `user_sdma_free_request()`, and `set_comp_state()`. Engine selection uses `dlid_to_selector()` and `sdma_select_user_engine()`.

## Control Flow
Queue allocation builds a packet queue, request array, in-use bitmap, txreq slab cache, completion queue mapped with `vmalloc_user()`, and system-pinning handler, then publishes `fd->pq` under RCU. Request processing copies `sdma_req_info`, validates completion index, iovec count, fragment size, opcode, SC/VL consistency, P_Key, no-GRH template constraint, and expected-request TID vector requirements. It claims a completion slot, initializes `struct user_sdma_request`, copies data iovecs and optional TID array, selects an SDMA engine, optionally allocates AHG, marks the completion `QUEUED`, then loops until all packets are submitted. `user_sdma_send_pkts()` allocates txreqs, computes per-packet lengths, updates header fields or AHG descriptors, pins/maps user pages through SDMA packet helpers, queues txreqs, and calls `sdma_send_txlist()`. If the engine is busy, the queue is deferred to `sde->dmawait` and the caller waits for activation. Completion callback frees txreqs, marks errors, frees request resources at the final sequence, and publishes `COMPLETE` or `ERROR`.

## State, Persistence, and Dependencies
Persistent per-file state includes `hfi1_user_sdma_pkt_q`, `hfi1_user_sdma_comp_q`, request array, bitmap, txreq slab, iowait state, MMU RB handler, pinned-page counts, and completion ring entries. Per-request state includes copied header template, SDMA info, SDE pointer, TID list, data length, iov progress, sequence counters, AHG index, KDETH offsets, and error flag. Dependencies include SDMA core, iowait, mmu_rb, pinning, expected receive TID definitions, rdmavt headers, and TX tracepoints.

## Integration Points
The file/device ioctl path passes user iovecs into `hfi1_user_sdma_process_request()`. Expected receive setup supplies TID values validated here. SDMA engine code owns descriptor submission and callbacks. Completion queues are consumed by userspace. Queue teardown synchronizes with SRCU to stop new requests, drains iowait, waits for active request count to reach zero, and frees pinning resources.

## Risks and Test Signals
Risks include trusting malformed user templates, completion-slot reuse races, AHG descriptor overflow, expected TID offset crossing errors, busy-engine waits timing out and needing wait-list cleanup, freeing queues while callbacks are outstanding, memory ordering for completion status/errcode, and mismatched SC/VL/P_Key validation. Test signals include invalid opcode/GRH/SC/VL/P_Key rejection, expected and eager SDMA multi-packet sends, AHG and non-AHG paths, engine busy deferral and activation, completion-ring state transitions, request abort/error callback paths, queue teardown under outstanding requests, and page-pinning leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_sdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_sdma.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_sdma.h

## Purpose
`user_sdma.h` defines the constants, helpers, queue structures, request structures, and public APIs for hfi1 userspace SDMA. It is the shared contract between `user_sdma.c`, pinning/MMU helpers, expected receive support, and tracepoints.

## Important APIs and Types
Key constants are `MAX_VECTORS_PER_REQ`, `MAX_PKTS_PER_QUEUE`, `BTH_SEQ_MASK`, AHG KDETH descriptor positions, PBC/LRH conversion macros, `TXREQ_FLAGS_REQ_ACK`, `TXREQ_FLAGS_REQ_DISABLE_SH`, and `SDMA_IOWAIT_TIMEOUT`. Helpers include `num_pages()`, request control field decoders `req_opcode()`, `req_version()`, `req_iovcnt()`, and `ahg_header_set()`. `struct hfi1_user_sdma_pkt_q` owns request slots, in-use bitmap, txreq cache, iowait, waitqueue, MMU handler, and lock accounting. `struct hfi1_user_sdma_comp_q` describes the completion ring. `struct user_sdma_request` is the main in-flight request record. `struct user_sdma_txreq` wraps a packet header, SDMA txreq, list node, request pointer, flags, and sequence number.

## Control Flow
Userspace SDMA lifecycle is queue allocation, repeated request processing, completion polling, and queue free. Requests copy user metadata into `user_sdma_request`, generate one or more `user_sdma_txreq` packets, submit via SDMA, and update the completion ring from callbacks.

## State, Persistence, and Dependencies
The header defines state ownership boundaries but stores no data itself. Queue state persists for the open file/context; request and txreq state lasts until callbacks complete or error cleanup runs. Dependencies include Linux device/wait APIs and local `common.h`, `iowait.h`, `user_exp_rcv.h`, `mmu_rb.h`, `pinning.h`, and `sdma.h`.

## Integration Points
`user_sdma.c` implements the declared APIs. Tracepoints include this header to inspect queue and request fields. Expected receive types are included because expected SDMA requests carry TID vectors and KDETH offsets. Pinning/MMU helpers manage user pages referenced by request iovecs.

## Risks and Test Signals
Risks include macro field masks drifting from uAPI definitions, request/txreq cacheline-sharing assumptions, fixed AHG array sizing, completion-ring size limits, and incorrect use of queue state outside SRCU protection. Test signals include structure compile coverage, max-vector rejection, AHG descriptor bounds checks, completion-ring wrap/reuse tests, and queue free while requests are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_sdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs.c

## Purpose
`verbs.c` is the hfi1 verbs integration hub. It registers the device with rdmavt/IB core, advertises device and port capabilities, dispatches incoming packets by opcode and QP, builds TX descriptors for PIO or SDMA, handles pkey enforcement, manages send wait lists for memory/PIO pressure, and exposes hardware statistics and device operations.

## Important APIs and Functions
Exports include `hfi1_kdeth_eager_rcv()`, `hfi1_kdeth_expected_rcv()`, `hfi1_ib_rcv()`, `hfi1_16B_rcv()`, `hfi1_wait_kmem()`, `hfi1_verbs_send_dma()`, `hfi1_verbs_send_pio()`, `egress_pkey_check()`, `hfi1_verbs_send()`, `ah_to_sc()`, `hfi1_get_npkeys()`, `hfi1_register_ib_device()`, `hfi1_unregister_ib_device()`, and `hfi1_cnp_rcv()`. Important internal pieces are opcode tables, header-length tables, `qp_ok()`, `tid_qp_ok()`, `hfi1_handle_packet()`, `verbs_sdma_complete()`, `wait_kmem()`, `build_verbs_ulp_payload()`, `build_verbs_tx_desc()`, `update_hcrc()`, `pio_wait()`, `verbs_pio_complete()`, `get_send_routine()`, device/port query helpers, AH validation/update, stats allocation, and registration of rdmavt driver function callbacks.

## Control Flow
RX flow enters through 9B, 16B, or KDETH-specific receive functions. The code traces the header, increments opcode stats, looks up QPs under RCU, checks QP state/opcode compatibility, applies pkey checks for bypass packets, locks the QP receive side, and calls the registered opcode handler (`hfi1_rc_rcv`, `hfi1_uc_rcv`, `hfi1_ud_rcv`, TID RDMA handlers, or `hfi1_cnp_rcv`). Multicast delivery iterates attached QPs. TX flow enters `hfi1_verbs_send()`, extracts pkey/opcode from 9B or 16B headers, chooses PIO or DMA based on device capability, QP type, packet size, opcode, and pending iowait, enforces egress pkeys, and invokes the selected send routine. DMA builds SDMA descriptors and submits them; PIO allocates a PIO buffer and copies header/payload directly, queueing the QP if resources are unavailable. Registration initializes ports, timers, locks, txreq cache, IB device fields, rdmavt parameters/callbacks, ports, sysfs, and stats.

## State, Persistence, and Dependencies
Persistent state includes module parameters for resource limits and copy policy, global system image GUID, opcode/stat tables, `hfi1_ibdev` wait lists/timers/txreq cache, per-port SL/SC mappings, rdmavt device parameters, and cached stats descriptors. Runtime QP state is shared with rdmavt and hfi1 private QP fields. Dependencies include `hfi.h`, `device.h`, `qp.h`, `verbs_txreq.h`, `debugfs.h`, `fault.h`, `affinity.h`, `ipoib.h`, rdmavt, IB MAD/user verbs, and OPA address helpers.

## Integration Points
This file binds hfi1 to the RDMA core via `ib_device_ops` and `rvt_register_device()`. It connects transport-specific files (`rc.c`, `uc.c`, `ud.c`, TID RDMA code) to RX dispatch and send construction. It uses SDMA/PIO hardware helpers, pkey enforcement, congestion processing, MAD processing, IPoIB parameters, sysfs/debugfs, and QP lifecycle callbacks from `qp.c`.

## Risks and Test Signals
Risks include opcode table drift, pkey enforcement inconsistencies between 9B/16B/user/kernel paths, incorrect PIO-vs-SDMA choice under resource pressure, wait-list leaks, missed QP refcount wakeups, descriptor build rollback bugs, registration cleanup leaks, stats descriptor global lifetime issues with multiple devices, and CNP handling for unsupported QP types. Test signals include device register/unregister cycles, RC/UC/UD/TID traffic dispatch, multicast delivery, PIO buffer exhaustion and wakeup, SDMA descriptor build failures, pkey violation counters/completions, fault injection, hardware stats queries, AH validation, port shutdown, and CNP/BECN processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs.h

## Purpose
`verbs.h` is the central hfi1 verbs header. It defines OPA/IB header wrappers, QP-private state, packet send state, opcode stats, port/device verbs structures, PSN helpers, TID RDMA accessors, and prototypes shared by RC/UC/UD/TID, QP, MAD, send, receive, and registration code.

## Important APIs and Types
Key types include `struct opa_16b_mgmt`, `struct hfi1_16b_header`, `struct hfi1_opa_header`, `struct hfi1_ahg_info`, `struct hfi1_sdma_header`, `struct hfi1_qp_priv`, `struct hfi1_swqe_priv`, `struct hfi1_ack_priv`, `struct hfi1_pkt_state`, `struct hfi1_opcode_stats`, `struct hfi1_opcode_stats_perctx`, `struct hfi1_ibport`, and `struct hfi1_ibdev`. Important inline helpers are `inc_opstats()`, `to_idev()`, `iowait_to_qp()`, `cmp_psn()`, `mask_psn()`, `delta_psn()`, `wqe_to_tid_req()`, `ack_to_tid_req()`, `__full_flow_psn()`, `full_flow_psn()`, `opa_bth_is_migration()`, and `hfi1_trdma_send_complete()`. It declares all major transport and registration APIs used across the hfi1 verbs subsystem.

## Control Flow
The header supports flow rather than implementing it. Send code fills `hfi1_pkt_state`, transport builders populate `verbs_txreq`/headers, `hfi1_verbs_send()` chooses egress, and completion paths call back into RC/TID helpers. Receive code decodes headers into `hfi1_packet` and dispatches to declared handlers. QP private fields hold send-context, SDMA, iowait, TID RDMA, OPFN, flow, retry, and pending-resource state used across those flows.

## State, Persistence, and Dependencies
`hfi1_qp_priv` is the largest persistent state definition in this subset, including AHG, SDMA engine, send context, receive context, TID timers/lists, OPFN data, TID RDMA parameters, flow state, retry/NACK flags, send/receive TID queues, counters, and read/write segment accounting. `hfi1_ibdev` stores rdmavt device info, wait-list locks, txreq cache, timers, counters, and optional debugfs/fault state. Dependencies include Linux lock/work/timer/slab headers, RDMA core/rdmavt headers, `iowait.h`, `tid_rdma.h`, and `opfn.h`.

## Integration Points
All researched C files include or depend on this header directly or indirectly. `verbs.c` implements many prototypes and uses the structures for registration and TX/RX dispatch. `uc.c`/`ud.c` use PSN/header helpers and `hfi1_pkt_state`. `verbs_txreq.c` uses `hfi1_ibdev`, `hfi1_qp_priv`, and `iowait_to_qp()`. Trace headers inspect these structures for diagnostics.

## Risks and Test Signals
Risks include cross-file ABI drift, cacheline-sensitive structure changes, PSN helper changes breaking wraparound comparisons, TID RDMA state misinterpretation, duplicate or stale prototypes, and changing `HFI1_UVERBS_ABI_VERSION` requirements when userspace ABI changes. Test signals include full driver compile, sparse/lockdep on QP/iowait usage, RC/UC/UD/TID traffic, PSN wrap tests, QP reset/error paths, registration/unregistration, and tracepoint compilation after structure edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs_txreq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs_txreq.c

## Purpose
`verbs_txreq.c` manages the slab cache and lifecycle of `struct verbs_txreq` objects used by verbs send paths. It allocates txreqs, handles low-memory/resource waits by queueing QPs on `dev->txwait`, cleans SDMA state and MR references on release, and wakes a waiting QP when a txreq becomes available.

## Important APIs and Functions
`hfi1_put_txreq(struct verbs_txreq *tx)` releases a tx request, drops an attached MR with `rvt_put_mr()`, cleans SDMA descriptor state with `sdma_txclean()`, frees the slab object, then wakes one QP from the txwait list. `__get_txreq(struct hfi1_ibdev *dev, struct rvt_qp *qp)` allocates from `dev->verbs_txreq_cache` while `qp->s_lock` is held; on failure it marks the QP `RVT_S_WAIT_TX`, queues its `s_iowait`, traces sleep, and takes a QP reference. `verbs_txreq_init()` creates a per-device slab cache named by unit. `verbs_txreq_exit()` destroys it.

## Control Flow
Send builders call `get_txreq()`/`__get_txreq()` before constructing a packet. If allocation succeeds, normal send logic owns the txreq until PIO completion or SDMA callback calls `hfi1_put_txreq()`. If allocation fails and the QP is in a receive-capable state, the QP is placed on `dev->txwait`, marked not busy, and later woken by `hfi1_put_txreq()` after another txreq is freed. The wait list is protected by `txwait_lock` seqlock and QP references are held until wakeup.

## State, Persistence, and Dependencies
Persistent state is the per-device `verbs_txreq_cache`, `txwait` list, `txwait_lock`, and `n_txwait` counter in `struct hfi1_ibdev`. Per-QP state includes `RVT_S_WAIT_TX`, `RVT_S_BUSY`, private `s_iowait`, and QP refcount. Dependencies include `hfi.h`, `verbs_txreq.h`, `qp.h`, `trace.h`, rdmavt MR/QP helpers, and SDMA cleanup.

## Integration Points
`uc.c`, `ud.c`, RC send code, and `verbs.c` consume txreqs for packet construction and send. `hfi1_put_txreq()` is called from PIO send completion/error paths and SDMA callbacks. QP wakeups integrate with `hfi1_qp_wakeup()` and tracepoint `hfi1_qpsleep`.

## Risks and Test Signals
Risks include wait-list corruption under seqlock misuse, missed wakeups, leaking QP references when queued, freeing txreqs with live SDMA descriptors, MR reference leaks, and destroying the cache while txreqs remain. Test signals include forced slab allocation failure, high-concurrency send pressure, txwait list drain on release, QP state transitions around `RVT_S_WAIT_TX`, SDMA cleanup after aborted sends, and unregister checks that wait lists are empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs_txreq.c -->
