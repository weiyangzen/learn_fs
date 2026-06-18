# Research: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005296`: lines 1-8785, `Docs/researches/chunks/subset-b-005296_research.md`
- `subset-b-005297`: lines 8786-17201, `Docs/researches/chunks/subset-b-005297_research.md`
- `subset-b-005298`: lines 17202-22829, `Docs/researches/chunks/subset-b-005298_research.md`

## Chunk Research

### subset-b-005296: lines 1-8785

# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli.c lines 1-8785

## Scope

This chunk covers the first 8,785 lines of `lpfc_sli.c`, the low-level SLI transport/control layer for the Broadcom/Emulex LPFC Fibre Channel host driver. It includes common SLI queue primitives, IOCB/SGL/RRQ lifecycle helpers, SLI-2/3 ring handling, SLI-4 mailbox/resource setup, reset/restart paths, receive-buffer provisioning, RAS firmware-log setup, congestion-management setup, RX monitor ring helpers, and the beginning of `lpfc_sli4_hba_setup()`. The chunk ends while `lpfc_sli4_hba_setup()` is still in progress, immediately after starting resource-identifier allocation error handling, so later chunks must reconcile the rest of SLI-4 HBA setup and teardown.

## Purpose

The code in this range is the adapter-facing core that turns driver work objects into hardware queue entries and turns hardware completions back into LPFC upper-layer callbacks. It bridges Linux kernel SCSI/FC/NVMe-FC code to SLI firmware concepts: WQ/MQ/RQ/EQ/CQ entries for SLI-4, IOCB command/response rings for SLI-2/3, mailbox commands for control-plane operations, and DMA buffers/SGLs/RPIs/VPIs/XRIs/VFIs used by FCP, ELS, NVMe, NVMET, discovery, and congestion-management flows.

## Important APIs, Types, and Functions

- `lpfc_iocb_type` classifies IOCB completions as solicited, unsolicited, abort, or unknown. `lpfc_sli_iocb_cmd_type()` maps many firmware IOCB opcodes into this classification and is central to response dispatch.
- Global WQE templates `lpfc_iread_cmd_template`, `lpfc_iwrite_cmd_template`, and `lpfc_icmnd_cmd_template` are initialized by `lpfc_wqe_cmd_template()` with invariant FCP read/write/command WQE fields. Later I/O paths fill variable BDE, transfer length, tags, context, and request fields.
- SLI-4 queue primitives include `lpfc_sli4_wq_put()`, `lpfc_sli4_mq_put()`, `lpfc_sli4_eq_get()`, `lpfc_sli4_cq_get()`, `lpfc_sli4_rq_put()`, and the corresponding release/doorbell helpers. They maintain host/HBA indexes, valid-bit toggling, notify intervals, queue statistics, and IF_TYPE_6/DPP/list/ring doorbell formatting.
- `lpfc_sli4_write_eq_db()`, `lpfc_sli4_if6_write_eq_db()`, `lpfc_sli4_write_cq_db()`, and `lpfc_sli4_if6_write_cq_db()` abstract completion/event queue rearming and release notification. INTx paths do a readback flush when rearming.
- IOCB allocation and release are handled by `__lpfc_sli_get_iocbq()`, `lpfc_sli_get_iocbq()`, `__lpfc_sli_release_iocbq_s3()`, `__lpfc_sli_release_iocbq_s4()`, and `lpfc_sli_release_iocbq()`. SLI-4 release also returns SGL/XRI state to the correct free, abort, or NVMET list.
- RRQ management is in `lpfc_set_rrq_active()`, `lpfc_handle_rrq_active()`, `lpfc_get_active_rrq()`, `lpfc_cleanup_vports_rrqs()`, `lpfc_test_rrq_active()`, and `lpfc_clr_rrq_active()`. It uses per-node XRI bitmaps, a global active RRQ list, RATOV timers, and mempool objects to decide when to send or clear RRQs.
- SLI-3 ring helpers include `lpfc_sli_next_iocb_slot()`, `lpfc_sli_submit_iocb()`, `lpfc_sli_update_ring()`, `lpfc_sli_update_full_ring()`, and `lpfc_sli_resume_iocb()`. These copy IOCBs to SLIM ring memory, update put/get indexes, and request ring-available interrupts when full.
- Receive-buffer provisioning spans legacy HBQs and SLI-4 RQs: `lpfc_sli_hbq_setup()`, `lpfc_sli_hbqbuf_fill_hbqs()`, `lpfc_sli_hbq_to_firmware_s3()`, `lpfc_sli_hbq_to_firmware_s4()`, `lpfc_sli_free_hbq()`, `lpfc_sli4_rb_setup()`, and `lpfc_post_rq_buffer()`.
- Mailbox completion handling is centered on `lpfc_sli_handle_mb_event()`, `lpfc_sli_def_mbox_cmpl()`, `lpfc_sli_wake_mbox_wait()`, and `lpfc_sli4_unreg_rpi_cmpl_clr()`. `lpfc_sli_chk_mbx_command()` validates completed mailbox opcodes and treats unknown completions as fatal.
- IOCB completion dispatch includes `lpfc_sli_handle_fast_ring_event()` for the SLI-3 FCP ring, `lpfc_sli_handle_slow_ring_event_s3()` for non-FCP SLI-3 rings, `lpfc_sli_handle_slow_ring_event_s4()` for SLI-4 slow-path queued CQ events, and `lpfc_sli_sp_handle_rspiocb()` for common slow-path response processing.
- Unsolicited frame handling is implemented by `lpfc_sli_process_unsol_iocb()`, `lpfc_complete_unsol_iocb()`, `lpfc_sli_prep_unsol_wqe()`, and `lpfc_nvme_unsol_ls_handler()`. These map received buffers, reconstruct multi-IOCB continuations, choose vports, synthesize WQE/WCQE fields, and hand work to ELS/CT/NVMe/NVMET handlers.
- Adapter reset/setup APIs include `lpfc_sli_brdready_s3()`, `lpfc_sli_brdready_s4()`, `lpfc_sli_brdkill()`, `lpfc_sli_brdreset()`, `lpfc_sli4_brdreset()`, `lpfc_sli_brdrestart_s3()`, `lpfc_sli_brdrestart_s4()`, `lpfc_sli_chipset_init()`, `lpfc_sli_config_port()`, `lpfc_sli_hba_setup()`, and the beginning of `lpfc_sli4_hba_setup()`.
- SLI-4 resource extent functions include `lpfc_sli4_get_avail_extnt_rsrc()`, `lpfc_sli4_chk_avail_extnt_rsrc()`, `lpfc_sli4_cfg_post_extnts()`, `lpfc_sli4_alloc_extent()`, `lpfc_sli4_dealloc_extent()`, `lpfc_sli4_alloc_resource_identifiers()`, `lpfc_sli4_dealloc_resource_identifiers()`, and `lpfc_sli4_get_allocated_extnts()`.
- Firmware and diagnostic features are configured through `lpfc_set_features()`, `lpfc_sli4_read_fcoe_params()`, `lpfc_sli4_read_rev()`, `lpfc_sli4_get_ctl_attr()`, `lpfc_sli4_retrieve_pport_name()`, `lpfc_sli4_ras_fwlog_init()`, `lpfc_sli4_ras_setup()`, `lpfc_read_lds_params()`, `lpfc_config_cgn_signal()`, and `lpfc_cmf_setup()`.
- RX monitor helpers `lpfc_rx_monitor_create_ring()`, `lpfc_rx_monitor_destroy_ring()`, `lpfc_rx_monitor_record()`, and `lpfc_rx_monitor_report()` provide a lock-protected circular buffer for congestion/CMF receive statistics.

