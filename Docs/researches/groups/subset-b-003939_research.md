# subset-b-003939 Research

Grouped research for Intel IRDMA verbs, utility, and virtual-channel files under `sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma`. Each section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/utils.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/utils.c

## Purpose

`utils.c` is the IRDMA driver support layer behind the uverbs-facing code. It manages ARP/cache state from Linux networking notifications, wraps hardware register access, owns much of the Control Queue Pair (CQP) request lifecycle, issues common CQP operations for QP/CQ/SRQ/AH/stats/work-scheduler resources, handles terminate and exception-queue helpers, manages PBLE backing memory, and synthesizes flush completions when QPs are torn down.

## Important APIs, Types, and Functions

- `irdma_arp_table`, `irdma_add_arp`, `irdma_inetaddr_event`, `irdma_inet6addr_event`, `irdma_net_event`, `irdma_netdevice_event`, and `irdma_add_ip` keep the driver's software and hardware ARP/MAC/IP view synchronized with netdev, VLAN, IPv4, IPv6, and neighbor state.
- `wr32`, `rd32`, and `rd64` are direct MMIO access helpers over `struct irdma_hw`.
- `irdma_alloc_and_get_cqp_request`, `irdma_put_cqp_request`, `irdma_cleanup_pending_cqp_op`, `irdma_wait_event`, `irdma_cqp_crit_err`, and `irdma_handle_cqp_op` are the core CQP request allocator, waiter, error classifier, cleanup path, and dispatcher.
- QP/CQ/SRQ CQP wrappers include `irdma_cqp_qp_create_cmd`, `irdma_cqp_qp_destroy_cmd`, `irdma_cqp_cq_create_cmd`, `irdma_cq_wq_destroy`, `irdma_srq_wq_destroy`, `irdma_hw_modify_qp`, `irdma_cqp_qp_suspend_resume`, and `irdma_modify_qp_to_err`.
- Termination helpers `irdma_terminate_start_timer`, `irdma_terminate_done`, and `irdma_terminate_del_timer` coordinate iWARP terminate completion, timeout fallback, CM disconnect, hash removal, and QP references.
- Exception and PUDA helpers include `irdma_ieq_check_mpacrc`, `irdma_ieq_get_qp`, `irdma_send_ieq_ack`, `irdma_puda_ieq_get_ah_info`, `irdma_puda_get_tcpip_info`, `irdma_puda_create_ah`, and `irdma_puda_free_ah`.
- Stats helpers include `irdma_hw_stats_start_timer`, `irdma_hw_stats_stop_timer`, `irdma_cqp_gather_stats_gen1`, `irdma_cqp_gather_stats_cmd`, and `irdma_cqp_stats_inst_cmd`.
- PBLE helpers include `irdma_prm_add_pble_mem`, `irdma_prm_get_pbles`, `irdma_prm_return_pbles`, `irdma_map_vm_page_list`, `irdma_pble_get_paged_mem`, and `irdma_pble_free_paged_mem`.
- Completion helpers `irdma_remove_cmpls_list`, `irdma_generated_cmpls`, and `irdma_generate_flush_completions` support software-generated CQEs for flushed WQEs.

## Control Flow

Network event flow starts from kernel notifiers. Address add/change paths resolve the real VLAN parent, locate the registered IRDMA `ib_device`, update the hardware ARP cache via `irdma_manage_arp_cache` or `irdma_add_arp`, notify CM address state through `irdma_if_notify`, and dispatch `IB_EVENT_GID_CHANGE`. Neighbor updates add or delete ARP entries based on `NUD_VALID`. Initial device bring-up calls `irdma_add_ip`, which scans all relevant up netdevices under RCU and seeds IPv4 and IPv6 addresses.

