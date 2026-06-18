# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli.c lines 17202-22829

## Scope

This chunk is the tail of the Emulex/Broadcom `lpfc_sli.c` SLI transport implementation. It begins in SLI-4 queue creation after the preceding completion queue setup and continues through mailbox-backed MQ/WQ/RQ/MRQ creation, queue destruction, SGL/XRI/RPI resource posting, unsolicited Fibre Channel receive-sequence handling, FCF discovery and failover helpers, configuration-region/object mailbox access, pending mailbox cleanup, deferred transmit-queue draining, WQE/SGL conversion and issue paths, abort-WQE construction, multi-XRI pool rebalancing, per-HDWQ auxiliary SGL and command/response buffer pools, and final common WQE preparation.

This is a chunk report only. The merged per-file report must reconcile it with earlier chunks that define shared helpers, queue primitives, mailbox issue paths, IOCB allocation, interrupt/CQE dispatch, discovery callbacks, NVMe/NVMET handlers, and the SLI-3/SLI-4 setup code that calls these routines.

## Purpose

The visible code provides the late-stage resource and datapath glue for SLI-4 operation:

- create and destroy firmware-visible MQ, WQ, RQ, and MRQ queues and bind them into driver parent/child queue lists;
- post SGL pages and RPI header pages to firmware, allocate/free logical XRI and RPI identifiers, and keep resource bitmaps/counters consistent;
- validate, assemble, abort, and deliver unsolicited FC frames to ELS/CT/NVMe/NVMET upper layers;
- build BA_ACC or BA_RJT responses for unsolicited ABTS frames and send MDS loopback frames back out;
- scan, add, rediscover, and round-robin FCF records for FCoE fabric selection and failover;
- read configuration region 23 and firmware objects, write firmware objects, and log firmware activation requirements;
- clean queued and completed discovery mailboxes when a vport needs discovery restart;
- drain deferred ELS/MDS IOCBs when SGL resources become available;
- convert BDE/BPL payload descriptions into SLI-4 SGL entries before WQE issue;
- issue WQEs to the correct SLI-4 work queue for NVMe LS, FCP/NVMe initiator I/O, CMF sync, and NVMET target work;
- manage XRI free-buffer pools across hardware queues, including private/public/expedite pools when XRI rebalancing is enabled;
- allocate, recycle, and free per-HDWQ extra SGL chunks and FCP command/response buffers;
- normalize common WQE fields before command submission.

## Important APIs, Types, and Functions

- Queue create/destroy:
  - `lpfc_mq_create()` creates a mailbox queue with `MQ_CREATE_EXT`, falls back to `MQ_CREATE` for older firmware, registers async event groups, assigns `queue_id`, `assoc_qid`, subtype, indices, and links the MQ to the parent CQ child list.
  - `lpfc_wq_create()` creates a work queue, selects create version based on firmware WQ capabilities and page size, requests DPP for version 1, validates DUA doorbell formats/offsets, maps doorbell/DPP BARs, allocates `wq->pring`, and links the WQ under its CQ.
  - `lpfc_rq_create()` creates paired header/data receive queues, with version-specific RQ context fields, DUA doorbell handling for the header queue, subtype-specific data buffer size, and child-list linkage for both queues.
  - `lpfc_mrq_create()` creates multiple NVMET receive queue pairs with a version-2 non-embedded mailbox, lays out header/data queue pages contiguously, and assigns sequential queue IDs from the returned base ID.
  - `lpfc_eq_destroy()`, `lpfc_cq_destroy()`, `lpfc_mq_destroy()`, `lpfc_wq_destroy()`, and `lpfc_rq_destroy()` issue queue-specific destroy mailboxes while SLI is active, then remove queue list links. WQ destroy also frees `wq->pring`.
- SGL/XRI/RPI resources:
  - `lpfc_sli4_post_sgl()` posts one XRI's one or two SGL pages with an embedded mailbox.
  - `lpfc_sli4_post_sgl_list()` posts a contiguous block of ELS SGLs using a non-embedded mailbox.
  - `lpfc_sli4_post_io_sgl_block()` and `lpfc_sli4_post_io_sgl_list()` post NVMe/FCP IO-buffer SGLs, grouping by contiguous XRIs and falling back to single embedded posts for isolated XRIs.
  - `lpfc_sli4_next_xritag()`, `lpfc_sli4_alloc_xri()`, and `lpfc_sli4_free_xri()` manage logical XRI allocation with `xri_bmask` and `max_cfg_param.xri_used` under `hbalock`.
  - `lpfc_sli4_post_all_rpi_hdrs()`, `lpfc_sli4_post_rpi_hdr()`, `lpfc_sli4_alloc_rpi()`, `lpfc_sli4_free_rpi()`, and `lpfc_sli4_remove_rpis()` manage RPI header posting and RPI bitmap/counter lifetime.
  - `lpfc_sli4_resume_rpi()` issues asynchronous Resume RPI mailboxes and pairs node references with the selected completion handler.