## Control Flow

Normal command submission on SLI-3 starts with a queued `lpfc_iocbq` on a ring `txq`. `lpfc_sli_resume_iocb()` checks link state and ring gating, gets a free command slot with `lpfc_sli_next_iocb_slot()`, removes work via `lpfc_sli_ringtx_get()`, and posts it with `lpfc_sli_submit_iocb()`. Submission sets the iotag when a completion callback exists, copies the IOCB to PCI/SLIM memory, records the command on `txcmplq` or immediately releases it, advances `cmdidx`, and writes the host command put index. When the ring is full, `lpfc_sli_update_full_ring()` sets `LPFC_CALL_RING_AVAILABLE` and requests a ring-available attention.

SLI-4 submission uses WQ/MQ/RQ helpers instead of IOCB rings. `lpfc_sli4_wq_put()` checks queue fullness using `host_index` and `hba_index`, sets periodic completion notification, optionally writes through a DPP aperture, enforces ordering with `wmb()`, advances the host index, then writes a list-format or ring-format doorbell. `lpfc_sli4_mq_put()` posts mailbox queue entries and records `phba->mbox` for completion. `lpfc_sli4_rq_put()` posts matched header/data RQEs to paired HRQ/DRQ queues and rings a receive queue doorbell on the notify interval.

Fast SLI-3 FCP completions enter `lpfc_sli_handle_fast_ring_event()`. The handler validates response ring indexes, serializes with `fcp_ring_in_use`, copies each response IOCB, classifies it, logs resource pressure and errors, looks up solicited commands by iotag, invokes command completions outside the lock, or calls unsolicited processing. It advances `rspGetInx`, handles response-ring-full attentions, and resumes command posting when command entries become available.

Slow-path completions enter either `lpfc_sli_handle_slow_ring_event_s3()` or `lpfc_sli_handle_slow_ring_event_s4()`. SLI-3 copies response IOCBs from the response ring into driver-owned `lpfc_iocbq` objects before calling `lpfc_sli_sp_handle_rspiocb()`. SLI-4 drains `sp_queue_event`, translates WQE completions through `lpfc_sli4_els_preprocess_rspiocbq()`, and forwards receive CQEs to `lpfc_sli4_handle_received_buffer()`. `lpfc_sli_sp_handle_rspiocb()` classifies the response, dispatches solicited completions, unsolicited frames, abort completions, or adapter messages, then releases chained response IOCBs unless ownership moved upward.

Unsolicited receive handling first resolves DMA buffers from HBQ tags, tagged buffers, or ring-posted physical addresses. Continuation IOCBs are chained by OXID until the final sequence arrives. The code derives R_CTL and type, applies an ELS firmware workaround for missing R_CTL on the ELS ring, chooses an NPIV vport when present, prepares SLI-4-compatible WQE/WCQE metadata, then routes to NVMe LS handling, profile callback, or R_CTL/type-specific ring callback. NVMe LS validates FC header fields, driver state, local/target port availability, and logged-in source node before handing the exchange to NVMe host or target transport code.

Mailbox completions are accumulated by interrupt-side code into `sli.mboxq_cmpl`; `lpfc_sli_handle_mb_event()` splices that list locally, validates the mailbox opcode, retries `MBXERR_NO_RESOURCES`, logs the completion, and invokes the mailbox callback. Default completion cleanup includes special handling for successful `REG_LOGIN64` after node teardown, `REG_VPI`, `UNREG_LOGIN`, `RESUME_RPI`, `INIT_LINK` security failures, and SLI-4 config mailbox memory.

