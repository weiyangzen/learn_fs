# Research: subset-b-005294

Grouped research for the lpfc NVMe initiator, shared NVMe/NVMET declarations, and NVMe target implementation. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvme.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvme.c

## Purpose

`lpfc_nvme.c` implements the initiator-side NVMe over Fibre Channel binding for the Broadcom/Emulex lpfc SLI-4 driver. It registers an `nvme_fc_port_template` with the Linux NVMe-FC transport, translates transport callbacks into lpfc work queue entries, manages local and remote NVMe port lifetime, sends and receives NVMe link service traffic, submits NVMe FCP I/O, and handles abort, completion, drain, and reset cleanup paths.

The file is tightly coupled to the lpfc node discovery model. NVMe remote ports are bound to `struct lpfc_nodelist` instances through `ndlp->nrport`, and I/O is allowed only when the node type and state match the expected NVMe target or initiator role. It shares SLI-4 queue, XRI, SGL, WQE, completion, and ABTS infrastructure with the SCSI/FCP side while keeping NVMe-specific statistics and completion semantics.

## Important APIs, Types, and Functions

The primary public entry points are `lpfc_nvme_create_localport`, `lpfc_nvme_destroy_localport`, `lpfc_nvme_update_localport`, `lpfc_nvme_register_port`, `lpfc_nvme_rescan_port`, `lpfc_nvme_unregister_port`, `lpfc_sli4_nvme_pci_offline_aborted`, `lpfc_sli4_nvme_xri_aborted`, `lpfc_nvme_wait_for_io_drain`, `lpfc_nvme_cancel_iocb`, `lpfc_nvme_flush_abts_list`, and `lpfc_nvmels_flush_cmd`. They are invoked from lpfc initialization, discovery, error recovery, and queue cleanup code.

The transport callback table `lpfc_nvme_template` wires the NVMe-FC host transport to local driver methods: local and remote port delete, queue create/delete, link-service request and abort, FCP I/O submit and abort, and link-service response transmit. The template also advertises hardware queue count, SGL segment limits, DMA boundary, and private data sizes for lpfc local port, remote port, and per-FCP request state.

`lpfc_nvme_create_queue` and `lpfc_nvme_delete_queue` allocate and free a small `lpfc_nvme_qhandle`, mapping NVMe queue index `qidx` to an lpfc hardware queue index. Queue zero is the admin queue and maps to hardware queue zero; I/O queues map modulo the configured maximum hardware queues. The handle also captures the CPU at creation time for diagnostics.

`__lpfc_nvme_ls_req`, `lpfc_nvme_ls_req`, `lpfc_nvme_gen_req`, `lpfc_nvme_ls_req_cmp`, `__lpfc_nvme_ls_req_cmp`, `__lpfc_nvme_ls_abort`, and `lpfc_nvme_ls_abort` implement outgoing NVMe link services. They allocate BPL DMA wrappers, build `CMD_GEN_REQUEST64_WQE` requests with NVMe FC type and ELS4 request R_CTL, hold an ndlp reference through completion, invoke the transport `done` callback, and cancel outstanding LS requests by scanning the nvmels work queue completion list.

`lpfc_nvme_handle_lsreq` handles unsolicited NVMe LS requests for the initiator personality by forwarding the payload to `nvme_fc_rcv_ls_req`; responses are sent by `lpfc_nvme_xmt_ls_rsp`, which reuses the generic response implementation from `lpfc_nvmet.c`.

The I/O submission path is `lpfc_nvme_fcp_io_submit` -> `lpfc_get_nvme_buf` -> `lpfc_nvme_prep_io_cmd` -> `lpfc_nvme_prep_io_dma` -> `lpfc_sli4_issue_wqe`. `lpfc_nvme_adj_fcp_sgls` rewrites the command and response SGEs for NVMe command IU and response IU semantics, with optional embedded command support. Completion flows through `lpfc_nvme_io_cmd_cmpl`, which decodes CQE status, reconstructs NVMe ERSP IUs when needed, reports transport status, handles exchange-busy deferral, updates congestion-management feedback, and releases the lpfc I/O buffer.

Abort handling is split between transport-requested aborts and firmware/reset-driven abort completions. `lpfc_nvme_fcp_abort` validates that the request still matches the lpfc buffer and is still on the completion queue before issuing `lpfc_sli4_issue_abort_iotag`. `lpfc_nvme_abort_fcreq_cmpl` releases the abort WQE. `lpfc_sli4_nvme_xri_aborted` and `lpfc_sli4_nvme_pci_offline_aborted` complete deferred aborted I/O and return buffers once the XRI is released.

