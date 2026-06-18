# subset-b-003955 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw.h

Purpose: Defines the central SoftiWARP provider object model for this kernel RDMA driver: device capabilities, PDs, memory registrations, CQs, QPs, RX/TX protocol contexts, SRQs, helper conversions, queue helpers, CRC helpers, and exported cross-file function prototypes. This header is the shared contract tying RDMA core verbs, iWARP wire processing, TCP socket callbacks, memory protection, and completion handling together.

Important APIs/types/functions: `struct siw_device` wraps `ib_device`, device limits, xarrays for QP and memory lookup, CEP/QP lists, and active object counters. `struct siw_qp` owns `ib_qp`, state lock, CEP/socket association, SQ/RQ/ORQ/IRQ queues, RX stream state, TX context, completion queues, SRQ, mmap entries, and lifetime reference state. `struct siw_mem`, `siw_mr`, `siw_umem`, and `siw_pbl` model STag-indexed registered memory. `siw_qp_id2obj()` uses RCU plus `kref_get_unless_zero`; queue helpers inspect user-mapped WQE flags with `READ_ONCE`; CRC helpers wrap crc32c for MPA.

Control flow: Verbs code allocates device, QP, CQ, SRQ, and MR instances matching these structures. CM moves sockets into QP ownership. TX/RX paths consume `siw_iwarp_tx` and `siw_rx_stream` state across partial TCP sends/receives. Completion helpers flush and reap queues through `siw_cq`.

State and persistence behavior: State is entirely in kernel memory and RDMA-core objects, not persistent on disk. Long-lived state is protected by spinlocks, rwsems, xarrays, krefs, atomics, and memory barriers because user queues may be mmaped and touched concurrently.

Dependencies/integration: Depends on RDMA core headers, `rdma/siw-abi.h`, `iwarp.h`, Linux sockets/skbuff, CRC, xarray, RCU, and ibverbs object lifecycles. Integration points are the function prototypes used by `siw_main.c`, `siw_verbs.c`, `siw_cm.c`, `siw_qp*.c`, `siw_mem.c`, and `siw_cq.c`.

Risks: Incorrect queue flag ordering can expose partially written WQEs/CQEs to userspace. Kref/xarray lifetime mistakes can become UAFs in socket callbacks or TX worker paths. STag validation and bounds errors are security-sensitive. Any layout drift must stay ABI-compatible with `siw-abi.h`.

Test signals: Build with lockdep/KASAN/KCSAN, create/destroy QPs/CQs/MRs/SRQs from userspace, exercise mmaped queues, RDMAP SEND/WRITE/READ, CRC on/off, invalid STag/key/bounds paths, QP error/flush paths, and concurrent QP destruction while sockets or TX workers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cm.c

Purpose: Implements SoftiWARP iWARP connection management over kernel TCP sockets and MPA request/reply negotiation. It bridges RDMA IWCM events to socket operations, performs active connect and passive listen/accept/reject, negotiates MPA v1/v2 options, IRD/ORD, CRC, GSO, and peer-to-peer RTR mode, then hands established sockets to the QP RX/TX path.

Important APIs/types/functions: `siw_connect()`, `siw_accept()`, `siw_reject()`, `siw_create_listen()`, and `siw_destroy_listen()` are registered as iWARP CM verbs. `siw_cep_alloc()`, `siw_cep_get/put()`, `siw_cep_set_inuse/free()`, and `siw_cm_alloc_work()` manage endpoint lifetime and serialized CEP state. `siw_send_mpareqrep()`, `siw_recv_mpa_rr()`, `siw_proc_mpareq()`, and `siw_proc_mpareply()` implement MPA framing and negotiation. Socket callbacks include `siw_cm_llp_state_change()`, `siw_cm_llp_data_ready()`, `siw_cm_llp_error_report()`, and the temporary `siw_rtr_data_ready()` callback for MPAv2 RTR establishment.

Control flow: Active connect creates a TCP socket, binds/connects synchronously, associates a CEP/QP/IWCM id, sends MPA REQ, and schedules timeout work. Data-ready work reads MPA REP, validates keys/options, transitions the QP to RTS via `siw_qp_modify()`, installs QP socket callbacks, optionally sends zero-length RTR traffic, then emits `IW_CM_EVENT_CONNECT_REPLY`. Passive listen binds a TCP socket, accepts child sockets in workqueue context, waits for MPA REQ, upcalls `IW_CM_EVENT_CONNECT_REQUEST`, and later `siw_accept()` transitions the QP to RTS before sending MPA REP.