CQP operations follow a common pattern. A caller gets a `struct irdma_cqp_request` from the preallocated available list or from atomic dynamic allocation, fills `cqp_request->info`, sets a scratch pointer back to the request, and calls `irdma_handle_cqp_op`. The dispatcher posts through `irdma_process_cqp_cmd`; synchronous callers then call `irdma_wait_event`, which services the CCQ, waits on the per-request waitqueue, switches to the deferred timeout threshold when a pending completion is observed, and requests a device reset on command progress timeout. Completion and reset cleanup free pending requests, wake waiters with error state, and drain both hardware ring scratch entries and software command list nodes.

Resource operations are thin command builders over that CQP substrate. QP/CQ/SRQ create and destroy functions fill operation-specific `cqp_info->in.u.*` fields. `irdma_hw_modify_qp` can wait synchronously or install a completion callback that decrements `iwqp->hw_mod_qp_pend`; on iWARP bad-close style failures it may generate an async event, send reset, or force an ERROR transition. AH, multicast-related AH, stats, CEQ/AEQ, work-scheduler, and STATS instance commands all reuse the same request mechanics.

Exception-queue flow parses received TCP/IP headers from PUDA buffers differently for generation 1 and newer hardware, finds the owning CM node/QP by the packet four-tuple, validates MPA CRCs, builds loopback AH info for partial FPDU handling, and sends duplicate/out-of-order ACKs through the CM TCP context. Terminate flow adds a temporary QP reference while a one-second timer is armed; successful or timed-out termination funnels through `irdma_terminate_done`, which marks `IRDMA_TERM_DONE`, transitions to ERROR once, and disconnects CM.

Flush completion generation is deferred until the hardware CQ is empty. `irdma_generate_flush_completions` walks SQ and RQ rings under CQ and QP locks, creates `struct irdma_cmpl_gen` entries with flushed status and original WR IDs, advances software ring tails, skips SQ NOPs, and invokes CQ completion handlers when new generated CQEs are queued. If the real CQ still has entries, it reschedules the delayed flush work.

## State and Persistence

All state is runtime kernel state. The file mutates ARP table entries and bitmaps under `rf->arp_lock`, CQP request lists under `cqp->req_lock`, resource bitmaps for QPs/CQs/SRQs/AHs/MCGs/work-scheduler nodes, QP/CQ reference counts and completion objects, QP terminate timers, delayed flush work, hardware stats timers, PBLE manager bitmaps, and generated-completion lists. Persistent external effects are limited to hardware MMIO/CQP state, DMA mappings, and RDMA core events while the driver is loaded.

## Dependencies and Integration Points

The file depends on Linux netdevice, inetaddr, inet6addr, neighbor, VLAN, RCU, timer, workqueue, DMA, vmalloc, CRC32C, and RDMA core APIs. Internally it integrates with `main.h` structures, the low-level `irdma_sc_*` hardware library, CM helpers, work-scheduler helpers, PBLE resource management, PUDA ILQ/IEQ paths, `verbs.c` object teardown and polling paths, and `virtchnl.c` for generation 3 GSI/vport cleanup.

## Risks

The highest risks are concurrency and lifetime defects. CQP requests are referenced by hardware scratch fields, software lists, waitqueues, callbacks, and reset cleanup; a missed refcount transition can leak a request or wake freed memory. QP/CQ table entries are sampled by interrupts, so refcount completion and `WRITE_ONCE`/locking discipline matters. Generated flush completions mutate work-queue rings outside normal hardware completion flow and must not race post-send/post-recv. Network notifier paths use RCU and `ib_device_get_by_netdev`; mistakes can leave stale ARP entries or dispatch GID changes for the wrong VLAN parent. PBLE page mapping error unwinds must unmap only successfully mapped pages. Timeout-driven reset requests are intentionally broad and can turn localized CQP stalls into device reset events.

## Test Signals

Useful signals include ARP add/update/delete through IPv4, IPv6, VLAN, and neighbor changes; CQP success, noncritical error, critical error, deferred completion, timeout, and reset paths; QP modify to RTS, SQD, ERROR, terminate timeout, and bad-close paths; CQ/QP/SRQ create and destroy leak checks; generated flush completions after outstanding SQ/RQ WQEs; stats timer and on-demand stats reads on gen1 and gen2+ hardware; PBLE allocation/free fragmentation tests; PUDA IEQ parsing for gen1 and newer packet layouts; and fault injection for DMA allocation, CQP request allocation, and `dma_map_page` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/verbs.c