## Control Flow

Initialization registers a local NVMe initiator port with `nvme_fc_register_localport` after filling `nvme_fc_port_info` from the vport WWNN/WWPN. The registration allocates transport-side localport storage and the lpfc private `lpfc_nvme_lport`. The driver then stores `vport->localport`, sets `vport->nvmei_support`, and clears all per-lport counters. Later FCID changes call `lpfc_nvme_update_localport` to update the localport port id and role, using discovery role when DID is zero and initiator role otherwise.

Discovery registers remote NVMe ports with `nvme_fc_register_remoteport`. `lpfc_nvme_register_port` builds `nvme_fc_port_info` from the ndlp DID, WWPN, WWNN, devloss timeout, and PRLI-derived target, initiator, or discovery capabilities. It handles reregister races by checking `ndlp->nrport`, preserving or acquiring ndlp references, clearing `NVME_XPT_UNREG_WAIT`, setting `NVME_XPT_REGD`, and rebinding the returned transport private rport to the current ndlp. Unregistration sets `NVME_XPT_UNREG_WAIT`, optionally forces devloss to zero during unload or HBA error, calls `nvme_fc_unregister_remoteport`, breaks `ndlp->nrport`, and drops the registration reference.

FCP I/O submission starts in the NVMe transport callback with localport, remoteport, queue handle, and `nvmefc_fcp_req`. The function rejects missing private data, driver unload, HBA I/O flush, missing request private area, missing ndlp, and unmapped target nodes. Keep-alive commands on admin queue can be expedited when resources are scarce. CMF read accounting can reject or time I/O. Shared ndlp queue depth is enforced unless expedited. Hardware queue selection follows either the transport queue mapping or CPU-based scheduling. A driver I/O buffer is allocated, request-private state is linked, optional VMID tags are attached, WQE and SGLs are prepared, and the WQE is issued to the selected hardware queue.

Completion reconstructs the NVMe transport view from lpfc CQEs. `CQE_CODE_NVME_ERSP` produces a synthetic `nvme_fc_ersp_iu` with command id, SQ head, SQ id, completion result, and transferred length. Plain success reports bytes placed and no response IU. `IOSTAT_FCP_RSP_ERROR` may actually be a valid NVMe ERSP of length `LPFC_NVME_ERSP_LEN`; otherwise it is logged as a protocol error. Local rejects and other errors become `NVME_SC_INTERNAL`, with PCI-offline and SLI-down tracked as offline conditions so exchange-busy handling does not defer forever. If XB is set and not offline, the buffer is put on the NVMe ABTS list rather than immediately returned.

Shutdown and error recovery are deliberately asynchronous. Localport unregister stores a stack completion in `lport->lport_unreg_cmp`, calls `nvme_fc_unregister_localport`, and waits in `lpfc_nvme_lport_unreg_wait`, periodically logging pending I/O, SCSI/NVMe ABTS buffers, and NVMe LS commands. Reset drains call `lpfc_nvme_wait_for_io_drain`, `lpfc_nvme_cancel_iocb`, `lpfc_nvme_flush_abts_list`, and `lpfc_nvmels_flush_cmd` to flush or synthesize completions.

## State and Persistence Behavior

The file maintains runtime kernel state only; there is no durable on-disk persistence. Persistent-like behavior is embodied in transport registrations, node references, queue mappings, and outstanding WQE/XRI ownership.

Important mutable state includes `vport->localport`, `vport->nvmei_support`, `ndlp->nrport`, `ndlp->fc4_xpt_flags`, `ndlp->cmd_pending`, `lpfc_nvme_lport` atomic counters, `lpfc_nvme_rport` bindings, per-request `lpfc_nvme_fcpreq_priv->nvme_buf`, I/O buffer `flags`, `nvmeCmd`, `ndlp`, hardware queue index, and ABTS lists. The code uses spinlocks on ndlp, hbalock, ring locks, and per-buffer locks to protect races between transport callbacks, completions, aborts, and driver teardown.

Reference ownership is central. Outgoing LS WQEs hold an ndlp reference until completion. Remote-port registration either reuses an existing nrport reference or takes a new ndlp reference and drops it at unregister/delete time. FCP request private data points back to the active lpfc I/O buffer only while the buffer owns the request; completion clears both directions before invoking `done` unless exchange-busy deferral requires later release.

