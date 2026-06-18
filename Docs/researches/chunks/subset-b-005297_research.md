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