Initialization and reset flows are layered. Legacy `lpfc_sli_hba_setup()` configures SLI-2/3 ports by issuing `CONFIG_PORT`, mapping rings, allocating VPI maps when NPIV is present, setting up HBQs, enabling link-attention processing, and calling post-config discovery setup. SLI-4 `lpfc_sli4_hba_setup()` begins by resetting the PCI function, checking port status, marking SLI active, reading revision/VPD, setting FCoE/FIP flags, setting host time, reading FCoE config region 23, retrieving port/controller attributes, parsing VPD, enabling selected features, requesting firmware features, enabling SLI-3-compatible flags, enabling dual dump, and then starting resource-identifier allocation. The rest of this function is outside this chunk.

## State and Persistence Behavior

This code is stateful across the `lpfc_hba`, `lpfc_sli`, `lpfc_sli4_hba`, vport, nodelist, ring, and queue structures. Important persistent fields include queue indexes and valid-bit polarity, ring `cmdidx`/`rspidx`/`local_getidx`, `txq`/`txcmplq` counts, `iocbq_lookup`, SGL active/free/abort lists, RRQ active lists and bitmaps, HBQ/RQ buffer lists and counts, mailbox active/completion queues, HBA flags, link state, VPD revision fields, feature flags, and resource identifier bitmaps/ID arrays.

Hardware-visible state is updated through coherent DMA memory, PCI/SLIM memory copies, MMIO doorbells, host group indexes, and mailbox command buffers. The code uses `wmb()`, `rmb()`, `mb()`, readback flushes, and lock transitions to keep host writes, device valid bits, and doorbells ordered. Persistent firmware-facing resource state includes allocated extents for RPI/VPI/XRI/VFI, posted SGLs, posted receive buffers, congestion buffer registration, and RAS firmware-log DMA buffers.

Timers and deferred work persist asynchronous state: RRQs wait for `fc_ratov + 1` before sending or clearing, ELS completions arm `els_tmofunc`, error attention polling maintains interrupt-rate statistics and requeues itself, idle-stat polling is scheduled for MSIX non-NVMET cases, and CMF synchronization uses counters and interval state to report congestion telemetry.

## Dependencies and Integration Points

This chunk depends on Linux kernel PCI, DMA, timer, spinlock, list, mempool, DMI, SCSI, Fibre Channel, and NVMe-FC infrastructure. It uses LPFC hardware definitions and bitfield helpers from `lpfc_hw*.h`, queue and SLI definitions from `lpfc_sli*.h`, discovery/node APIs from `lpfc_disc.h` and `lpfc_crtn.h`, SCSI/NVMe helpers from `lpfc_scsi.h` and `lpfc_nvme.h`, vport helpers, debugfs trace hooks, and logging categories from `lpfc_logmsg.h`.

Upper-layer integration happens through callback pointers on `lpfc_iocbq`, mailbox completion callbacks, ring receive profile callbacks, NVMe host/target LS handlers, discovery ELS handlers, fabric abort helpers, queue-depth rampdown callbacks, and worker wakeups. Lower-layer integration is direct MMIO/PCI interaction with doorbell registers, host attention/chip attention registers, host status/control registers, mailbox SLIM/MQ memory, and device reset functions.

## Risks and Edge Cases

- Queue index corruption is treated as fatal in several paths. Bad response put indexes or HBQ get indexes move the adapter to `LPFC_HBA_ERROR`, set error-attention work, and wake or call the error handler.
- SLI-4 valid-bit processing is barrier-sensitive. The explicit `mb()` after EQE/CQE valid checks is there to prevent speculative reads from acting on stale hardware data.
- Locking differs by generation and path: SLI-3 often uses `hbalock`, while SLI-4 ring paths may use `ring_lock` plus `hbalock` and `sgl_list_lock`. Mistakes can race queue/list ownership, especially around `txcmplq`, SGL active-list entries, and RRQ bitmaps.
- Resource release depends on exchange state. SLI-4 ELS/NVMe/NVMET SGLs may go to free, NVMET, or ABTS lists depending on `LPFC_EXCHANGE_BUSY`, PCI offline state, and `SGL_XRI_ABORTED`. Premature release can reuse an XRI while firmware still owns it.
- Mailbox completions are security and lifecycle sensitive. Unknown mailbox commands force HBA error; `MBXERR_NO_RESOURCES` is retried; default cleanup may issue an unregister login from inside a registration completion; node references must match mailbox lifecycle.
- Receive-buffer handling has multiple fallback formats. HBQ tag lookup failures, continuation IOCB ordering, bad NVMe LS headers, missing local/target ports, or absent logged-in nodes lead to buffer recycling and sometimes unsolicited LS aborts.
- Reset and restart paths deliberately disable interrupts/error attention, change PCI command bits, issue kill/restart/reset sequences, and clear major driver state. These paths must not run concurrently with live queue use except through the intended HBA-down/error recovery coordination.
- SLI-4 resource extent allocation assumes firmware-provided counts/sizes and allocates multiple bitmaps and ID arrays. Partial allocation failures must unwind in exact reverse order; extent reprovisioning after reset deallocates all extent types if any count/size changed.
- `lpfc_sli4_get_allocated_extnts()` contains an embedded/non-embedded sizing branch where `req_len` is initialized to `emb_len`, making the `if (req_len > emb_len)` path unreachable in this chunk. That may be intentional placeholder logic or a latent issue to compare with later code/history.
- RX monitor reporting uses `strlen()`/`strlcat()` inside a loop under a spinlock; large buffers or many entries can add lock hold time, though reads are capped by `max_read_entries`.
- This chunk ends mid-initialization. Error unwind and completion of `lpfc_sli4_hba_setup()` must be verified in the next chunk before judging whole-function safety.