## Purpose

`verbs.c` is the IRDMA implementation of the RDMA core `ib_device_ops` interface. It exposes device and port query operations, user context allocation and mmap, protection domains, QPs, CQs, SRQs, memory windows, memory regions including dmabuf-backed MRs, work request posting, CQ polling/arming/resizing, multicast, address handles, hardware counters, and device registration for both RoCE and iWARP modes.

## Important APIs, Types, and Functions

- Query and registration functions include `irdma_query_device`, `irdma_query_port`, `irdma_query_qp`, `irdma_query_pkey`, `irdma_query_gid`, `irdma_get_dev_fw_str`, `irdma_ib_register_device`, `irdma_ib_unregister_device`, and `irdma_ib_dealloc_device`.
- User ABI handling is centered on `irdma_alloc_ucontext`, `irdma_dealloc_ucontext`, `irdma_mmap`, `irdma_mmap_legacy`, `irdma_user_mmap_entry_insert`, and push-page mmap setup/removal helpers.
- Object lifecycle functions include `irdma_alloc_pd`, `irdma_dealloc_pd`, `irdma_create_qp`, `irdma_destroy_qp`, `irdma_create_cq`, `irdma_destroy_cq`, `irdma_resize_cq`, `irdma_create_srq`, `irdma_destroy_srq`, `irdma_modify_srq`, and `irdma_query_srq`.
- QP state management splits into `irdma_modify_qp` for iWARP and `irdma_modify_qp_roce` for RoCE, supported by QP context builders, validation, GSI/vport resource setup, and push-mode allocation.
- Memory operations include `irdma_reg_user_mr`, `irdma_reg_user_mr_dmabuf`, `irdma_rereg_user_mr`, `irdma_dereg_mr`, `irdma_alloc_mr`, `irdma_map_mr_sg`, `irdma_alloc_mw`, `irdma_dealloc_mw`, `irdma_reg_phys_mr`, and `irdma_get_dma_mr`.
- Work/completion paths are `irdma_post_send`, `irdma_post_recv`, `irdma_post_srq_recv`, `irdma_poll_cq`, `__irdma_poll_cq`, `irdma_process_cqe`, and `irdma_req_notify_cq`.
- RoCE-only integration includes `irdma_attach_mcast`, `irdma_detach_mcast`, `irdma_create_ah`, `irdma_create_user_ah`, `irdma_destroy_ah`, `irdma_query_ah`, and the multicast/AH cache helpers.
- Static `ib_device_ops` tables compose common operations with RoCE, iWARP, gen1, and gen3-specific operation sets.

## Control Flow

Device registration calls `irdma_init_rdma_device`, selects RoCE or iWARP node type and protocol operations, sets common verbs operations, overlays gen1 or gen3 extensions, associates the netdev, registers with RDMA core, marks link status active, and emits a port event. Query functions translate hardware attributes and netdev state into RDMA core attributes; RoCE gets pkeys, GID table, UD/GSI, AH, multicast, and RNR support, while iWARP gets RNIC node identity and IW CM callbacks.

Userspace setup begins with `irdma_alloc_ucontext`. It validates ABI version and WQE format support, supports a legacy gen1 response shape, creates an mmap entry for the doorbell page in modern mode, returns hardware limits and feature flags, and initializes per-context registered-memory lists for CQs, QPs, and SRQs. `irdma_mmap` either accepts legacy fixed one-page mapping or resolves RDMA mmap entries into BAR PFNs with noncached or write-combined page protections. QP push pages add two more mmap entries after hardware allocates a push index during QP transition.