State and persistence behavior: CEP state moves through IDLE, LISTENING, CONNECTING, AWAIT_MPAREQ, RECVD_MPAREQ, AWAIT_MPAREP, RDMA_MODE, and CLOSED. State lives only in memory. CEP krefs cover socket callback ownership, IWCM references, queued work, listener-child links, and QP associations. Timers are implemented as delayed work.

Dependencies/integration: Uses Linux kernel sockets/TCP, IWCM, RDMA core, MPA/iWARP helpers, QP state functions, and module parameters from `siw_main.c`. `siw_cm_init()` creates a single-threaded CM workqueue for ordered endpoint processing.

Risks: High-risk areas are socket callback replacement/restoration, CEP/QP refcount transfer, MPA private-data length handling, timeout cancellation races, listener wildcard binding, and failure unwinding that must not double-release sockets or IWCM ids. MPA CRC/marker negotiation affects interoperability.

Test signals: Validate IPv4/IPv6 active/passive connects, MPA v1/v2 private data, CRC strict/required modes, peer reject and timeout, listener destruction with pending children, simultaneous close, first RDMA frame arriving immediately after MPA REP, lockdep with callback reclassification, and QP destroy during handshake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cm.h

Purpose: Declares the SoftiWARP connection endpoint model, MPA negotiation state, CM work item types, socket helper shims, and public CM entry points used by `siw_cm.c`, `siw_main.c`, and QP close paths.

Important APIs/types/functions: `enum siw_cep_state` is the endpoint state machine. `struct siw_mpa_info` stores the received/sent MPA header, MPAv2 negotiation payload, private data pointer, and bytes received. `struct siw_cep` binds IWCM id, SIW device, socket, QP, listener links, work freelist, MPA timer, negotiated ORD/IRD, enhanced setup flag, saved socket callbacks, lock/kref/waitqueue, and in-use serialization. `enum siw_work_type` and `struct siw_cm_work` describe accept, MPA read, socket close, peer close, and timeout work. `getname_peer()`, `getname_local()`, and `ksock_recv()` are thin socket helpers.

Control flow: CM code allocates a CEP, associates it with a socket through `sk_user_data`, replaces socket callbacks, queues `siw_cm_work` items, and eventually moves the socket to QP callbacks. Listen CEPs hold child CEPs through `listen_cep`; passive connect requests pass child CEPs through IWCM provider data.

State and persistence behavior: No persistent storage. The header encodes in-memory synchronization expectations: CEP lock protects state/work freelist/timer, kref guards callback/work lifetimes, and `in_use` plus waitqueue serialize state-machine execution across callbacks and worker context.

Dependencies/integration: Includes `net/sock.h`, TCP, and `rdma/iw_cm.h`. It exposes `siw_connect`, `siw_accept`, `siw_reject`, listen create/destroy, CM init/exit, CEP refcount helpers, and `siw_cm_queue_work()` to the rest of the driver.

Risks: Because `sk_to_cep()` and `sk_to_qp()` trust `sk_user_data`, any callback after disassociation or wrong callback ordering can crash. Work freelist sizing must cover concurrent close/data/timeout events. Provider-data overloading for listener versus passive child IDs is subtle.

Test signals: Compile-time coverage of prototypes, active/passive IWCM calls, socket callback stress, listener teardown, private data propagation, timeout path, and sanitizers/lockdep around CEP lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cq.c

Purpose: Implements completion queue reaping and CQ flush for SoftiWARP. It translates internal `siw_cqe` records produced by QP completion paths into standard `ib_wc` work completions consumed by kernel clients and CQ polling.

Important APIs/types/functions: `map_wc_opcode[]` maps SIW opcodes to `IB_WC_*` opcodes. `map_cqe_status[]` maps internal SIW completion statuses to `ib_wc_status`. `siw_reap_cqe()` pops one valid CQE under `cq->lock`, fills an `ib_wc`, clears the CQE valid flag, and advances `cq_get`. `siw_cq_flush()` drains all currently valid CQEs by repeatedly reaping.