## Test Signals and Validation Hooks

- Queue primitive tests should exercise WQ/MQ/RQ full and wraparound behavior, valid-bit toggling with `eqav`/`cqav`, notify interval doorbells, IF_TYPE_6 doorbells, DPP-enabled WQ posting, and INTx readback flushes.
- Completion-path validation should cover SLI-3 fast FCP completions, slow ELS completions, abort completions, unknown IOCB commands, resource-error queue-depth rampdown, adapter messages, continuation unsolicited IOCBs, and `LPFC_DRIVER_ABORTED`/`LPFC_EXCHANGE_BUSY` state translation.
- Mailbox tests should cover success, unknown command, `MBXERR_NO_RESOURCES` retry, `REG_LOGIN64` cleanup/unregister, `UNREG_LOGIN` deferred PLOGI, wait completion wakeup, SLI-4 config mailbox cleanup, and `INIT_LINK` security denial logging.
- Receive-buffer tests should include HBQ and SLI-4 RQ posting, buffer tag lookup, missing buffer handling, buffer recycle after upper-layer rejection, NVMe LS validation failures, target and initiator NVMe LS dispatch, and vport selection with NPIV VPIs.
- Reset/setup validation should inspect HBA flags and link state after board ready, board kill, SLI-3 reset/restart, SLI-4 PCI function reset, chipset init timeout/error paths, and HBA-down flushing.
- Resource tests should cover extent-supported and non-extent resource provisioning, extent size/count change across reset, allocation failure unwinds, deallocation flag clearing, and SGL reposting with contiguous and non-contiguous XRI lists.
- Feature/config tests should watch log IDs for READ_REV, FCoE parameter reads, controller attribute retrieval, port name retrieval, feature mismatch, dual dump, MI/CMF enablement, congestion signal fallback to FPIN-only, LDS parameter read completion, and RAS firmware-log mailbox failures.
- Runtime observability comes from LPFC log categories (`LOG_SLI`, `LOG_MBOX`, `LOG_INIT`, `LOG_TRACE_EVENT`, `LOG_CGN_MGMT`, `LOG_NVME_DISC`, `LOG_LDS_EVENT`), debugfs slow-ring/discovery traces, queue statistics counters, `slistat`, HBQ/RQ buffer counts, CMF/RX monitor reports, and HBA flag/link-state transitions.

## Cross-Chunk Follow-Up

The merge lane must combine this with later `lpfc_sli.c` chunks to finish `lpfc_sli4_hba_setup()`, SLI-4 interrupt/CQE handlers, WQE issue paths, abort/XRI completion handling, queue creation/destruction, and any later definitions referenced here such as `lpfc_sli4_post_sgl_list()`, `lpfc_sli4_issue_wqe()`, `lpfc_sli4_handle_received_buffer()`, `lpfc_sli4_els_preprocess_rspiocbq()`, and the rest of SLI-4 HBA setup error unwinding.

### subset-b-005297: lines 8786-17201

# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli.c lines 8786-17201

## Scope

This chunk covers the middle SLI layer of the LPFC Fibre Channel driver. It starts in the latter half of `lpfc_sli4_hba_setup()` and continues through mailbox issue paths, IOCB/WQE submission, abort and shutdown paths, error-attention and interrupt handling, SLI4 CQ/EQ processing, queue polling, queue memory allocation, and the beginning of SLI4 queue creation helpers through the opening of `lpfc_rq_create()`.

## Purpose

The code bridges three major responsibilities:

- Bring an SLI4 HBA from resource discovery into an operational queue-backed state.
- Serialize mailbox commands and IOCB/WQE submissions across SLI3 and SLI4 hardware models.
- Convert hardware interrupts and completion queue entries into driver work, upper-layer completions, receive-buffer processing, and recovery events.

The chunk is compatibility-heavy. Many public wrappers dispatch through function pointers configured for LPFC PCI device groups, so common discovery, ELS, CT, FCP, and management paths can call one API while SLI3 uses IOCB rings and SLI4 uses EQ/CQ/WQ/MQ/RQ queues.

## Important APIs and functions

- `lpfc_sli4_hba_setup()` tail: reads service parameters, creates and sets up SLI4 queues, posts ELS/NVMET/IO SGLs, initializes IOCB lists and receive buffers, registers FCFI/MRQ state, starts timers, arms interrupts, initializes CMF, optionally initializes/down-links the port, enables RAS firmware logging, and sets `HBA_SETUP`.
- Mailbox timeout and issue path:
  - `lpfc_mbox_timeout()` posts `WORKER_MBOX_TMO` and wakes the worker.
  - `lpfc_sli4_mbox_completions_pending()` and `lpfc_sli4_process_missed_mbox_completions()` inspect the mailbox CQ/EQ to avoid false timeouts caused by missed interrupts.
  - `lpfc_mbox_timeout_handler()` marks mailbox timeout state, clears SLI active state, sets link unknown, and resets the HBA.
  - `lpfc_sli_issue_mbox_s3()`, `lpfc_sli4_post_sync_mbox()`, `lpfc_sli_issue_mbox_s4()`, and `lpfc_sli4_post_async_mbox()` implement SLI3 SLIM/host mailbox flow, SLI4 bootstrap synchronous mailbox flow, SLI4 interrupt-mode enqueue, and worker-posted MQ submission.
  - `lpfc_sli_issue_mbox()` dispatches through `phba->lpfc_sli_issue_mbox`.