QP creation validates attributes, allocates Q2/host context memory, reserves a QP number or gen3 GSI vport, binds send/recv CQs and PD, imports user-registered WQE memory or allocates coherent kernel rings, initializes the low-level QP, fills RoCE or iWARP offload context, adds RoCE work-scheduler QoS when needed, creates the QP through CQP, publishes it in `rf->qp_table`, and returns actual ring sizes and capabilities to userspace. Destruction marks the QP destroy-pending, moves active QPs to error, cancels kernel flush work, cleans CQEs for kernel QPs, drops the table reference and waits unless reset is active, destroys hardware state, removes push mmap entries, and frees QP resources.

QP modification is protocol-specific. RoCE consumes standard IB attributes such as AV, QPN, pkey, qkey, path MTU, PSNs, retry/RNR settings, access flags, and RD atomic limits, updates UDP/RoCE offload context, recalculates VLAN priority and work-scheduler user priority, updates ARP, validates state transitions through `ib_modify_qp_is_ok`, and issues hardware modify commands for INIT/RTR/RTS/SQD/ERR transitions. iWARP ties RTS to CM establishment, handles close/terminate/error states, schedules CM close timers, optionally resets TCP, and serializes against outstanding async hardware modify operations. Both paths can allocate push pages and return push mmap keys to userspace.

CQ/SRQ creation imports user PBL registrations or allocates coherent kernel memory, initializes low-level objects, creates hardware objects via CQP, and returns IDs and sizes. CQ resize creates/imports a replacement buffer, issues `IRDMA_OP_CQ_MODIFY`, saves old kernel buffers on `resize_list`, and later frees old buffers only after polling proves the old CQEs have drained. Polling walks resized buffers before the current CQ, converts low-level completion info into `ib_wc`, consumes software-generated flush completions when hardware has none, and reports resize completion counts back to hardware.

MR registration pins/imports user memory with `ib_umem_get` or `ib_umem_dmabuf_get_pinned_revocable_and_lock`, chooses the best hardware page size, builds PBLEs, optimizes contiguous memory to direct physical registration when possible, allocates randomized STags, and registers through CQP. Special user MR types for QP/CQ/SRQ are not hardware-registered application MRs; instead they populate per-ucontext memory lists later consumed by object create paths. Reregistration first invalidates hardware, then updates access, PD, or translation; dmabuf revocation serializes through the dmabuf reservation lock and invalidates the hardware key before release.

Posting paths translate kernel `ib_send_wr` and `ib_recv_wr` chains into low-level UK operations under QP/SRQ locks. Send supports send, send-with-imm, send-with-invalidate, RDMA write/read, local invalidate, fast MR registration, and gen3 atomics when enabled. UD/GSI send embeds AH ID, qkey, and destination QPN. Receive rejects direct RQ posting for SRQ-backed QPs. CQ notification arms the low-level CQ once, promotes solicited arms to any-event arms, and can report missed events when CQEs or generated completions are present.

## State and Persistence

State lives in RDMA core objects and driver wrappers: ucontexts hold ABI mode, mmap entries, and registered memory lists; PDs hold hardware PD IDs; QPs hold low-level QP state, offload contexts, CQ/PD links, push mmap entries, CM links, timers, and ring memory; CQs hold low-level CQ state, coherent buffers, resize history, generated completions, arm state, and table references; MRs hold umem references, PBLE allocations, STags, access, page size, and registration state. No disk persistence exists. Hardware state persists only until destroyed, reset, or device unregister.

## Dependencies and Integration Points

`verbs.c` integrates with RDMA core uverbs, mmap, GID, AH, CQ, QP, MR, dmabuf, hardware-stats, and IW CM APIs. It depends on `utils.c` for CQP submission, CQP resource cleanup, refs, generated completions, multicast MAC derivation, and QP events; on low-level `irdma_sc_*` and `irdma_uk_*` routines for hardware contexts and WQE/CQE formats; on CM helpers for iWARP connect/listen/accept/reject/close; on PBLE resource management; on Linux DMA, PCI BAR, netdev, VLAN, and dmabuf reservation/fence APIs; and on `virtchnl.c` for gen3 GSI vport setup.

## Risks