Control flow: TX/RX completion producers write CQEs into the ring and set `SIW_WQE_VALID`. Pollers call `siw_poll_cq()` in `siw_verbs.c`, which delegates here. During CQ destroy or queue flush, this file clears outstanding entries so backing memory can be released.

State and persistence behavior: CQ state is an in-memory ring with `cq_put`, `cq_get`, `num_cqe`, and a queue that may be mmaped to userspace. No state persists outside the kernel object. `READ_ONCE`/`WRITE_ONCE` protect against concurrent userspace-visible flag changes.

Dependencies/integration: Depends on `ib_verbs.h` and `siw.h`. Completion producers are in `siw_qp.c`; consumers are `siw_verbs.c` poll/destroy paths. Kernel CQs carry `base_qp` references and invalidate metadata; user CQs may have CQE fields modified by userspace, so this file validates opcode/status before array lookup.

Risks: CQE flag ordering and bounds checking are critical. User-mapped CQEs are adversarial; missing opcode/status validation could cause out-of-bounds reads. CQ overflow is handled by producers with CQ error events, so tests need to cover producer/consumer race behavior.

Test signals: Poll empty and non-empty CQs, kernel and user CQ modes, invalid user-written opcode/status, remote-invalidation completions, CQ flush on destroy, CQ overflow events, and concurrent producer/poller stress with KCSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_main.c

Purpose: Provides SoftiWARP module initialization, RDMA device registration, netdevice integration, per-CPU TX worker placement, module parameters, and the RDMA device operations table binding the provider to RDMA core and IWCM.

Important APIs/types/functions: Global tunables include `zcopy_tx`, `try_gso`, `loopback_enabled`, `mpa_crc_required`, `mpa_crc_strict`, `siw_tcp_nagle`, `mpa_version`, and `peer_to_peer`. `siw_device_ops` registers all verbs and IWCM callbacks. `siw_device_create()` allocates and initializes `struct siw_device`, RDMA identity, netdev binding, limits, xarrays, counters, and ops. `siw_newlink()` implements RDMA netlink `newlink` for type `siw`. `siw_netdev_event()` unregisters on netdev removal and emits port events on address changes. `siw_get_tx_cpu()` and `siw_put_tx_cpu()` balance QP TX assignment across NUMA-local worker CPUs.

Control flow: Module init validates constants, initializes CPU masks, starts CM and TX workers, registers a netdevice notifier, and registers RDMA link ops. Users create SIW devices via RDMA netlink; each device is attached one-to-one to a qualified netdev. Module exit stops workers, unregisters notifier/link ops/driver, exits CM, and frees CPU masks.

State and persistence behavior: Module-level state consists of CPU masks, per-CPU use counters, TX kthreads, and RDMA link/notifier registrations. Device state is in RDMA core and `siw_device`; there is no disk persistence.

Dependencies/integration: Integrates with Linux netdevice events, RDMA core registration, RDMA netlink, kthreads, NUMA CPU topology, and all SIW verbs/CM/QP functions. Qualifies Ethernet, IEEE802, ARPHRD_NONE, and optional loopback netdevs.

Risks: Init error unwinding spans CM, TX threads, CPU masks, and notifiers. TX CPU selection must handle offline CPUs and no-worker cases. Netdev unregister races can interact with active QPs and CM endpoints. Device naming and `dev_id` are process-local and incrementing.

Test signals: Module load/unload, rdma link add/delete for eligible and ineligible netdevs, loopback enable behavior, CPU hotplug or offline TX CPU reassignment, netdev unregister, address-change event delivery, and failure injection during init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_mem.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_mem.c

Purpose: Implements SoftiWARP memory registration backing, STag lookup/validation/invalidation, user-memory pinning representation, physical buffer list allocation, PBL address lookup, and memory reference release.

