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