## Dependencies and Integration Points

The file depends on Linux NVMe-FC host APIs from `<linux/nvme-fc-driver.h>` and `<linux/nvme-fc.h>`, SCSI and FC transport definitions, and lpfc internal SLI-4, discovery, logging, vport, and debugfs infrastructure. It integrates with `lpfc_init.c` for localport creation/destruction, reset cleanup, queue and buffer allocation, and firmware capability gating. It integrates with `lpfc_attr.c` for reporting counters and local/remote port state through sysfs `nvme_info`.

Shared helpers from other lpfc modules include `lpfc_sli4_issue_wqe`, `lpfc_sli_get_iocbq`, `lpfc_sli_release_iocbq`, `lpfc_get_io_buf`, `lpfc_release_io_buf`, `lpfc_get_sgl_per_hdwq`, `lpfc_ndlp_check_qdepth`, `lpfc_vmid_get_appid`, `lpfc_update_cmf_cmd`, `lpfc_update_cmf_cmpl`, `lpfc_disc_state_machine`, and SLI abort helpers. The file also calls generic LS response and abort helpers declared in `lpfc_nvme.h` and implemented in `lpfc_nvmet.c`.

## Risks and Edge Cases

The highest-risk areas are asynchronous lifetime races among nvme-fc transport unregister, ndlp deletion, abort completion, and I/O completion. The code contains explicit guards for missing private pointers, stale `ndlp->nrport`, `NVME_XPT_UNREG_WAIT`, mismatched `nvmefc_fcp_req`, requests no longer on `LPFC_IO_ON_TXCMPLQ`, HBA flush, PCI offline, and localport unload.

Queue-depth and buffer scarcity paths must preserve CMF accounting and not leak request-private backpointers. The expedited keep-alive path intentionally bypasses normal scarcity controls for admin keep-alive commands, so changes around `lpfc_get_nvme_buf` or qdepth handling should preserve that behavior.

SGL construction is sensitive to segment counts, expanded SGL links, embedded command layout, response IU length, endian conversions, and last-SGE marking. Incorrect changes can cause DMA corruption or protocol-level data mismatches. The completion path also depends on subtle interpretation of `IOSTAT_FCP_RSP_ERROR` as a valid NVMe ERSP in one case.

Exchange-busy handling defers buffer release onto ABTS lists. Any change that clears `LPFC_SBUF_XBUSY`, calls `done`, or releases buffers in a different order can create double completion, use-after-free, or XRI reuse before firmware releases the exchange.

## Test Signals

Strong runtime signals include `nvme_info` counters for LS requests/completions/errors, FCP no-XRI, bad ndlp, queue-depth, WQ errors, aborts, completion XB, and completion errors. Kernel logs with message ids in the 6000-6213 and 6310 ranges expose queue binding, LS issue/completion, I/O failures, aborts, unregister waits, and ABTS flushes. Debugfs timing and CPU-affinity checks under `CONFIG_SCSI_LPFC_DEBUG_FS` can identify queue steering and latency regressions.

Functional testing should cover localport registration/unregistration, remoteport register/unregister/reregister under devloss, discovery role rescan, admin keep-alive under low resources, read/write/control I/O, embedded and non-embedded commands, high segment counts with expanded SGLs, CMF-managed reads, VMID-tagged I/O, transport-requested aborts, firmware XRI abort completions, PCI offline cleanup, and simultaneous unload with active NVMe LS and FCP I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvme.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvme.h

## Purpose

`lpfc_nvme.h` is the shared declaration layer for lpfc NVMe initiator and NVMe target support. It pulls in the Linux NVMe, NVMe-FC driver, and NVMe-FC protocol headers, defines lpfc-specific NVMe constants, declares transport-private data structures, describes target exchange state and flags, and exposes cross-file helper prototypes shared between `lpfc_nvme.c` and `lpfc_nvmet.c`.

The header is not standalone logic, but it is the contract that keeps the initiator and target implementations synchronized around queue handles, local/remote port private data, target-port counters, per-XRI context ownership, and LS helper reuse.

## Important APIs, Types, and Constants

Initiator constants include `LPFC_NVME_DEFAULT_SEGS`, `LPFC_NVME_ERSP_LEN`, `LPFC_NVME_WAIT_TMO`, `LPFC_NVME_EXPEDITE_XRICNT`, `LPFC_NVME_FB_SHIFT`, `LPFC_NVME_MAX_FB`, and `LPFC_NVME_LS_TIMEOUT`. They define default segment advertisement, expected NVMe ERSP IU length, unregister wait logging interval, expedited XRI reserve size, first-burst encoding bounds, and link-service timeout.