Important APIs/types/functions: `siw_mem_id2obj()` resolves an STag index from the device memory xarray under RCU and returns a referenced `siw_mem`. `siw_mr_add_mem()` allocates a memory object, selects a cyclic 24-bit STag index, stores PD/VA/length/permissions, and sets MR lkey/rkey. `siw_mr_drop_mem()` invalidates and removes the memory object from the xarray. `siw_check_mem()` and `siw_check_sge()` enforce STag validity, PD match, permissions, key match, and address bounds. `siw_invalidate_stag()` implements local/remote invalidation. `siw_umem_get()` pins userspace memory through `ib_umem_get()` and stores pages in chunked arrays. `siw_pbl_get_buffer()` walks PBL entries by byte offset.

Control flow: Verbs registration calls into `siw_umem_get()` or `siw_pbl_alloc()`, then `siw_mr_add_mem()`. TX/RX paths resolve and hold memory references while moving data, then release with `siw_wqe_put_mem()` or specific put paths. Deregistration invalidates first, erases from lookup, and drops the final reference after active users finish.

State and persistence behavior: Memory registrations are transient kernel objects keyed by STag. `stag_valid` is the fast invalidation bit, made visible before xarray erase with a barrier. User pages remain pinned through `ib_umem` until release.

Dependencies/integration: Uses RDMA umem, scatter-gather iteration, DMA virtual helpers, xarray, RCU, krefs, and SIW QP WQE formats. It is a security boundary for all remote RDMA access.

Risks: Bounds checks use `addr + len` arithmetic and must avoid overflow assumptions. STag key/index mismatches, stale references after deregistration, and invalidation ordering are high-risk. Chunk calculation in `siw_umem_get()` must match pinned pages.

Test signals: Register/deregister user MRs, DMA MRs, fast-reg PBL MRs, zero-length rejection, stale STag access, wrong PD, wrong key, remote write/read permission failures, local invalidation, remote invalidation via SEND_INV, and deregister while TX/RX holds references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_mem.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_mem.h

Purpose: Declares the memory-management API used by verbs, TX, RX, and QP flush code, plus inline helpers for releasing memory references and resolving pinned user pages.

Important APIs/types/functions: Exposes `siw_umem_get/release()`, `siw_pbl_alloc()`, `siw_pbl_get_buffer()`, `siw_mem_id2obj()`, `siw_invalidate_stag()`, `siw_check_mem()`, `siw_check_sge()`, `siw_wqe_put_mem()`, `siw_mr_add_mem()`, `siw_mr_drop_mem()`, and `siw_free_mem()`. `siw_mem_put()` wraps kref release. `siw_unref_mem_sgl()` drops a sequence of memory references in WQEs. Chunk macros define 512-page chunks and derived page-list sizing. `siw_get_upage()` maps a virtual address into the two-level `siw_umem` page array.

Control flow: TX/RX paths call check helpers to resolve SGEs into referenced `siw_mem` objects, use page/PBL helpers to locate memory, and then release via WQE put helpers. Verbs uses allocation and MR attach/drop helpers during registration/deregistration.

State and persistence behavior: The API manipulates in-memory, kref-counted memory registrations and pinned page arrays. It assumes callers hold references before dereferencing memory and release them once WQE processing completes.

Dependencies/integration: Depends on `siw.h` structure definitions and RDMA kernel types included by compile units. It is used heavily by `siw_mem.c`, `siw_qp_tx.c`, `siw_qp_rx.c`, `siw_qp.c`, and `siw_verbs.c`.

Risks: `siw_get_upage()` trusts `umem->fp_addr` and `num_pages`; wrong chunk arithmetic can return invalid pages. `siw_unref_mem_sgl()` stops at the first NULL, so callers must keep contiguous resolved-memory slots. Reference leaks or double puts surface under error and flush paths.

Test signals: Page lookup at first/last page, non-page-aligned buffers, multi-chunk MRs, partial SGE resolution failure, WQE flush after partial memory resolution, and KASAN/KCSAN on deregister plus in-flight TX/RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp.c

Purpose: Implements QP-level state transitions, socket data/write callbacks after connection establishment, read-queue initialization, terminate-message generation, SQ/RQ/ORQ/IRQ activation, completion production, queue flushing, and QP xarray lifetime.