- Unsolicited receive processing:
  - `lpfc_fc_frame_check()` validates FC `r_ctl`, frame type, optional VFT header recursion, and loopback application header constraints.
  - `lpfc_fc_frame_to_vport()` maps incoming `fcfi`, VFI, and DID to a vport, with fabric DID and point-to-point exceptions.
  - `lpfc_fc_frame_add()`, `lpfc_seq_complete()`, and `lpfc_prep_seq()` assemble multi-frame FC sequences into IOCB chains for upper-layer processing.
  - `lpfc_sli4_handle_received_buffer()` is the central receive-buffer dispatcher for MDS loopback, invalid frame drop, vport lookup, ABTS handling, sequence assembly, and ULP handoff.
  - `lpfc_sli4_handle_unsol_abort()`, `lpfc_sli4_abort_partial_seq()`, `lpfc_sli4_abort_ulp_seq()`, and `lpfc_sli4_seq_abort_rsp()` clean partial/ULP-owned sequences and send BA_ACC/BA_RJT where appropriate.
  - `lpfc_sli4_handle_mds_loopback()` and `lpfc_sli4_mds_loopback_cmpl()` copy the received payload into a DMA buffer, issue `CMD_SEND_FRAME`, free resources on completion, and call `lpfc_drain_txq()`.
- FCF/config/object helpers:
  - `lpfc_sli4_add_fcf_record()` and `lpfc_mbx_cmpl_add_fcf_record()` send non-embedded ADD_FCF mailbox commands.
  - `lpfc_sli4_build_dflt_fcf_record()` constructs a default FCF record using `phba->fc_map`, default FIP/FKA values, and optional VLAN bitmap state.
  - `lpfc_sli4_fcf_scan_read_fcf_rec()`, `lpfc_sli4_fcf_rr_read_fcf_rec()`, and `lpfc_sli4_read_fcf_rec()` submit asynchronous READ_FCF commands with different completion handlers and scan/failover semantics.
  - `lpfc_sli4_fcf_rr_next_index_get()`, `lpfc_check_next_fcf_pri_level()`, `lpfc_sli4_fcf_rr_index_set()`, and `lpfc_sli4_fcf_rr_index_clear()` maintain the round-robin FCF bitmap and priority list.
  - `lpfc_sli4_redisc_fcf_table()`, `lpfc_mbx_cmpl_redisc_fcf_table()`, and `lpfc_sli4_fcf_dead_failthrough()` drive full FCF rediscovery and last-resort link-down style failover.
  - `lpfc_sli_get_config_region23()`, `lpfc_sli4_get_config_region23()`, and `lpfc_sli_read_link_ste()` read region 23 and parse TLVs to set `LINK_DISABLED`.
  - `lpfc_wr_object()` writes firmware objects in embedded mailbox BDE batches, updates the caller's offset, and logs firmware instantiation requirements through `lpfc_log_fw_write_cmpl()`.
  - `lpfc_read_object()` reads a firmware object into a caller buffer through an embedded mailbox plus an external `lpfc_mbuf` buffer.
- Mailbox/TX/WQE datapath:
  - `lpfc_cleanup_pending_mbox()` removes queued/completed REG_LOGIN64 and REG_VPI mailboxes for one vport, redirects active/completed completions to default cleanup, and marks login mailboxes for immediate unregister.
  - `lpfc_drain_txq()` tries to issue deferred ELS or MDS-loopback IOCBs from a ring TX queue, cancelling entries that fail with local reject.
  - `lpfc_wqe_bpl2sgl()` converts BPL/BDE payload descriptors into SLI-4 SGE entries and returns the SGL's XRI.
  - `lpfc_sli4_issue_wqe()` selects the target WQ path for NVMe LS, NVMe/FCP/CMF initiator IO, or NVMET target IO, places the WQE, queues it on `txcmplq`, and polls the associated EQ.
  - `lpfc_sli4_issue_abort_iotag()` builds an abort WQE for an in-flight IO, mirrors the original IO's hardware queue and protocol flags, marks `LPFC_DRIVER_ABORTED`, and submits through `lpfc_sli4_issue_wqe()`.
  - `lpfc_sli_prep_wqe()` fills common WQE fields for ELS request/response, generic request, xmit sequence, and BLS response commands, including context tags, temporary RPI, command type, request tag, CQ ID, length location, DBDE, IOD, and QoS disable fields.