Target constants include `LPFC_NVMET_DEFAULT_SEGS`, RQ posting defaults, `LPFC_NVMET_SUCCESS_LEN`, MRQ bounds, `LPFC_NVMET_WAIT_TMO`, and `LPFC_NVMET_INV_HOST_ACTIVE`. These configure target SGL advertisement, receive queue depth assumptions, successful response length, maximum multi-receive queues, targetport unregister wait time, and hosthandle invalidation state.

`lpfc_ndlp_get_nrport(ndlp)` is a small but important safety macro. It returns NULL if there is no NVMe rport binding or if `NVME_XPT_UNREG_WAIT` is set, preventing users from dereferencing transport-private remoteport state during asynchronous unregister.

`struct lpfc_nvme_qhandle` is the per-NVMe-queue opaque handle returned to the host transport. It stores the lpfc hardware queue index, the original NVMe queue index, and CPU at creation.

`struct lpfc_nvme_lport` is private data behind `nvme_fc_local_port`. It points back to `lpfc_vport`, stores the localport unregister completion, and contains atomic counters for LS requests, FCP submission failures, aborts, and completion errors.

`struct lpfc_nvme_rport` is private data behind `nvme_fc_remote_port`. It binds the remote transport object to the lpfc localport and ndlp, plus a completion for remoteport unregister flows.

`struct lpfc_nvme_fcpreq_priv` is per-FCP-request private storage used by the NVMe-FC host transport. Its single `nvme_buf` pointer links a transport request to the active lpfc I/O buffer so abort callbacks can find the WQE/XRI to abort.

`struct lpfc_nvmet_tgtport` is private data behind `nvmet_fc_target_port`. It stores the owning HBA, targetport unregister completion, invalidation state, and many atomic counters grouped by receive LS, transmit LS, receive FCP, transmit FCP, abort, and defer paths. These counters feed observability through sysfs/debug paths and are essential for diagnosing target behavior.

`struct lpfc_nvmet_ctx_info` is the per-CPU, per-MRQ context-list bucket used by the target side. It contains a context list, lock, next/start CPU pointers for replenishment, a count, and padding to reduce cache-line contention.

`struct lpfc_async_xchg_ctx` is the central target exchange context. It stores the target transport FCP request, active-list linkage, HBA, ndlp, optional LS request/response state, active and abort WQEs, a context lock, SID, OXID, payload size, MRQ index, state, flags, payload/RQ buffer pointers, owning context buffer, hardware queue, and optional debug timestamp fields. It is used for both unsolicited LS and FCP target exchanges.

The exported prototypes connect the two C files: initiator LS request, completion, and abort helpers from `lpfc_nvme.c`; target/generic unsolicited LS abort and LS response helpers from `lpfc_nvmet.c`.

## Control Flow Role

The header defines the finite-state vocabulary used by target exchange code: LS receive, LS abort, LS response, FCP receive, data, abort, done, and free. It also defines flags that can be combined independently of state: I/O in progress, abort operation issued, exchange busy, context release requested, ABTS received, RQ buffer reuse through workqueue, WQ-full deferral, and transport-notification state.

The target implementation relies on these states to validate transitions in LS response completion, FCP operation preparation and completion, release, abort, and context repost. The initiator implementation relies on the shared LS helper declarations and on initiator private structures for queue and transport object callbacks.

## State and Persistence Behavior

All data declared here represents in-kernel volatile state. No fields are persisted across driver reload or reboot. However, these structures model long-lived runtime ownership: localport and targetport private areas live as long as their transport registrations; rport private data lives as long as remoteport registration; `lpfc_async_xchg_ctx` instances are pooled and reused across target FCP exchanges; per-request private data lives across submit, abort, and completion callbacks.

Because the structures are shared across interrupt, workqueue, transport callback, discovery, and unload contexts, the lock annotations and field grouping matter. `ctxlock` protects target exchange flags, ndlp lock protects `nrport` and FC4 transport flags, and per-context-list locks protect target context pools. Atomic counters avoid broad locking for stats.

## Dependencies and Integration Points