Important APIs/types/functions: `iwarp_pktinfo[]` defines per-RDMAP opcode header templates and RX handlers. `siw_qp_llp_data_ready()` consumes TCP payload through `siw_tcp_rx_data()` when QP is RTS. `siw_qp_llp_close()` transitions QPs on LLP close and flushes queues. `siw_qp_mpa_rts()` creates MPAv2 zero-length RTR READ/WRITE work. `siw_qp_modify()` handles SIW state transitions and access flags. `siw_activate_tx()` selects between pending inbound read responses and SQ work. `siw_sqe_complete()` and `siw_rqe_complete()` write CQEs and fire CQ callbacks. `siw_sq_flush()` and `siw_rq_flush()` complete queued/in-progress work with flush errors. `siw_qp_add()` and `siw_free_qp()` manage xarray registration and teardown.

Control flow: CM/verbs call `siw_qp_modify()` to move IDLE/RTR into RTS once MPA succeeds. Post-send paths queue SQEs and call `siw_activate_tx()`, which may serve IRQ read responses before local SQ work. RX completion of read responses releases ORQ and may resume fenced TX. Close/error paths suspend RX/TX, send terminate when possible, drop CM, and flush queues.

State and persistence behavior: QP state is guarded by `state_lock`; SQ/RQ/ORQ have spinlocks or state-lock-only flush assumptions. Queue indices are free-running counters modulo power-of-two sizes. Completion state is shared with CQ rings and possibly userspace mmap. No persistence outside kernel objects.

Dependencies/integration: Integrates CM CEPs, TCP callbacks, TX/RX files, memory helpers, CQ events, and RDMA core events. Uses krefs and xarray for QP lookup.

Risks: State transitions and flushes are race-prone with socket callbacks, TX workers, and QP destruction. CQ overflow handling must not leave WQEs permanently valid. ORQ/IRQ fairness and fencing can deadlock if flags or indices are mishandled. Terminate generation reconstructs headers and is protocol-sensitive.

Test signals: QP state matrix, active/passive close, simultaneous socket close and destroy, SQ/RQ flush order, CQ overflow, fenced reads, ORQ full/resume, IRQ starvation prevention, remote terminate, and invalid work opcode/status paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp_rx.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp_rx.c

Purpose: Implements the receive-side TCP-to-iWARP parser and executor. It consumes stream bytes from TCP skbs, reconstructs MPA FPDUs, validates DDP/RDMAP headers, places SEND/WRITE/READ RESPONSE payloads into registered memory, creates READ RESPONSE work for inbound READ REQUESTs, validates CRC/trailers, completes received messages, and drops the connection on protocol errors.

Important APIs/types/functions: Data movers include `siw_rx_umem()`, `siw_rx_kva()`, `siw_rx_pbl()`, and `siw_rx_data()`. Header validators include `siw_send_check_ntoh()`, `siw_write_check_ntoh()`, and `siw_rresp_check_ntoh()`. Opcode handlers are `siw_proc_send()`, `siw_proc_write()`, `siw_proc_rreq()`, `siw_proc_rresp()`, and `siw_proc_terminate()`. `siw_get_hdr()` parses minimum and full iWARP headers; `siw_get_trailer()` validates padding/CRC. `siw_rdmap_complete()` finalizes complete RDMAP messages. `siw_tcp_rx_data()` is the main TCP read callback routine.

Control flow: `siw_tcp_rx_data()` loops while skb bytes remain and advances `SIW_GET_HDR`, `SIW_GET_DATA_START/MORE`, and `SIW_GET_TRAILER`. Once a full FPDU trailer validates, it completes the RDMAP message if `DDP_FLAG_LAST` is set. SEND consumes RQ/SRQ entries, WRITE resolves remote target STag, RRESP matches ORQ read state, RREQ creates TX-side READ RESPONSE work, and TERM logs peer error then resets.

State and persistence behavior: RX state is held in `siw_rx_stream` and two `siw_rx_fpdu` contexts for tagged and untagged interleaving. It tracks MSN, tagged offsets, current WQE, SGE/PBL indices, CRC accumulator, partial-header/data/trailer progress, and suspend status. No persistent storage.

Dependencies/integration: Uses skb copy APIs, page mapping, memory validation helpers, QP/CQ completion helpers, SRQ events, TX scheduling for read responses, and CM drop scheduling.

Risks: TCP fragmentation means every state transition must tolerate partial headers, payloads, and trailers. Protocol errors must set correct TERM info and complete/flush local WQEs safely. CRC over userspace buffers deliberately uses skb data to avoid races. RRESP matching to ORQ is security-critical.