- Multi-XRI and per-HDWQ buffers:
  - `lpfc_adjust_pvt_pool_count()`, `lpfc_adjust_high_watermark()`, `lpfc_move_xri_pvt_to_pbl()`, `_lpfc_move_xri_pbl_to_pvt()`, `lpfc_move_xri_pbl_to_pvt()`, and `lpfc_keep_pvt_pool_above_lowwm()` rebalance XRI-backed IO buffers between private and public pools.
  - `lpfc_release_io_buf()` returns an IO buffer to the expedite, private, public, or legacy put list after clearing protocol state and returning extra SGL/CMD-RSP buffers.
  - `lpfc_get_io_buf_from_private_pool()`, `lpfc_get_io_buf_from_expedite_pool()`, `lpfc_get_io_buf_from_multixri_pools()`, `lpfc_io_buf()`, and `lpfc_get_io_buf()` allocate IO buffers while avoiding XRIs that still need RRQ handling.
  - `lpfc_get_sgl_per_hdwq()`, `lpfc_put_sgl_per_hdwq()`, `lpfc_free_sgl_per_hdwq()`, `lpfc_get_cmd_rsp_buf_per_hdwq()`, `lpfc_put_cmd_rsp_buf_per_hdwq()`, and `lpfc_free_cmd_rsp_buf_per_hdwq()` own per-HDWQ pools for extra SGL chunks and FCP command/response DMA buffers.

Core structures touched in this chunk include `struct lpfc_hba`, `struct lpfc_queue`, `struct lpfc_sli4_hdw_queue`, `struct lpfc_sli_ring`, `struct lpfc_iocbq`, `struct lpfc_io_buf`, `struct lpfc_sglq`, `struct hbq_dmabuf`, `struct lpfc_vport`, `struct lpfc_nodelist`, `struct lpfc_multixri_pool`, `struct lpfc_pvt_pool`, `struct lpfc_pbl_pool`, `struct lpfc_epd_pool`, `struct lpfc_rpi_hdr`, `LPFC_MBOXQ_t`, `union lpfc_wqe128`, and many mailbox request/response layouts.

## Control Flow

Queue creation is mailbox-driven and mostly synchronous. Each create routine allocates a mailbox from `phba->mbox_mem_pool`, formats an SLI_CONFIG command with the correct subsystem/opcode, writes queue context and DMA page addresses from the queue's `page_list`, issues `lpfc_sli_issue_mbox(..., MBX_POLL)`, checks both mailbox return code and embedded SLI_CONFIG subheader status, then initializes software queue metadata and links the new queue to its parent CQ. Error paths free the mailbox but generally leave caller-owned queue memory for higher-level teardown. Destroy routines mirror this by issuing destroy mailboxes only when `LPFC_SLI_ACTIVE` is set, then unlinking software list nodes regardless of hardware-active status.

SGL posting flows split into single and block paths. Single-XRI posting uses `lpfc_sli4_post_sgl()` with embedded mailbox payload. Block posting computes a non-embedded request length, allocates mailbox DMA, writes SGL page pairs and a starting XRI, then issues synchronously or with a wait depending on `intr_enable`. `lpfc_sli4_post_io_sgl_list()` first groups IO buffers into contiguous XRI runs so firmware can accept block posts; holes or a final singleton are posted individually. Posted buffers have `LPFC_SBUF_NOT_POSTED` cleared and successful `IOSTAT_SUCCESS` recorded before replenishment.