- API table setup:
  - `lpfc_mbox_api_table_setup()` selects SLI3 or SLI4 mailbox and board helper implementations.
  - `lpfc_sli_api_table_setup()` selects SLI3 or SLI4 IOCB/WQE issue, release, and command-preparation functions.
- IOCB/WQE submission:
  - `__lpfc_sli_ringtx_put()` and `lpfc_sli_next_iocb()` manage pending transmit queues.
  - `__lpfc_sli_issue_iocb_s3()` posts IOCBs to SLI3 rings or queues them when busy.
  - `__lpfc_sli_issue_fcp_io_s4()` prepares embedded FCP I/O and calls `lpfc_sli4_issue_wqe()`.
  - `__lpfc_sli_issue_iocb_s4()` selects ELS or FCP WQ, obtains or reuses SGL/XRI state, writes WQE fields, posts to WQ, and records the command on `txcmplq`.
  - `lpfc_sli_issue_iocb()` is the public wrapper, preparing WQEs for SLI4, taking the right ring lock, and polling EQs if needed.
- Command preparation:
  - `lpfc_sli_prep_els_req_rsp()`, `lpfc_sli_prep_gen_req()`, `lpfc_sli_prep_xmit_seq64()`, and `lpfc_sli_prep_abort_xri()` dispatch to SLI3 IOCB builders or SLI4 WQE builders.
  - SLI4 builders set request tags, class, context tags, command codes, ELS IDs, CT/RPI mode, VMID/app-id hints, CQ IDs, and abort criteria.
- Shutdown, abort, and synchronous wait:
  - `lpfc_sli_mbox_sys_flush()`, `lpfc_sli_mbox_sys_shutdown()`, `lpfc_sli_host_down()`, and `lpfc_sli_hba_down()` drain mailbox queues, outstanding mailbox commands, IOCB tx queues, ELS buffers, and timers.
  - `lpfc_sli_issue_abort_iotag()`, `lpfc_sli_hba_iocb_abort()`, `lpfc_sli_abort_iocb()`, and `lpfc_sli_abort_taskmgmt()` issue ABTS/close-exchange work for outstanding commands.
  - `lpfc_sli_issue_iocb_wait()` and `lpfc_sli_issue_mbox_wait()` provide sleeping synchronous wrappers over asynchronous completions.
- Interrupt and completion handling:
  - `lpfc_sli_check_eratt()`, `lpfc_sli_eratt_read()`, and `lpfc_sli4_eratt_read()` detect error attention conditions and record work status.
  - `lpfc_sli_sp_intr_handler()`, `lpfc_sli_fp_intr_handler()`, and `lpfc_sli_intr_handler()` process SLI3 slow/fast/device-level interrupts.
  - `lpfc_sli4_hba_intr_handler()`, `lpfc_sli4_hba_intr_handler_th()`, and `lpfc_sli4_intr_handler()` process SLI4 EQ-driven interrupt paths.
  - `__lpfc_sli4_process_cq()`, `__lpfc_sli4_sp_process_cq()`, and `__lpfc_sli4_hba_process_cq()` claim CQs, process bounded CQEs, ring doorbells periodically, and reschedule under heavy load.
  - CQE dispatchers handle MCQE mailbox/async events, ELS WCQEs, WQ release events, XRI abort events, normal RQ events, NVMET RQ events, and FCP completions.
- Queue memory and creation:
  - `lpfc_sli4_queue_alloc()` allocates queue objects and DMA-coherent pages, initializes work items and list heads.
  - `lpfc_sli4_queue_free()` releases DMA pages, RQ buffers, and queue list membership.
  - `lpfc_modify_hba_eq_delay()` tunes EQ interrupt coalescing through EQ delay registers or mailbox commands.
  - `lpfc_eq_create()`, `lpfc_cq_create()`, `lpfc_cq_create_set()`, `lpfc_mq_create()`, and `lpfc_wq_create()` construct mailbox payloads for hardware queue creation and link queues into parent/child topology.
  - `lpfc_rq_create()` begins at the end of this chunk.

## Important types and state