Test signals: Fragment every FPDU boundary, CRC success/failure, padding lengths 0-3, SEND with too-small RQ, SRQ limit event, WRITE invalid STag/key/bounds/permission, RRESP without ORQ, READ REQUEST IRQ exhaustion, interleaved tagged/untagged messages, remote TERM parsing, and close during partial receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp_tx.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp_tx.c

Purpose: Implements the transmit-side SoftiWARP SQ engine. It validates WQE memory, builds RDMAP/DDP/MPA headers, handles inline and fragmented payloads, computes optional MPA CRC, sends through kernel TCP sockets with copy or zero-copy page splicing, processes local REG_MR/LOCAL_INV operations, and schedules per-CPU TX worker execution.

Important APIs/types/functions: `siw_qp_prepare_tx()` builds one complete short FPDU or initializes fragmented send state. `siw_prepare_fpdu()` sizes each FPDU to TCP MSS/GSO limits and sets DDP LAST/padding. `siw_tx_ctrl()` sends complete control/header fragments. `siw_tx_hdt()` sends header-data-trailer FPDUs and updates partial-send state. `siw_0copy_tx()` and `siw_tcp_sendpages()` implement page-based TX. `siw_check_sgl_tx()` resolves SGEs. `siw_qp_sq_proc_tx()` processes wire operations; `siw_qp_sq_proc_local()` handles local memory verbs. `siw_qp_sq_process()`, `siw_sq_start()`, `siw_run_sq()`, `siw_create_tx_threads()`, and `siw_stop_tx_threads()` implement scheduling.

Control flow: Post-send or IRQ activation prepares a current WQE. If first processing, memory is checked, bytes are calculated, TCP segment length updated, and a short or fragmented FPDU is prepared. The TX loop sends control-only or HDT data, pauses on `-EAGAIN`, reschedules on burst exhaustion, completes successful WQEs, or drops the connection and completes errors on failure.

State and persistence behavior: TX state lives in `siw_iwarp_tx`: current packet union, sent header bytes, bytes unsent, WQE progress, SGE/PBL indices, CRC state, sendpage and GSO flags, ORQ fence flag, and syscall context. Per-CPU worker queues are in `llist_head`s. No persistent state.

Dependencies/integration: Uses TCP sendmsg/sendpage internals, page mapping, RDMA memory helpers, QP completion helpers, CM drop, CPU TX workers from `siw_main.c`, and `iwarp_pktinfo[]` templates.

Risks: Partial TCP sends must leave resumable state exactly correct, including CRC and trailer progress. Zero-copy with unsignalled user buffers has lifetime/immutability assumptions. ORQ cleanup on failed READ send is race-sensitive with loopback RRESP. Fragment array sizing and kmap ordering are correctness and safety risks.

Test signals: Short inline SEND/WRITE, multi-SGE large payloads, send pauses at header/data/trailer, CRC enabled, zero-copy threshold behavior, GSO/no-GSO, RDMA READ loopback, ORQ full, fenced WQEs, REG_MR/LOCAL_INV, TX CPU worker wakeup, CPU offline reassignment, and injected TCP send errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_verbs.c

Purpose: Implements the RDMA core verbs surface for SoftiWARP: userspace context allocation, device/port/GID queries, PD/QP/CQ/SRQ lifecycle, post-send/receive, CQ poll/notify, mmap of user queues, MR registration/deregistration/mapping, and asynchronous event dispatch.

Important APIs/types/functions: `siw_alloc_ucontext()`, `siw_query_device()`, `siw_query_port()`, and `siw_query_gid()` expose device capabilities and identity. `siw_create_qp()`, `siw_verbs_modify_qp()`, `siw_destroy_qp()`, `siw_post_send()`, and `siw_post_receive()` implement QP verbs. `siw_create_cq()`, `siw_poll_cq()`, and `siw_req_notify_cq()` implement CQ operations. MR functions include `siw_reg_user_mr()`, `siw_alloc_mr()`, `siw_map_mr_sg()`, `siw_get_dma_mr()`, and `siw_dereg_mr()`. SRQ functions cover create/modify/query/destroy/post. `siw_mmap()` maps vmalloc-backed queues via RDMA mmap entries.

