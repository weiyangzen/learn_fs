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