- `struct lpfc_hba`: central adapter state. This chunk updates `link_state`, `hba_flag`, `bit_flags`, `work_ha`, `work_hs`, `work_status`, `last_completion_time`, `data_flags`, `poll_list`, `mbox_mem_pool`, `wq`, and many `sli4_hba` members.
- `struct lpfc_sli`: shared SLI state, especially `sli_flag`, `mbox_active`, `mboxq`, `mboxq_cmpl`, `iocbq_lookup`, `last_iotag`, and ring state.
- `struct lpfc_sli4_hba`: queue hierarchy and SLI4 capability/state container. Relevant fields include `hdwq`, `hba_eq_hdl`, `mbx_cq`, `mbx_wq`, `els_wq`, `nvmels_wq`, `hdr_rq`, `dat_rq`, `nvmet_mrq_hdr`, `nvmet_mrq_data`, `nvmet_cqset`, `lpfc_wq_list`, `cq_lookup`, `cq_max`, `pc_sli4_params`, queue doorbell callbacks, abort/asynce work queues, RAS state, and SGL/XRI counts.
- `struct lpfc_queue`: represents EQ/CQ/MQ/WQ/RQ memory and runtime state: queue IDs, type/subtype, parent/child lists, DMA pages, producer/consumer indices, notification limits, CPU/channel affinity, `queue_claimed`, `q_flag`, doorbell addresses, DPP state, and per-queue counters.
- `struct lpfc_iocbq`: the common command object used for both SLI3 IOCBs and SLI4 WQEs. This chunk uses `iocb`, `wqe`, `wcqe_cmpl`, `cq_event`, `iotag`, `cmd_flag`, `cmd_cmpl`, `wait_cmd_cmpl`, `rsp_iocb`, `context_un`, `sli4_xritag`, `sli4_lxritag`, `hba_wqidx`, `io_buf`, `vport`, and `ndlp`.
- `LPFC_MBOXQ_t`: mailbox command object. This chunk uses mailbox command/status fields, SLI4 MQE fields, MCQE copy-out, extension buffers, `mbox_cmpl`, `mbox_flag`, `ctx_buf`, `ctx_ndlp`, `ctx_u.mbox_wait`, and `vport`.
- Queue and completion structures include `struct lpfc_cqe`, `struct lpfc_mcqe`, `struct lpfc_wcqe_complete`, `struct lpfc_wcqe_release`, `struct sli4_wcqe_xri_aborted`, `struct lpfc_rcqe`, and mailbox create payloads such as `lpfc_mbx_eq_create`, `lpfc_mbx_cq_create`, `lpfc_mbx_cq_create_set`, `lpfc_mbx_mq_create_ext`, and `lpfc_mbx_wq_create`.

## Control flow

### SLI4 HBA setup tail

The setup path reads host and port identity, creates host-side queues, sets queues up on the device, initializes SLI ring/queue bookkeeping, updates and posts SGL lists, initializes IOCB resources, creates NVMET target state when configured, posts RPI headers, registers FCFI/MRQ state, allocates IO buffers, unblocks async mailbox posting, posts receive buffers, starts watchdog/heartbeat/error timers, arms CQ/EQ interrupts, enables interrupt mode, initializes CMF, optionally issues `DOWN_LINK` or `INIT_LINK`, frees the setup mailbox, enables RAS logging, and sets `HBA_SETUP`. Error exits unwind in reverse order through IO buffer free, queue unset, IOCB list free, queue destroy, timer stop, and mailbox free.

### Mailbox serialization

Only one mailbox is active at a time. SLI3 tracks `LPFC_SLI_MBOX_ACTIVE`, optionally queues new commands on `sli.mboxq`, copies mailbox payloads to host SLIM or host mailbox memory, rings `CA_MBATT`, and either polls for completion or waits for interrupt completion. SLI4 has two modes:

- Before interrupts are enabled, polling uses the bootstrap mailbox region. It waits for the BMBX ready bit, writes high and low DMA addresses, copies the MQE and MCQE result back, and clears `mbox_active`.
- After interrupts are enabled, synchronous polling temporarily blocks async mailbox posting with `LPFC_SLI_ASYNC_MBX_BLK`; asynchronous callers enqueue on `sli.mboxq`, and the worker uses `lpfc_sli4_post_async_mbox()` to move one command to `mbx_wq`, set `mbox_active`, arm the timeout, and post the MQE.

Mailbox completions in SLI4 are consumed from MCQEs. Heartbeat completions are handled inline; other completions move to `mboxq_cmpl`, set `HA_MBATT`, release the MQ entry if consumed, clear active state, and wake the worker to process completion callbacks and post the next mailbox.

### IOCB/WQE issue

SLI3 issue validates HBA state, link state, deferred error state, and ring blocking flags. It drains `txq` opportunistically into available command ring slots, updates ring doorbells, and queues or returns busy when no slot is available.

SLI4 issue uses WQs. FCP I/O is sent through the hardware queue selected by `hba_wqidx`; ELS and other slow-path commands use the ELS WQ. Commands without an XRI obtain an ELS SGL/XRI unless they are aborts; continuations reuse active SGL state. The WQE gets XRI tags and SGL mapping, is posted with `lpfc_sli4_wq_put()`, and then the command is placed on the ring `txcmplq` so completion lookup by request tag can find it.

### Abort and teardown

Host and HBA teardown drain pending tx queues and issue aborts for commands already on completion queues. Abort paths avoid aborting abort commands and avoid double-aborting `LPFC_DRIVER_ABORTED` commands. SLI4 abort WQEs must go to the same WQ as the original command, so abort IOCBs inherit `hba_wqidx` and set `LPFC_USE_FCPWQIDX` for FCP. The IA bit is selected based on unload, link-down, SLI4 link status, and loopback state. If abort submission fails, the original command's driver-aborted mark is cleared and the abort IOCB is released.

Synchronous wait wrappers replace the caller's completion with a wake completion, sleep on a wait queue or completion object, and on timeout mark the command so a late completion either calls the saved fallback completion or leaves resource ownership with the timed-out path.

### Error attention and interrupts

SLI3 uses HA/HC/HS registers. Slow-path interrupts handle link attention, mailbox attention, and ELS ring attention by disabling relevant interrupts, copying mailbox results, queuing work, and waking the worker. Fast-path interrupts process FCP and optional extra rings directly.

SLI4 uses EQs and CQs. The top-level SLI4 interrupt path iterates configured IRQ channels. Each EQ handler checks device state, optionally switches to threaded IRQ processing, updates interrupt counters and EQ delay state, calls `lpfc_sli4_process_eq()`, and rearms or reports spurious interrupts. EQEs map to CQs through fast `cq_lookup`, NVMET CQ sets, NVME-LS CQ, or slow-path child-list lookup.