The main risks are ABI compatibility, partial-object unwind, and concurrent teardown. User request lengths, ABI version, raw/legacy attribute interpretation, mmap keys, and copy-to-user failure paths must match userspace libraries. QP/CQ/SRQ create paths allocate hardware IDs, coherent memory, PBLs, work-scheduler nodes, CQP state, and table entries in stages; any error unwind can leak hardware resources or leave stale table pointers. CQ resize is subtle because old buffers must survive until all old CQEs have been consumed. MR/dmabuf revocation is high risk because hardware DMA access must be invalidated before the exporter can move or revoke storage. State transitions differ sharply between RoCE and iWARP, and incorrect transitions can deadlock close timers, miss flushes, or expose invalid remote access. AH caching for user AHs relies on identical `ah_info` matching and refcounts under a mutex.

## Test Signals

Good coverage includes ABI negotiation for legacy gen1 and modern userspace; mmap of doorbell and push pages; PD/QP/CQ/SRQ create/destroy failure injection; QP state matrices for RoCE RC/UD/GSI and iWARP RC; push-mode activation and copy-to-user failure rollback; CQ poll, arm, missed event, generated flush completion, and resize drain behavior; user MR registration for MEM/QP/CQ/SRQ types; fast-reg MR map limits; dmabuf revoke, dereg, and rereg paths; multicast attach/detach with IPv4, IPv6, VLAN, and max members; AH cache reuse and destruction; hardware stats reads; and device unregister during active objects/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/verbs.h

## Purpose

`verbs.h` declares the IRDMA driver-private wrappers around RDMA core objects and exposes a small set of helpers shared between `verbs.c`, `utils.c`, and other driver modules. It is the main type contract for ucontext, PD, AH, MR/PBL, SRQ, CQ, QP, mmap entries, firmware-version helpers, completion opcode translation, multicast MAC helpers, device registration, QP events, and generated completions.

## Important APIs, Types, and Functions

- `struct irdma_ucontext` extends `ib_ucontext` with the owning IRDMA device, doorbell mmap entry, per-context CQ/QP/SRQ registered-memory lists and locks, ABI version, legacy mode, and raw-attribute mode.
- `struct irdma_pd`, `struct irdma_ah`, `struct irdma_mr`, `struct irdma_srq`, `struct irdma_cq`, and `struct irdma_qp` are the driver wrappers installed through `INIT_RDMA_OBJ_SIZE`.
- `struct irdma_pbl` and nested `irdma_qp_mr`, `irdma_cq_mr`, and `irdma_srq_mr` represent user memory registrations used as queue backing memory.
- `struct irdma_cq_buf` and `struct irdma_cmpl_gen` support CQ resize buffer lifetime and software-generated completions.
- `struct irdma_user_mmap_entry` records BAR offsets and cacheability for RDMA mmap entries.
- `irdma_fw_major_ver` and `irdma_fw_minor_ver` decode firmware version fields from `dev->feature_info`.
- `set_ib_wc_op_sq`, `set_ib_wc_op_rq`, and `set_ib_wc_op_rq_gen_3` translate internal completion operation types into RDMA core `ib_wc_opcode` values.
- Function prototypes expose registration, unregister, dealloc, QP event, generated flush completion, generated completion polling, and multicast MAC APIs.

## Control Flow

The header does not implement object lifecycles directly, but its structures define how lifecycle code moves state. Ucontext memory registrations are inserted into type-specific lists during MR registration and removed when QP/CQ/SRQ creation consumes them. QPs link RDMA core state, low-level `irdma_sc_qp`, CQs, PD, CM node, offload context, push mmap entries, workqueue/timer state, and kernel/user ring memory. CQs hold the low-level CQ, coherent memory or user memory state, a refcount completion used by async interrupt paths, resize buffers, and generated completions. MR/PBL fields allow one object shape to represent application MRs, memory windows, DMA MRs, and queue-memory registrations.

The inline WC helpers are called from CQ polling after low-level CQ parsing. SQ operation types map to write, read, send, register MR, atomic, and local invalidate completions. RQ mapping differs by hardware generation and send-with-immediate support: older iWARP treats immediate receive as RDMA-write-with-immediate, while gen3 uses low-level op types for receive-with-immediate.