This header directly depends on the kernel NVMe-FC APIs and lpfc internal structures declared elsewhere. It is included by `lpfc_nvme.c`, `lpfc_nvmet.c`, `lpfc_init.c`, `lpfc_attr.c`, and other lpfc modules that need NVMe state or helper prototypes. The macros and structs integrate with SLI-4 queue allocation, receive queue handling, XRI/SGL pools, debugfs timing, sysfs `nvme_info`, discovery state, and transport registration APIs.

The prototypes intentionally share LS request/response logic between initiator and target modes. That reuse means changes to LS helper signatures or `lpfc_async_xchg_ctx` fields must be coordinated across both C files and with unsolicited receive code outside this subset.

## Risks and Edge Cases

The main risk is field ownership ambiguity. `lpfc_async_xchg_ctx` is touched by interrupt handlers, worker threads, abort callbacks, transport release callbacks, and cleanup paths. Flags such as `LPFC_NVME_CTX_RLS`, `LPFC_NVME_XBUSY`, and `LPFC_NVME_ABORT_OP` determine whether a context can be recycled; incorrect interpretation can lead to use-after-free, leaks, or double release.

The `lpfc_ndlp_get_nrport` macro intentionally hides rports while unregister is pending. Bypassing it or changing `NVME_XPT_UNREG_WAIT` semantics can reintroduce stale transport object dereferences.

Stats counters are grouped by comments that name implementation functions. Adding paths without updating counters or sysfs output can make operational diagnosis misleading.

The MRQ context indexing macro assumes `phba->sli4_hba.nvmet_ctx_info` is allocated as `num_possible_cpu * cfg_nvmet_mrq` and that `cfg_nvmet_mrq` is clamped before use. Invalid MRQ sizing would corrupt context-list indexing.

## Test Signals

Compile coverage with `CONFIG_NVME_FC`, `CONFIG_NVME_TARGET_FC`, and `CONFIG_SCSI_LPFC_DEBUG_FS` is important because the header exposes fields under conditional debug usage and prototypes consumed under conditional NVMe support. Runtime signals include coherent `nvme_info` counters, correct localport/targetport registration, no stale rport lookup while unregister wait is set, balanced ndlp references on hosthandle release, and no context-list corruption under multi-CPU/MRQ target I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvmet.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvmet.c

## Purpose

`lpfc_nvmet.c` implements the target-side NVMe over Fibre Channel personality for the lpfc SLI-4 driver and also hosts generic unsolicited NVMe LS response helpers used by both target and initiator code. It registers an `nvmet_fc_target_template`, allocates per-XRI target exchange contexts, processes unsolicited NVMe FCP command IUs and LS requests, translates target transport operations into TSEND, TRECEIVE, and TRSP WQEs, handles WQ-full deferral, manages exchange-busy and ABTS cleanup, and invalidates target hosthandles during node teardown.

The code is state-machine heavy. A received target command is represented by `struct lpfc_async_xchg_ctx`, moves from receive to data/status/abort/done/free states, and may be owned at different moments by an RQ buffer, an active context list, a WQE, the nvmet-fc transport, a workqueue item, or the ABTS cleanup list.

## Important APIs, Types, and Functions

`lpfc_nvmet_cmd_template` initializes static WQE templates for target send, receive, and response operations. These templates are copied and completed in `lpfc_nvmet_prep_fcp_wqe` for `NVMET_FCOP_READDATA`, `NVMET_FCOP_READDATA_RSP`, `NVMET_FCOP_WRITEDATA`, and `NVMET_FCOP_RSP`.

Target transport callbacks are collected in `lpfc_tgttemplate`: targetport delete, LS response transmit, FCP operation transmit, FCP abort, FCP request release, deferred receive release, discovery event, target-originated LS request and abort, host release, and host address lookup. The template advertises hardware queue count, SGL limits, DMA boundary, target private size, and `NVMET_FCTGTFEAT_READDATA_RSP`.

Lifecycle functions include `lpfc_nvmet_setup_io_context`, `lpfc_nvmet_cleanup_io_context`, `lpfc_nvmet_create_targetport`, `lpfc_nvmet_update_targetport`, and `lpfc_nvmet_destroy_targetport`. Setup allocates per-CPU/per-MRQ context buckets, context buffers, reusable IOCB/WQE objects, and NVMET SGL/XRI resources. Create registers with `nvmet_fc_register_targetport`, initializes target counters, and points `phba->targetport` at the transport object. Destroy flushes WQ-full work, unregisters the targetport with a bounded wait, cleans context pools, and clears the pointer.