Control flow: Userspace creates context, then PD/CQ/QP/SRQ/MR objects. User QPs/CQs/SRQs allocate `vmalloc_user` rings and return mmap offsets through SIW ABI responses. Kernel clients post WR lists directly; user-mapped queues are consumed from shared rings. Posting SEND validates state and queue space, converts IB WRs to SIW SQEs, marks them valid with barriers, and starts TX. Receive posting does the same for RQ/SRQ entries.

State and persistence behavior: Object counts are device atomics. QP/CQ/SRQ rings may be mmaped and synchronized through flags/barriers. MR state persists only as registered kernel objects and pinned memory until deregistration. Destroy paths remove mmap entries, suspend QPs, force error state, and wait for QP kref completion.

Dependencies/integration: Registered by `siw_main.c` in `ib_device_ops`; delegates state transitions to `siw_qp.c`, memory operations to `siw_mem.c`, completions to `siw_cq.c`, and events to RDMA core callbacks.

Risks: Uverbs ABI size checks, mmap entry lifetime, immediate post errors versus queued work, QP destroy with active callbacks, and user-mapped ring trust boundaries are high-risk. Some operations are intentionally unsupported and must return stable errors. MR deregistration while active relies on krefs and RCU.

Test signals: libibverbs smoke tests, rdma-core SIW tests, create/destroy loops, mmaped queues, kernel-client post paths, CQ notify missed events, MR reg/fast-reg/map/dereg, SRQ limit events, QP modify state matrix, drain SQ/RQ in error state, and fuzz invalid WR opcodes/flags/sge counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_verbs.h

Purpose: Declares the RDMA verbs entry points implemented by `siw_verbs.c` and a small SGL conversion helper. It is the interface consumed by `siw_main.c` when constructing `ib_device_ops` and by other SIW files that need event or mmap callbacks.

Important APIs/types/functions: `siw_copy_sgl()` copies RDMA-core `ib_sge` arrays into SIW ABI `siw_sge` arrays. Prototypes cover context, device, port, GID, PD, QP, CQ, MR, SRQ, mmap, and event functions: `siw_create_qp`, `siw_post_send`, `siw_post_receive`, `siw_poll_cq`, `siw_reg_user_mr`, `siw_alloc_mr`, `siw_map_mr_sg`, `siw_post_srq_recv`, `siw_qp_event`, `siw_cq_event`, `siw_srq_event`, and `siw_port_event`.

Control flow: `siw_main.c` binds most of these functions into the RDMA core ops table. `siw_qp.c`, `siw_qp_rx.c`, and `siw_qp_tx.c` call event helpers and rely on SGL layouts produced by post paths. CM uses QP event integration indirectly through state changes and errors.

State and persistence behavior: The header itself has no state. It defines the callable surface for code that allocates or mutates in-memory RDMA objects and user-mapped queues.

Dependencies/integration: Includes Linux errno, IWCM, ib verbs, user verbs, `siw.h`, and `siw_cm.h`. This creates a broad dependency surface; changes here ripple through provider registration and all compile units using verbs prototypes.

Risks: Prototype drift with RDMA core APIs breaks builds across kernel versions. `siw_copy_sgl()` assumes destination capacity has already been validated by the caller. Duplicate `siw_query_port` declaration is harmless but a maintenance smell.

Test signals: Full driver build against target kernel headers, sparse/checkpatch for prototype mismatches, create/post/query verbs smoke tests, and compile coverage with user and kernel resource paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/Makefile

Purpose: Defines the kbuild inclusion map for InfiniBand upper-layer protocol drivers in this source tree. It routes selected kernel configuration symbols to ULP subdirectories.

Important APIs/types/functions: This is a Makefile, not C code. It conditionally includes `ipoib/`, `srp/`, `srpt/`, `iser/`, `isert/`, and `rtrs/` via `obj-$(CONFIG_...) += directory/` assignments.

Control flow: During kernel build, kbuild evaluates each `CONFIG_INFINIBAND_*` symbol. Enabled symbols add the corresponding subdirectory to the build traversal; disabled symbols omit it completely. The file has no runtime control flow.

State and persistence behavior: No runtime state. The only persistent effect is build graph selection from kernel configuration.