## State and Persistence

The header defines runtime-only in-memory state. Important persistence boundaries are RDMA core object lifetimes, hardware resource IDs, mmap entries, DMA memory references, refcounts/completions, and queue ring state. It also encodes bitfields such as `user_mode`, `is_hwreg`, `dma_mr`, `pbl_allocated`, `on_list`, `flush_issued`, `hte_added`, `suspend_pending`, and `rts_ae_rcvd` that drive teardown and state transitions.

## Dependencies and Integration Points

The types embed RDMA core objects (`ib_ucontext`, `ib_pd`, `ib_ah`, `ib_mr`, `ib_mw`, `ib_srq`, `ib_cq`, `ib_qp`) and low-level IRDMA objects (`irdma_sc_*`, `irdma_*_uk`, PBLE, DMA, AH, and QP context structures). They are consumed by `main.h` container helpers, `verbs.c` object operations, `utils.c` CQP and completion paths, CM code, and low-level hardware programming code.

## Risks

Because these structures define cross-file ownership, layout and flag changes have broad blast radius. Refcount and completion fields must remain paired with table publication/removal rules. Queue-memory PBL fields are type-dependent, so using a CQ PBL as a QP PBL or failing to update `on_list` can corrupt later object creation. Opcode mapping helpers are small but user-visible through CQ polling; wrong mappings break application completion semantics. Bitfield state is compact but easy to update without proper locking if callers do not follow the surrounding `verbs.c` and `utils.c` protocols.

## Test Signals

Compile-time signals include all container conversions, object-size registration, and prototypes matching definitions. Runtime signals include CQ polling opcode correctness for SQ/RQ, gen2 versus gen3 immediate-data receives, QP/CQ refcount completion under destroy, queue-memory registration consumption from ucontext lists, push mmap lifecycle, generated flush completion delivery, and correct firmware version reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/virtchnl.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/virtchnl.c

## Purpose

`virtchnl.c` implements the IRDMA virtual-channel client used by non-privileged functions, especially gen3 VF-style devices, to negotiate capabilities and request privileged PF-mediated setup. It sends synchronous virtual-channel operations, validates responses, translates PF-provided register layouts and bit-field masks into local hardware tables, obtains/releases HMC function IDs, maps AEQ/CEQ queues to interrupt vectors, manages vports, and reads RDMA capabilities.

## Important APIs, Types, and Functions

- `irdma_sc_vchnl_init` initializes virtual-channel state in `struct irdma_sc_dev`, negotiates channel version for non-privileged devices, fetches capabilities, and updates hardware revision.
- Static `vchnl_reg_map` and `vchnl_regfld_map` translate virtual-channel register and field IDs into local `hw_regs`, `hw_masks`, and `hw_shifts` indexes.
- `irdma_alloc_vchnl_req_msg`, `irdma_free_vchnl_req_msg`, `irdma_vchnl_req_send_sync`, `irdma_vchnl_req_verify_resp`, and `irdma_vchnl_req_get_resp` implement common request allocation, serialization, send, response validation, and response copyout.
- `irdma_vchnl_req_get_reg_layout` parses PF-provided register offsets and field descriptions, resolves MMIO addresses, and initializes doorbell pointers.
- `irdma_vchnl_req_get_ver`, `irdma_vchnl_req_get_caps`, `irdma_vchnl_req_get_hmc_fcn`, and `irdma_vchnl_req_put_hmc_fcn` negotiate channel/device capabilities and HMC ownership.
- `irdma_vchnl_req_aeq_vec_map`, `irdma_vchnl_req_ceq_vec_map`, `irdma_vchnl_req_add_vport`, and `irdma_vchnl_req_del_vport` request vector and vport resource configuration from the privileged peer.

## Control Flow

Initialization marks the channel up, stores privilege and PF/VF role, and seeds the requested hardware revision. Privileged devices do not need channel negotiation. Non-privileged devices first send `GET_VER` with the maximum supported channel version, reject peers below the minimum supported version, then send `GET_RDMA_CAPS`; the returned hardware revision replaces the initial revision after range validation.