Receive processing starts in `lpfc_sli4_handle_received_buffer()`. MDS diagnostics and unsolicited data loopback frames are sent to the loopback helper or freed during unload. Other frames are validated, mapped to an FCF ID from the receive CQE format, mapped to a vport by DID/VFI/FCFI, and dropped if the vport is not registered except for allowed point-to-point discovery frames. BA_ABTS frames go through abort cleanup and BA response construction. All other frames are inserted into a per-vport receive sequence list sorted by FC sequence count. Once `lpfc_seq_complete()` sees sequence count zero, no holes, and END_SEQ, `lpfc_prep_seq()` converts buffers into IOCBq entries and `lpfc_sli4_send_seq_to_ulp()` invokes the generic unsolicited IOCB handler.

The unsolicited ABTS path copies the FC header before freeing the receive buffer. Initiator-originated ABTS attempts partial sequence cleanup first, then upper-layer abort cleanup. For non-NVMET ports, `lpfc_sli4_seq_abort_rsp()` finds or creates a node for the source DID, allocates a response IOCB, marks RRQ active if the XRI is known, chooses BA_ACC or BA_RJT, fills a BLS response WQE, and issues it on the ELS ring. NVMET uses `lpfc_nvmet_rcv_unsol_abort()` instead of sending this response path.

FCF operations are asynchronous mailbox workflows. Scan and round-robin reads allocate a mailbox, call `lpfc_sli4_mbx_read_fcf_rec()`, set an operation-specific completion, and submit with `MBX_NOWAIT`; scan reads also snapshot event tags and set `FCF_TS_INPROG`. Rediscovery cancels vport retry timers, sends a rediscover mailbox, and the completion starts the rediscovery wait timer or falls back to retrying current discovery / link-down style failthrough depending on `FCF_ACVL_DISC` versus `FCF_DEAD_DISC`.

`lpfc_cleanup_pending_mbox()` is a vport discovery repair flow. Under `hbalock`, it moves queued REG_LOGIN64/REG_VPI mailboxes for the vport to a local list, adjusts the active mailbox completion and immediate-unregister flag if the active mailbox belongs to the vport, and walks pending completions to set default completions and immediate unregister on login mailboxes. Outside the lock it frees the moved mailboxes and releases node references.

WQE issue flow is protocol-flag based. NVMe LS requests allocate an ELS SGL under the NVMe LS ring lock, convert BPL/BDE to SGL entries, set the XRI in the BLS response command layout, put the WQE on the NVMe LS WQ, and queue completion tracking. FCP/NVMe/CMF initiator requests and NVMET requests use the caller-selected hardware queue's IO WQ, set the CQ map, put the WQE, queue completion tracking, and poll the associated EQ. Any unrecognized flag set returns `WQE_ERROR`.

Multi-XRI buffer allocation and release use either legacy per-HDWQ get/put lists or the rebalancing pools. The rebalancing path tries to keep private pools above a low watermark, steal batches from local or round-robin public pools, and route returned buffers to private or public based on outstanding work plus ABTS buffers against high/low watermarks and XRI limits. Expedite buffers have their own HBA-level pool and bypass normal pool selection on release.

## State and Persistence

All state in this chunk is runtime driver, DMA, or adapter state rather than persistent filesystem state:

- Queue objects persist firmware IDs (`queue_id`), parent queue association (`assoc_qid`), subtype/type, host/HBA indices, doorbell register pointers, DPP register pointers/IDs, notification intervals, and list membership under parent CQ/EQ relationships.
- Queue DMA pages in each `page_list` are zeroed before queue creation and their physical addresses are handed to firmware; child-list additions represent successful software publication of firmware queues.
- XRI state lives in `phba->sli4_hba.xri_bmask`, `xri_ids`, and `max_cfg_param.xri_used`; RPI state lives in `rpi_bmask`, `rpi_ids`, `rpi_count`, `next_rpi`, and `lpfc_rpi_rsrc_rdy`.
- Receive sequence state persists temporarily on `vport->rcv_buffer_list` with `rcv_buffer_time_stamp`, allowing timeout cleanup by `lpfc_rcv_seq_check_edtov()`.
- FCF failover state is maintained in `phba->fcf` fields such as `fcf_rr_bmask`, `fcf_pri_list`, `fcf_pri[]`, `eligible_fcf_cnt`, `current_rec`, `fcf_flag`, and FCoE event tags.
- Region 23 parsing may set `LINK_DISABLED` in `phba->hba_flag`, which changes later link bringup behavior.
- Firmware object write/read use mailbox-accessible DMA buffers. `lpfc_wr_object()` persists firmware image/object bytes to adapter firmware storage by mailbox side effect and updates the caller's transfer offset.
- Pending mailbox cleanup mutates `phba->sli.mboxq`, `sli.mbox_active`, `sli.mboxq_cmpl`, mailbox completion functions, `LPFC_MBX_IMED_UNREG`, and node reference counts.
- TX queue drain moves entries from `pring->txq` to hardware completion tracking or a local cancellation list; it also updates `pring->txq_max`.
- Multi-XRI pools persist counts and linked lists in per-HDWQ private/public pools plus the HBA expedite pool. Optional `LPFC_MXP_STAT` counters record snapshots and hit/empty statistics.
- Auxiliary SGL and command/response pool entries are DMA allocations kept on `hdwq->sgl_list`, `lpfc_buf->dma_sgl_xtra_list`, `hdwq->cmd_rsp_buf_list`, and `lpfc_buf->dma_cmd_rsp_list`.