CQ processing uses `queue_claimed` to serialize concurrent interrupt/poll/work processing. It processes up to `max_proc_limit`, writes CQ doorbells every `notify_interval`, records load flags such as `HBA_EQ_DELAY_CHK` and `HBA_NVMET_CQ_NOTIFY`, defers rearm under high load, and reschedules delayed work when polling is preferable to immediate re-interrupt.

### CQE dispatch

- MCQE: copies and endian-converts mailbox CQE, then dispatches mailbox completion or async event.
- ELS WCQE: allocates a pseudo response IOCBQ, queues it to `sp_queue_event`, and sets `HBA_SP_QUEUE_EVT`.
- FCP WCQE: looks up the command by request tag, copies WCQE completion into the command, updates exchange-busy state, optionally ramps down queue depth on no-resource local rejects, and calls the command completion.
- Release WCQE: releases WQ entries against ELS WQ or matching fast-path child WQ.
- XRI aborted WCQE: handles IO XRI aborts immediately, notifies NVME/NVMET where needed, or queues ELS/NVME-LS abort events to worker context.
- RQ RCQE: releases RQ entries, obtains posted receive buffers, queues unsolicited frames to slow-path work, special-cases MDS loopback frames, and records insufficient-buffer or DMA-failure counters.
- NVMET RCQE: maps CQ ID to MRQ index, validates FCP command frame control bits, and dispatches unsolicited NVMET FCP commands.

### Queue creation

Queue allocation creates `struct lpfc_queue` plus DMA-coherent pages sized to adapter page capabilities, initializes queue lists and work items, and records entries per page. Queue creation helpers use mailbox commands to create hardware queues and then link software objects into parent/child lists:

- EQs become interrupt event roots and record `queue_id`, notify interval, and max processing limit.
- CQs bind to EQs, support queue-create version/counter variants, update `cq_lookup` maximum tracking, and store type/subtype.
- CQ sets create multiple CQs for NVMET MRQ in one non-embedded mailbox, binding each CQ to its matching hardware queue EQ and assigning IDs from a returned base ID.
- MQs bind mailbox queue memory to a CQ. The code tries `MQ_CREATE_EXT` with async event groups and falls back to legacy `MQ_CREATE`.
- WQs bind work queues to CQs, select WQ create version based on adapter capabilities and WQE/page size, optionally request DPP, map doorbell/DPP BARs, validate doorbell format and offsets, allocate the associated `lpfc_sli_ring`, and add the WQ under the parent CQ.

## State and persistence behavior

This is kernel driver runtime state, not durable on-disk state. Persistent behavior is limited to in-memory adapter state that survives across events until reset/unload:

- `phba->sli.sli_flag` gates mailbox activity, async mailbox blocking, SLI active state, EQ delay register use, and link-attention processing.
- `phba->sli.mbox_active`, `sli.mboxq`, and `sli.mboxq_cmpl` persist mailbox ownership across interrupt, worker, timeout, and shutdown contexts.
- `phba->link_state`, `sli4_hba.link_state.status`, `hba_flag`, `bit_flags`, `work_ha`, `work_hs`, and `work_status` persist link/error/recovery state until worker/reset paths consume them.
- IOCB/WQE objects persist in `txq`, `txcmplq`, and `iocbq_lookup` until completion, abort, cancellation, or teardown.
- Queue IDs, parent/child queue lists, CQ lookup entries, doorbell register addresses, DPP mappings, and DMA pages persist for the lifetime of queue setup.
- Timers and work items persist as asynchronous control-plane mechanisms: mailbox timeout, heartbeat, ELS timeout, error polling, EQ delay work, idle-stat heartbeat, and CPU-hotplug polling.
- Receive buffer counters and queue counters persist operational telemetry for support and adaptive behavior.

## Dependencies and integration points

- Linux kernel primitives: spin locks, IRQ handlers, timers, workqueues, delayed work, RCU lists, completions, wait queues, mempools, DMA coherent allocation, PCI channel state, BAR/ioremap helpers, per-CPU counters, `jiffies`, and memory barriers.
- SCSI/Fibre Channel midlayer integration: `Scsi_Host`, `fc_host_node_name`, `fc_host_port_name`, `fc_host_post_vendor_event`, `scsilun_to_int`, FCP command structures, and FC frame headers.
- LPFC subsystems outside this chunk:
  - Queue primitives such as `lpfc_sli4_qe`, `lpfc_sli4_wq_put`, `lpfc_sli4_mq_put`, `lpfc_sli4_rq_release`, EQ/CQ doorbell writers, and queue setup/destroy helpers.
  - Mailbox builders and helpers such as `lpfc_sli4_config`, `lpfc_read_sparam`, `lpfc_set_host_data`, `lpfc_reg_fcfi`, `lpfc_reg_fcfi_mrq`, `lpfc_down_link`, `lpfc_unreg_login`, and `lpfc_mbox_*`.
  - Discovery, ELS, CT, and node management callbacks such as `lpfc_els_unsol_event`, `lpfc_ct_unsol_event`, `lpfc_mbx_cmpl_dflt_rpi`, `lpfc_cleanup_discovery_resources`, `lpfc_find_vport_by_vpid`, `lpfc_findnode_rpi`, and node refcount helpers.
  - FCP/NVME/NVMET paths such as `lpfc_sli_prep_wqe`, `lpfc_sli4_issue_wqe`, `lpfc_new_io_buf`, `lpfc_io_free`, `lpfc_nvmet_unsol_fcp_event`, `lpfc_nvmet_wqfull_process`, and NVMET XRI-abort hooks.
  - Recovery and monitoring helpers such as `lpfc_reset_hba`, `lpfc_issue_hb_tmo`, `lpfc_fabric_abort_hba`, `lpfc_hba_down_prep`, `lpfc_sli_abts_recover_port`, `lpfc_worker_wake_up`, CMF setup, RAS setup, and EQ delay modulation.