Every request is built into a fixed-size zeroed `IRDMA_VCHNL_MAX_MSG_SIZE` buffer. The op context is the address of the stack `irdma_vchnl_req`, request payload is copied into `op_buf->buf`, and `irdma_vchnl_req_send_sync` serializes access with `dev->vchnl_mutex` before calling `ig3rdma_vchnl_send_sync`. The received buffer and length are stored in `dev->vc_recv_buf` and `dev->vc_recv_len`, then `irdma_vchnl_req_get_resp` verifies that the response context matches, clamps response data to the caller-provided response buffer, validates size rules for the operation, checks `op_ret`, and copies response payload.

Register-layout parsing reads a sequence of `irdma_vchnl_reg_info` records until an invalid ID. Known IDs are mapped to local hardware register indexes; DB offset and page-relative records are stored as offsets, while BAR-relative records are resolved through `ig3rdma_get_reg_addr`. Doorbell pointers such as `wqe_alloc_db`, `cq_arm_db`, `aeq_alloc_db`, `cqp_db`, and `cq_ack_db` are derived from the populated register table. The following field records are mapped into masks and shifts after validating nonzero bit widths and at most 64 total bits.

HMC and vport operations are small structured requests. Gen3 `GET_HMC_FCN` includes protocol and receives an HMC function ID plus QoS scheduler handles. `ADD_VPORT` and `DEL_VPORT` send vport/QP1 IDs; add-vport copies returned scheduler handles into the provided QoS array. AEQ and CEQ vector mapping allocate a one-vector flexible array request, set the unused queue index to `IRDMA_Q_INVALID_IDX`, and request `QUEUE_VECTOR_MAP`.

## State and Persistence

State is runtime-only and stored in `struct irdma_sc_dev`: channel-up flag, privilege/PF flags, channel version, capabilities, receive buffer length, hardware revision, HMC function ID, QoS handles, register pointer table, mask/shift tables, and doorbell pointers. Requests are temporary heap buffers. The only persistence outside memory is the PF/peer's hardware configuration changed by the virtual-channel operation.

## Dependencies and Integration Points

The file depends on low-level IRDMA hardware definitions, HMC definitions, `ig3rdma_vchnl_send_sync`, `ig3rdma_get_reg_addr`, work-scheduler/QoS structures, and `to_ibdev` logging from `utils.c`. It is called during control-device initialization, gen3 GSI/vport setup and teardown from `verbs.c`/`utils.c`, and interrupt/vector setup code elsewhere in the driver.

## Risks

Virtual-channel parsing is a trust boundary between privileged and non-privileged functions. Response context, length, op return, register IDs, field IDs, bit widths, and register address resolution must be validated before mutating hardware tables. The fixed max message size prevents unbounded allocation but does not by itself prove payload lengths are semantically correct. `resp_len` arithmetic depends on a valid received length at least as large as the response header. Register layout parsing must not accept invalid masks or NULL MMIO addresses, because later MMIO writes would fault or hit wrong registers. The mutex is essential because shared `vc_recv_buf` and `vc_recv_len` are per-device scratch state.

## Test Signals

Useful tests include version negotiation success/failure, unsupported hardware revision rejection, response op-context mismatch, short/oversized response validation, PF error propagation through `op_ret`, register layouts with invalid IDs and invalid bit widths, page-relative versus BAR-relative register mapping, HMC function get/put, QoS handle propagation, AEQ/CEQ vector mapping request shapes, vport add/delete rollback in GSI setup, and concurrent virtual-channel callers proving mutex serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/virtchnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/virtchnl.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/virtchnl.h

## Purpose

`virtchnl.h` defines the IRDMA virtual-channel ABI used between a non-privileged RDMA function and its privileged peer. It assigns channel and operation versions, operation codes, register and register-field IDs, packed request and response buffer formats, HMC/vport/vector/capability payloads, initialization parameters, and public request helper prototypes.

## Important APIs, Types, and Functions