Dependencies/integration: Integrates with the parent InfiniBand driver Makefile and each ULP subdirectory Makefile. It depends on Kconfig symbols being defined elsewhere, including the IPoIB symbols in `ulp/ipoib/Kconfig`.

Risks: A missing or misspelled config symbol silently excludes a ULP. Directory order can matter if future build products have implicit dependencies, though these entries are currently independent. Because this file only selects subdirectories, per-driver object composition lives elsewhere.

Test signals: `make olddefconfig` with each ULP enabled/disabled, `make M=drivers/infiniband/ulp`, checking generated built-in/module targets, and confirming IPoIB object traversal only when `CONFIG_INFINIBAND_IPOIB` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/Kconfig

Purpose: Defines kernel configuration options for IP-over-InfiniBand support, connected mode, and debug instrumentation.

Important APIs/types/functions: `CONFIG_INFINIBAND_IPOIB` is a tristate depending on `NETDEVICES && INET` and enables the IPoIB driver. `CONFIG_INFINIBAND_IPOIB_CM` is a bool depending on IPoIB that compiles connected-mode support. `CONFIG_INFINIBAND_IPOIB_DEBUG` defaults to yes and includes debug code/debugfs support when IPoIB is enabled. `CONFIG_INFINIBAND_IPOIB_DEBUG_DATA` depends on debug and adds data-path debug instrumentation.

Control flow: Kconfig presents these options during configuration and writes selected symbols into `.config`. The IPoIB Makefile then includes optional objects based on these symbols. Connected mode is compiled only when selected and still requires runtime mode changes through sysfs.

State and persistence behavior: Configuration choices persist in the kernel `.config` and determine compile-time object inclusion. There is no runtime state in this file, but help text documents sysfs and MTU implications.

Dependencies/integration: Integrates with kbuild and `ulp/ipoib/Makefile`. Runtime documentation is referenced through `Documentation/infiniband/ipoib.rst`. Connected mode affects `ipoib_cm.o`; debug affects `ipoib_fs.o` and module parameters/debugfs.

Risks: Debug defaults can increase compiled code and data-path debug can affect performance even when output is off. Connected mode help warns that multicast and UD traffic may drop unless destination MTU is constrained. Dependency changes can alter whether IPoIB is available on minimal networking builds.

Test signals: Kconfig dependency tests, build with IPoIB as built-in/module/off, connected mode on/off object inclusion, debugfs availability under debug, data-path performance comparison with debug data, and runtime MTU/mode sysfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/Makefile

Purpose: Defines the kbuild object composition for the IPoIB kernel module/object.

Important APIs/types/functions: `obj-$(CONFIG_INFINIBAND_IPOIB) += ib_ipoib.o` creates the aggregate IPoIB target. `ib_ipoib-y` always includes `ipoib_main.o`, `ipoib_ib.o`, `ipoib_multicast.o`, `ipoib_verbs.o`, `ipoib_vlan.o`, `ipoib_ethtool.o`, and `ipoib_netlink.o`. `ib_ipoib-$(CONFIG_INFINIBAND_IPOIB_CM)` conditionally adds `ipoib_cm.o`. `ib_ipoib-$(CONFIG_INFINIBAND_IPOIB_DEBUG)` conditionally adds `ipoib_fs.o`.

Control flow: Kbuild builds the aggregate object from the listed components when IPoIB is enabled. Optional connected-mode and debug source files are compiled into the same aggregate only when their config symbols are true. There is no runtime logic here.

State and persistence behavior: No runtime state. Build output is determined by persistent kernel configuration.

Dependencies/integration: Driven by `ulp/ipoib/Kconfig` and included by `ulp/Makefile`. The object grouping means symbol visibility and initialization are linked into one driver target, with optional feature code compiled in or absent.

Risks: Forgetting to add a new source file here will produce unresolved symbols or missing functionality. Optional object guards must match the C preprocessor expectations in IPoIB sources. Debug object inclusion changes debugfs/module-parameter behavior.

Test signals: Build all config combinations: base IPoIB only, connected mode, debug, debug-data, and module/built-in. Inspect `ib_ipoib.o` composition or build logs, and run modpost to catch unresolved references from optional code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/Makefile -->