- Hardware/firmware contracts: SLI3 HA/HC/HS/SLIM registers, SLI4 bootstrap mailbox, MQ/CQ/EQ/WQ/RQ mailbox opcodes, CQE code formats, WQE field encodings, XRI/RPI/VPI/FCFI identifiers, queue autovalid support, DPP/DUA modes, and adapter page-size/count capabilities.

## Risks and edge cases

- Mailbox ownership races are central. Timeout handling, missed-completion scanning, interrupt completion, shutdown flush, and synchronous waits all touch `mbox_active` and `LPFC_SLI_MBOX_ACTIVE`; lock ordering and token release must remain exact.
- SLI4 synchronous mailbox while interrupts are enabled blocks async posting. If `LPFC_SLI_ASYNC_MBX_BLK` is not cleared on all failure paths, mailbox progress can stall.
- Late IOCB completions after `lpfc_sli_issue_iocb_wait()` timeout rely on `LPFC_IO_WAKE_TMO`, saved `wait_cmd_cmpl`, and ownership comments. Callers must not free timed-out IOCBs contrary to the documented contract.
- SLI4 aborts must use the same WQ as the original command. Incorrect `hba_wqidx`, missing `LPFC_USE_FCPWQIDX`, or wrong CQ ID can lead to ineffective aborts or leaked node references.
- Queue creation has many hardware capability branches. Unsupported entry counts are sometimes downgraded to the smallest valid count unless below a minimum; this can hide configuration mismatch unless logs are watched.
- CQ processing intentionally allows concurrent interrupt and poll/work attempts and depends on `queue_claimed` plus doorbell rearm semantics. Incorrect mode switching can cause missed completions or interrupt storms.
- `cq_lookup` fast mapping depends on valid queue IDs and `cq_max`. Missing lookup entries fall back only for known NVMET/NVME-LS or slow-path child-list cases.
- Receive path error handling must keep RQ release and buffer accounting balanced. DMA-failure and insufficient-buffer cases update counters and may repost later via worker flags.
- DPP and DUA WQ creation depends on BAR mappings and firmware-returned doorbell formats/offsets. Unsupported doorbell metadata returns errors after firmware queue creation may already have partially succeeded.
- Shutdown paths disable softirqs around lock-protected mailbox/IOCB flushes; incorrect use in future changes can deadlock with timer contexts.
- Many paths call completions while not holding locks after moving objects between lists. Callback ownership and object lifetime must be respected by all callers.

## Test and validation signals

Useful validation signals for this chunk include:

- HBA bring-up reaches `HBA_SETUP`, creates EQ/CQ/MQ/WQ/RQ hierarchy, posts SGL/RPI/RQ resources, arms interrupts, and starts heartbeat/error timers without unwinding logs such as queue allocation/setup failures.
- Mailbox tests cover SLI4 pre-interrupt `MBX_POLL`, interrupt-mode async enqueue/post/completion, synchronous mailbox while async queue is blocked, mailbox timeout, missed mailbox completion, and shutdown flush.
- IOCB/WQE tests cover ELS, CT generic request, xmit sequence, FCP I/O, embedded FCP command mode, VMID/app-id tagging, SGL exhaustion/queueing, and continuation commands that reuse active SGL state.
- Abort tests cover ELS abort, FCP abort by LUN/target/host, task-management aborts, link-down IA close behavior, loopback behavior, already-aborted commands, and abort submission failure cleanup.
- Interrupt tests cover SLI3 combined and MSI-X slow/fast handlers, SLI4 EQ-to-CQ dispatch, threaded IRQ mode, polling mode transitions, no-EQE/spurious interrupt logs, CQ load rescheduling, and EQ delay modulation.
- Completion tests cover MCQE mailbox completion, async events, ELS pseudo response creation, FCP request-tag lookup, release WCQEs, XRI-aborted events, normal RQ receive, NVMET MRQ receive, MDS loopback frames, DMA-failure RCQEs, and insufficient-buffer RCQEs.
- Queue creation tests should exercise adapter variants for queue create versions, CQ autovalid, EQ autovalid, MQ create fallback, WQ 64-byte and 128-byte entries, page-size capability branches, DPP enabled/disabled paths, DUA mode, and invalid queue counts.
- Runtime counters/logs that indicate health include `slistat.mbox_cmd`, `slistat.mbox_busy`, `slistat.sli_intr`, per-CQ `CQ_*` counters, per-RQ buffer counters, EQ no-entry counters, `last_completion_time`, `WORKER_MBOX_TMO` clearing, and absence of lookup-miss logs for command completions.

## Chunk-local open questions for merge lane

- The full `lpfc_sli4_hba_setup()` prologue and `lpfc_rq_create()` body are outside this chunk, so final synthesis should connect setup prerequisites and receive-queue mailbox details from adjacent chunks.
- Queue destroy/unset functions are outside this range; final risk analysis should compare create-time partial-failure behavior with destroy-time cleanup.
- Some helper behavior is inferred from names and usage, including SGL update/repost helpers, WQE preparation, and queue doorbell implementations; adjacent chunks should confirm exact side effects.

### subset-b-005298: lines 17202-22829

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