Receive-side functions include `lpfc_nvmet_unsol_fcp_event`, `lpfc_nvmet_unsol_fcp_buffer`, `lpfc_nvmet_replenish_context`, `lpfc_nvmet_process_rcv_fcp_req`, `lpfc_nvmet_fcp_rqst_defer_work`, `lpfc_nvmet_ctxbuf_post`, and `lpfc_nvmet_defer_rcv`. They allocate or replenish an exchange context for an unsolicited FCP frame, move it to the active list, pass payload to `nvmet_fc_rcv_fcp_req`, repost or defer RQ buffers, and recycle context buffers after transport release.

LS-side functions include `lpfc_nvmet_handle_lsreq`, `__lpfc_nvme_xmt_ls_rsp`, `__lpfc_nvme_xmt_ls_rsp_cmp`, `lpfc_nvmet_xmt_ls_rsp`, `lpfc_nvmet_xmt_ls_rsp_cmp`, `lpfc_nvmet_prep_ls_wqe`, `lpfc_nvme_unsol_ls_issue_abort`, and `lpfc_nvmet_xmt_ls_abort_cmp`. They forward received LS payloads to `nvmet_fc_rcv_ls_req`, send `CMD_XMIT_SEQUENCE64_WQE` LS responses, free receive buffers, complete transport callbacks, and abort exchanges that cannot be responded to.

FCP operation functions include `lpfc_nvmet_xmt_fcp_op`, `lpfc_nvmet_xmt_fcp_op_cmp`, and `lpfc_nvmet_prep_fcp_wqe`. They prepare WQEs, set BDEs/SGEs, issue work to hardware queues, handle WQ-full by queueing to `wqfull_list`, update transport response status, call the nvmet-fc `done` callback, and leave final recycling to `lpfc_nvmet_xmt_fcp_release`.

Abort and cleanup functions include `lpfc_nvmet_xmt_fcp_abort`, `lpfc_nvmet_rcv_unsol_abort`, `lpfc_sli4_nvmet_xri_aborted`, `lpfc_nvmet_wqfull_flush`, `lpfc_nvmet_wqfull_process`, `lpfc_nvmet_unsol_issue_abort`, `lpfc_nvmet_sol_fcp_issue_abort`, `lpfc_nvmet_unsol_fcp_issue_abort`, and their completion callbacks. They distinguish unsolicited aborts before any WQE, solicited aborts of active WQEs, firmware XRI-aborted CQEs, and transport-requested FCP aborts.

`lpfc_nvmet_invalidate_host`, `lpfc_nvmet_host_release`, and `lpfc_nvmet_host_traddr` bridge lpfc ndlp lifetime with nvmet-fc hosthandle lifetime. The driver passes ndlp as the hosthandle and uses `NLP_XPT_HAS_HH` and `LPFC_NVMET_INV_HOST_ACTIVE` to avoid reference imbalance during invalidation.

## Control Flow

Target startup first calls `lpfc_nvmet_cmd_template` during driver initialization so static TSEND/TRECEIVE/TRSP templates are available. When target mode is enabled for an HBA WWPN, `lpfc_nvmet_create_targetport` allocates NVMET context resources, fills `nvmet_fc_port_info` from pport WWNN/WWPN/DID, updates target template limits from driver configuration, registers with nvmet-fc, and initializes all target statistics.

For unsolicited FCP receive, the CQ path calls `lpfc_nvmet_unsol_fcp_event`. If target mode is disabled the RQ buffer is reposted. Otherwise `lpfc_nvmet_unsol_fcp_buffer` selects the context list for the current CPU and MRQ. If the list is empty, `lpfc_nvmet_replenish_context` steals contexts from another CPU bucket for the same MRQ. If no context is available, the frame is queued on `lpfc_nvmet_io_wait_list`, a replacement RQ buffer is posted, and `defer_ctx` is incremented. With a context, the code records SID, OXID, size, MRQ index, RQ buffer, state, and debug timestamps, adds the context to `t_active_ctx_list`, and either processes immediately or queues `defer_work` depending on CQ load.

`lpfc_nvmet_process_rcv_fcp_req` passes the command payload to `nvmet_fc_rcv_fcp_req`. A zero return means transport accepted it; the receive buffer is reposted unless ownership was already transferred by a reuse/defer path. `-EOVERFLOW` means the transport deferred freeing the receive buffer; the driver posts a replacement RQ buffer and waits for `.defer_rcv`. Other errors clear transport notification state, move the context to the deferred release/ABTS list, and issues an unsolicited FCP abort.