- Channel version constants restrict the supported channel to version 2, with legacy version 0 explicitly documented as unsupported.
- Operation-version constants define per-operation payload revisions for HMC get/put, register layout, queue-vector map/unmap, vport add/delete, and RDMA capabilities.
- `enum irdma_vchnl_ops` assigns the wire operation codes for version, HMC function, register layout, capabilities, queue-vector mapping, and vport management.
- Register IDs such as `IRDMA_VCHNL_REG_ID_CQPTAIL`, `IRDMA_VCHNL_REG_ID_CQPDB`, and `IRDMA_VCHNL_REG_ID_DB_ADDR_OFFSET` abstract PF-provided MMIO layout. `IRDMA_VCHNL_REG_PAGE_REL` marks page-relative offsets.
- Register-field IDs such as `IRDMA_VCHNL_REGFLD_ID_CCQPSTATUS_CQP_OP_ERR` and `IRDMA_VCHNL_REGFLD_ID_COMMIT_FPM_CQCNT` abstract hardware bit shifts/masks.
- Packed payloads include `irdma_vchnl_req_hmc_info`, `irdma_vchnl_resp_hmc_info`, `irdma_vchnl_op_buf`, `irdma_vchnl_resp_buf`, and `irdma_vchnl_rdma_caps`.
- Flexible-array vector/vport structures include `irdma_vchnl_qvlist_info`, `irdma_vchnl_qv_info`, `irdma_vchnl_req_vport_info`, and `irdma_vchnl_resp_vport_info`.
- `irdma_vchnl_init_info`, `irdma_vchnl_req`, and `irdma_vchnl_req_init_info` are local driver control structures used to initialize and issue requests.
- Public prototypes expose initialization, version/capability/HMC/register/vector/vport requests, and response parsing.

## Control Flow

The header defines the shape consumed by `virtchnl.c`: callers fill `irdma_vchnl_req_init_info` with operation code, operation version, optional request payload, and optional response buffer. `virtchnl.c` serializes that into `irdma_vchnl_op_buf`, sends it through the hardware-specific transport, receives `irdma_vchnl_resp_buf`, and copies the packed `buf[]` into the expected typed payload.

Register layout flow uses arrays of `irdma_vchnl_reg_info` followed by `irdma_vchnl_reg_field_info`, terminated by invalid IDs. Capability flow returns `irdma_vchnl_rdma_caps`, whose minimum response size can be as small as one byte for forward-compatible extension. HMC and vport responses return scheduler handles for each user priority.

## State and Persistence

The header has no executable state. It defines wire-compatible packed structures and local request descriptors. Fields such as `op_ctx`, `buf_len`, `op_ret`, `hmc_func`, `qs_handle`, `hw_rev`, `cqp_timeout_s`, and register offsets become runtime state in `struct irdma_sc_dev` after `virtchnl.c` processes them.

## Dependencies and Integration Points

The file includes `hmc.h` and `irdma.h` for HMC, hardware generation, and priority constants. It forward-declares `struct irdma_qos` and uses `struct irdma_sc_dev` from the wider driver. The definitions integrate with `virtchnl.c`, gen3 hardware-specific channel transport, device initialization, interrupt vector setup, GSI/vport setup, and CQP timeout tuning in `utils.c`.

## Risks

This header is an ABI contract. Changing packed structure layout, operation IDs, version constants, or register/field IDs can break PF/VF interoperability. Flexible-array sizes must be computed with `struct_size` by callers. Because response capability minimum size is intentionally small, consumers must tolerate missing future fields and keep defaults sane. Packed unaligned structures require careful copying rather than direct assumptions about natural alignment.

## Test Signals

Compile and ABI tests should check structure sizes, packed offsets, operation ID stability, register ID translation coverage, `struct_size` calculations for vector lists, and version min/max behavior. Runtime tests should confirm that every public prototype has a matching implementation and that PF/VF peers using the declared version and payloads can negotiate caps, register layout, HMC function, queue-vector mapping, and vport add/delete successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/virtchnl.h -->