## Dependencies and Integration Points

Kernel dependencies include DMA pool APIs, mempools, spinlocks with IRQ save/restore, Linux list primitives, bit operations, jiffies/time comparisons, work wakeups, PCI BAR mappings, endian conversion helpers, Fibre Channel frame definitions, and SCSI/NVMe/NVMET upper-layer integration through driver-local callbacks.

Internal dependencies are dense:

- mailbox formatting/issue/free helpers: `lpfc_sli4_config()`, `lpfc_sli_issue_mbox()`, `lpfc_sli_issue_mbox_wait()`, `lpfc_mbox_tmo_val()`, `lpfc_sli4_mbox_cmd_free()`, `lpfc_mbox_rsrc_cleanup()`, `lpfc_dump_mem()`, `lpfc_sli4_dump_cfg_rg23()`, `lpfc_sli4_mbx_read_fcf_rec()`;
- queue and WQE helpers from earlier in the file: `lpfc_sli4_wq_put()`, `lpfc_sli_ringtxcmpl_put()`, `lpfc_sli4_poll_eq()`, `lpfc_sli_ringtx_get()`, `__lpfc_sli_issue_iocb()`;
- IOCB/SGL helpers: `lpfc_sli_get_iocbq()`, `__lpfc_sli_get_iocbq()`, `lpfc_sli_release_iocbq()`, `__lpfc_sli_release_iocbq()`, `__lpfc_sli_get_els_sglq()`, `lpfc_sli4_get_iocb_cnt()`;
- FC discovery/node APIs: `lpfc_findnode_did()`, `lpfc_nlp_init()`, `lpfc_enqueue_node()`, `lpfc_nlp_get()`, `lpfc_nlp_put()`, `lpfc_set_rrq_active()`, `lpfc_test_rrq_active()`, `lpfc_retry_pport_discovery()`;
- upper-layer receive and abort hooks: `lpfc_complete_unsol_iocb()`, `lpfc_ct_handle_unsol_abort()`, `lpfc_nvmet_rcv_unsol_abort()`, `lpfc_nvme_unsol_ls_handler()` from nearby/earlier code;
- FCF/discovery timers and failover: `lpfc_cancel_all_vport_retry_delay_timer()`, `lpfc_fcf_redisc_wait_start_timer()`, `lpfc_unregister_unused_fcf()`, `lpfc_linkdown()`;
- buffer lifecycle helpers: `lpfc_in_buf_free()`, `lpfc_io_buf_replenish()`, `lpfc_mbuf_alloc()`, `lpfc_mbuf_free()`, `dma_pool_alloc()`, `dma_pool_zalloc()`, `dma_pool_free()`;
- bitfield macros and constants generated/defined in LPFC headers for mailbox, WQE, CQE, SGE, FC header, FCF, RPI, XRI, and queue context fields.

Externally visible functions from this chunk are used by setup, discovery, SCSI/NVMe IO submission, abort, shutdown, and debug paths elsewhere in the driver. Examples include queue create/destroy APIs, RPI/XRI allocation APIs, `lpfc_sli4_handle_received_buffer()`, FCF read/rediscovery functions, `lpfc_wr_object()`, `lpfc_read_object()`, `lpfc_cleanup_pending_mbox()`, `lpfc_drain_txq()`, IO buffer pool APIs, and `lpfc_sli_prep_wqe()`.

## Risks and Edge Cases