When the target transport asks the driver to move data or status, `lpfc_nvmet_xmt_fcp_op` rejects unload and already-aborted exchanges, prepares the WQE, sets completion and context pointers, marks I/O in progress, and issues to `ctxp->hdwq`. A full WQ queues the WQE on the queue `wqfull_list`, sets `HBA_NVMET_WQFULL`, marks `LPFC_NVME_DEFER_WQFULL`, and returns success to the transport so the operation can be retried by `lpfc_nvmet_wqfull_process` when WQE space is available. Completion updates `fcp_error`, transferred length, XBUSY state, statistics, timestamps, and calls the transport `done` callback. Final READDATA_RSP and RSP operations move state to DONE and wait for `.fcp_req_release` to recycle; intermediate data operations clear WQE command fields for reuse.

`lpfc_nvmet_xmt_fcp_release` is the normal recycle point. If an abort or XBUSY is active, it moves the context to the ABTS list with `LPFC_NVME_CTX_RLS` and lets abort/XRI completion recycle it. Otherwise it calls `lpfc_nvmet_ctxbuf_post`, which frees or reposts the RQ buffer, services any wait-list frame using the same context buffer, or returns the context buffer to the current CPU/MRQ free list.

LS receive uses a separate allocation pattern. An unsolicited LS exchange context is forwarded to `nvmet_fc_rcv_ls_req` by `lpfc_nvmet_handle_lsreq`. The transport later calls `lpfc_nvmet_xmt_ls_rsp`; the generic `__lpfc_nvme_xmt_ls_rsp` validates the LS state, prepares an XMIT_SEQUENCE WQE, issues it, frees the inbound buffer after successful issue, and completes/free the context in `__lpfc_nvme_xmt_ls_rsp_cmp`. If response issue fails, it frees the inbound buffer and sends ABTS with `lpfc_nvme_unsol_ls_issue_abort`.

Abort processing has several paths. Transport-requested `lpfc_nvmet_xmt_fcp_abort` sets `LPFC_NVME_ABORT_OP` unless the exchange is already XBUSY or aborting. If the WQE was deferred due to WQ-full, it issues an unsolicited abort and flushes the queued WQE. If the exchange is still only received, it sends an unsolicited FCP abort; otherwise it sends a solicited abort for the active WQE. Incoming ABTS (`lpfc_nvmet_rcv_unsol_abort`) first searches the ABTS list, then the wait list, then the active list, notifies the transport when needed, issues a firmware abort, and sends BA_ACC or BA_RJT. Firmware XRI-aborted CQEs (`lpfc_sli4_nvmet_xri_aborted`) clear XBUSY, possibly activate RRQ handling, notify transport of unobserved aborts, and recycle if transport already released.

## State and Persistence Behavior

The file maintains volatile kernel state only. Long-lived runtime state includes `phba->targetport`, `phba->nvmet_support`, `sli4_hba.nvmet_ctx_info`, target MRQ queues, target SGL/XRI lists, active target context list, ABTS target context list, NVMET wait list, and per-target atomic counters.

`lpfc_async_xchg_ctx` state is the core state machine. Valid flows include FREE -> RCV -> DATA -> DONE -> FREE, LS_RCV -> LS_RSP -> free, and RCV/DATA/LS states -> ABORT/DONE -> FREE. Flags capture concurrent conditions that the state alone cannot express: hardware I/O in progress, abort WQE issued, firmware exchange busy, transport release already requested, ABTS received, RQ buffer reused through workqueue, deferred WQ-full operation, and whether the transport has been notified.

Context pools are partitioned by CPU and MRQ to reduce contention, but contexts can migrate between CPU buckets. If a context is freed on a CPU different from where it was allocated, `lpfc_nvmet_ctxbuf_post` returns it to the current CPU bucket for the original MRQ. If a receive arrives while no context is available, the RQ buffer is persisted temporarily on an in-memory wait list and later consumed by the next context release.

Hosthandle state is represented by ndlp references and flags. The target transport is handed an ndlp pointer as hosthandle. `lpfc_nvmet_invalidate_host` sets target state to block new target-originated LS requests during invalidation and calls `nvmet_fc_invalidate_host` only when `NLP_XPT_HAS_HH` indicates the transport owns a hosthandle reference. `lpfc_nvmet_host_release` clears the flag, drops the ndlp reference, and clears invalidation state.

## Dependencies and Integration Points