- Queue create paths publish partial software state late, but firmware queue IDs can be assigned before later local failures such as WQ `pring` allocation or DPP BAR mapping. Callers must destroy or recover firmware queues when create returns an error after mailbox success.
- `lpfc_mq_create()` logs unsupported MQ counts and accepts any count above 16 by falling through to a 16-entry ring size. Similar fallback behavior exists in RQ create. This is intentional but can hide a mismatch between allocated host queue pages and firmware queue depth.
- DUA/DPP paths trust firmware-returned BAR sets and doorbell offsets after limited validation. Unsupported offsets or failed BAR maps return errors after the firmware queue exists.
- Some mailbox timeout paths intentionally do not free the mailbox because completion may still arrive later. Callers and completion handling must preserve ownership discipline to avoid leaks or use-after-free.
- `lpfc_sli4_post_sgl()` logs mailbox/subheader failures but returns `0` unconditionally. Higher-level code can mark an SGL as posted even if firmware rejected the mailbox.
- Block SGL posting assumes the list order has contiguous XRIs starting at `xritag_start`. The caller groups contiguity in `lpfc_sli4_post_io_sgl_list()`, but `lpfc_sli4_post_sgl_list()` itself does not validate that invariant.
- Receive sequence assembly uses `fh_seq_id`, `fh_ox_id`, and source ID but does not explicitly compare RX_ID or DID in `lpfc_fc_frame_add()`. That may be aligned with FC sequence semantics, but malformed traffic could stress sequence coalescing.
- In `lpfc_sli4_abort_partial_seq()`, the matching sequence's data buffers are freed but the header list node is not removed and the header buffer is not freed in the visible block. That path deserves review with surrounding ownership expectations because it can leave stale receive-list state if not handled elsewhere.
- `lpfc_sli4_seq_abort_rsp()` sets `xmit_bls_rsp64_oxid` twice, first with `oxid` and then with `rxid`; the second assignment appears suspicious and could overwrite OX_ID instead of setting an RX_ID field.
- `lpfc_seq_complete()` compares `hdr->fh_seq_cnt` directly to zero for the first frame, while later comparisons use `be16_to_cpu()`. If the field is big-endian as in the FC header, this is benign for zero only but fragile if extended.
- MDS loopback requeues a CQ event to the slow-path queue if IOCB allocation fails. The same `dmabuf` must remain valid and not be double-freed while the event is retried.
- FCF priority handling drops and reacquires `hbalock` inside list iteration in `lpfc_check_next_fcf_pri_level()`. The list can change while unlocked unless callers serialize FCF list mutation elsewhere.
- Region 23 TLV parsing advances `offset` using `rgn23_data[offset + 1]` after mutating `offset` in one branch; malformed or short region data could cause out-of-bounds reads unless firmware guarantees well-formed TLVs inside `data_size`.
- `lpfc_cleanup_pending_mbox()` mutates queued, active, and completed mailbox state under `hbalock`, but frees moved mailboxes outside the lock. The local reference handling for active mailbox `ctx_ndlp` is careful, but this path is sensitive to completion races.
- `lpfc_drain_txq()` calls `__lpfc_sli_issue_iocb()` while holding `ring_lock`; the callee must obey the expected locking contract. It breaks on `IOCB_BUSY`, leaving remaining entries queued.
- `lpfc_wqe_bpl2sgl()` depends on mixed endian assumptions: BPL address fields are already byte-swapped, WQE BDE fields are not, and SGE `word2` is converted CPU-to-little after bitfield updates. Any upstream format change can corrupt SGLs.
- `lpfc_sli4_issue_wqe()` returns `WQE_BUSY` after failing to get an ELS SGL but does not enqueue the WQE; the caller must retry or defer correctly.
- `lpfc_sli4_issue_abort_iotag()` derives `struct lpfc_io_buf` with `container_of(cmdiocb, struct lpfc_io_buf, cur_iocbq)`, so it is only valid for IO IOCBs embedded in `lpfc_io_buf`.
- Multi-XRI pool rebalancing relies on accurate `count`, `txcmplq_cnt`, and ABTS counters under different locks. Counter/list mismatches can strand buffers or overrun high-watermark accounting.
- `lpfc_release_io_buf()` returns early if XRI pools were destroyed after offline, intentionally dropping the buffer from pool accounting because no useful recovery remains.
- `lpfc_get_io_buf_from_multixri_pools()` checks `if (!qp)` after taking the address of an array element, which will never be NULL for a valid index. The real risk is an out-of-range `hwqid`, which is not locally checked.
- Per-HDWQ SGL/CMD-RSP allocators drop `hdwq_lock` before `GFP_ATOMIC` allocation and reacquire it to attach the new object. Concurrent pool changes are acceptable, but the allocation is immediately attached to the requesting IO buffer rather than the shared pool.
- `lpfc_sli_prep_wqe()` assumes command-specific fields and `job->ndlp`/`cmd_dmabuf` are valid for each command. The default case dumps stack for invalid command values, which is appropriate for driver debugging but noisy under corrupted state.

## Test and Validation Signals

- Exercise queue creation and teardown on firmware supporting version-0, version-1, and version-2 queue create formats. Verify queue IDs, child-list linkage, doorbell registers, DPP enable/disable behavior, and destroy ordering.
- Fault-inject mailbox allocation, non-embedded DMA allocation, mailbox status/substatus failures, invalid firmware queue ID `0xFFFF`, BAR-map failures, and WQ `pring` allocation failures. Confirm callers unwind firmware-created queues and software lists correctly.
- Validate DUA-mode doorbell formats and offsets for WQ/RQ on adapters exposing alternate BAR sets.
- Post IO SGL lists with fully contiguous XRIs, XRI holes, exact `LPFC_NEMBED_MBOX_SGL_CNT` block sizes, final singleton entries, and large `cfg_sg_dma_buf_size` requiring second SGL pages. Confirm `LPFC_SBUF_NOT_POSTED` and replenishment state match firmware success/failure.
- Test `lpfc_sli4_post_sgl()` failure handling specifically, because the function currently returns success even after logging mailbox failure.
- Run receive-path tests for single-frame ELS/CT/NVMe, multi-frame ordered sequences, out-of-order sequence count insertion, missing END_SEQ, sequence holes, invalid R_CTL/type drops, VFT-tagged frames, loopback application-header validation, and receive sequence EDTOV cleanup.
- Inject BA_ABTS for partial driver-owned sequences, upper-layer-owned CT sequences, responder-originated aborts, unknown XRIs, and NVMET-enabled ports. Verify BA_ACC/BA_RJT fields, RRQ state, node references, and buffer cleanup.
- Validate MDS loopback with normal command completion, IOCB allocation failure/requeue, DMA allocation failure, and issue failure.
- Test FCF scan/read/round-robin with empty priority lists, single priority entries, all FLOGI-failed entries, invalid FCF indexes, rediscover mailbox failure, ACVL and DEAD FCF rediscovery flags, and event-tag changes during scans.
- Feed region 23 parser with valid disabled/enabled TLVs, non-Linux driver TLVs, last-record markers, bad signatures, bad versions, zero-length data, and boundary-length records.
- Exercise firmware object write/read with exact page multiples, short final page, mailbox timeout, invalid object name, empty object with EOF, and too-small caller buffers.
- During discovery restart, queue active and completed REG_LOGIN64/REG_VPI mailboxes for one vport and unrelated mailboxes for others. Verify only matching entries are cleaned, node refs are released once, and immediate unregister flags are applied.
- Populate ELS and MDS TX queues with issuable, busy, and failing IOCBs. Confirm `lpfc_drain_txq()` leaves busy entries queued, cancels hard failures with `IOSTAT_LOCAL_REJECT/IOERR_SLI_ABORTED`, and updates `txq_max`.
- Validate WQE issue for NVMe LS, FCP, NVMe, CMF, and NVMET paths, including EQ polling, tx completion queue insertion, CQ ID selection, SGL conversion, and `WQE_BUSY` retry behavior.
- Test abort-WQE submission for link-up, link-down, external-loopback, FCP/NVMe/FOF original commands, and invalid non-IO IOCB inputs.
- Stress multi-XRI pools under high queue count with XRI rebalancing on and off. Watch private/public/expedite counts, low/high watermark adjustments, round-robin public-pool stealing, RRQ-active skip behavior, and stats under `LPFC_MXP_STAT`.
- Verify per-HDWQ extra SGL and command/response buffer pools under allocation failure, return with empty per-IO lists, final pool free, and concurrent get/put pressure.
- Confirm `lpfc_sli_prep_wqe()` fills expected context tags and temporary RPI fields for FLOGI, SCR, RDF, EDC, RSCN, FDISC, LOGO, QFPA, UVEM, PLOGI, loop topology ELS responses, generic requests, xmit sequences, and BLS responses.