This file depends on Linux NVMe target FC APIs (`nvmet_fc_register_targetport`, `nvmet_fc_unregister_targetport`, `nvmet_fc_rcv_ls_req`, `nvmet_fc_rcv_fcp_req`, `nvmet_fc_rcv_fcp_abort`, `nvmet_fc_invalidate_host`), Linux FC frame headers, DMA scatterlists, workqueues, and lpfc SLI-4 internals. It integrates with lpfc initialization for target-mode gating, SGL/XRI allocation, MRQ queue creation, reset cleanup, and `lpfc_nvmet_cmd_template` setup.

It shares generic LS request completion and abort helpers with the initiator file. It relies on discovery node lookup (`lpfc_findnode_did`) and node states `NLP_STE_UNMAPPED_NODE` and `NLP_STE_MAPPED_NODE` when preparing WQEs or aborts. It relies on queue code to call `lpfc_nvmet_wqfull_process` when WQE space returns and on abort/XRI worker paths to call `lpfc_sli4_nvmet_xri_aborted`.

Sysfs/debug integration is through counters in `lpfc_nvmet_tgtport`, wait-list counts in `sli4_hba`, debug timing fields under `CONFIG_SCSI_LPFC_DEBUG_FS`, and log categories `LOG_NVME`, `LOG_NVME_DISC`, `LOG_NVME_ABTS`, and `LOG_NVME_IOERR`.

## Risks and Edge Cases

The highest-risk area is context lifetime. A context may be simultaneously visible to the active list, ABTS list, transport request, WQ-full list, deferred work, and abort completion logic. The code relies on `ctxlock`, list locks, and flags to prevent double recycling. Changes to `LPFC_NVME_CTX_RLS`, `LPFC_NVME_ABORT_OP`, or `LPFC_NVME_XBUSY` handling can cause use-after-free, leaked XRIs, or missed transport completions.

Receive-buffer ownership is subtle. `LPFC_NVME_CTX_REUSE_WQ`, `rqb_buffer`, `defer_rcv`, and wait-list processing decide whether a buffer should be reposted with `lpfc_rq_buf_free`, freed by the RQ buffer provider, or retained until transport defers release. Mistakes can exhaust RQ buffers or repost the same DMA buffer twice.

WQ-full handling reports success to nvmet-fc after queueing locally. That makes flush and abort handling responsible for synthesizing completions for queued WQEs. If the queue flag or `wqfull_list` is mishandled, the transport may wait forever or receive completion after abort release.

ABTS paths must choose solicited versus unsolicited abort correctly. Before any data WQE is issued, the driver aborts by transmitting a BLS ABTS on the exchange; after a WQE is active, it issues an abort by XRI/iotag. Incoming ABTS must also check active, wait, and ABTS lists and send BA_ACC/BA_RJT consistently.

SGL and WQE preparation is DMA-sensitive. `lpfc_nvmet_prep_fcp_wqe` assumes valid scatterlists for data operations, respects max segment advertisement, embeds non-success response payloads in WQE words, uses response DMA directly for TRSP success, maintains `ctxp->offset`, and toggles exchange create/continue bits. Any off-by-one in SGE last markers, segment counts, or embedded response length can corrupt target data transfer.

Targetport teardown has a bounded wait (`LPFC_NVMET_WAIT_TMO`) while other paths may still hold contexts. Cleanup must flush WQ-full entries and context lists without deleting live work.

## Test Signals

Useful signals include target `nvme_info` counters for LS receive/drop, LS response/error/XB, FCP receive/defer/drop, read/write/response operation counts, FCP response completions/errors/aborts/XB, abort completions, unsolicited versus solicited aborts, and WQ-full/context/FOD deferrals. Wait-list depth and total wait count indicate context starvation. Logs around message ids 6023-6039, 6102-6112, 6150-6166, 6179, 6313-6325, and 6403-6425 expose lifecycle, state mismatch, abort, and resource paths.

Functional testing should exercise targetport registration/unregistration, MRQ allocation and CPU migration, unsolicited FCP receive under immediate and deferred CQ processing, no-context wait-list replenishment, transport FOD deferral, read data, write data, read-data-with-response, response-only completions, success and non-success response lengths, WQ-full queue/reissue/flush, target-originated LS requests, unsolicited LS response failure and abort, transport-requested aborts before and after WQE issue, incoming ABTS for active/waiting/ABTS-list/missing exchanges, firmware XRI-aborted CQEs, host invalidation with and without `NLP_XPT_HAS_HH`, and unload/reset while target I/O is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_nvmet.c -->
