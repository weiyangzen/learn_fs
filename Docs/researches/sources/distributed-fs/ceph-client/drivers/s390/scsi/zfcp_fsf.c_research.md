# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_fsf.c`

## Purpose

`zfcp_fsf.c` implements Fibre Channel Support Function command handling for zfcp. It creates, queues, completes, and frees FSF requests; interprets FSF protocol/status responses; handles unsolicited status-read events; implements adapter/port/LUN open/close/exchange commands for ERP; sends CT/ELS commands for FC services and BSG; sends SCSI FCP commands, aborts, and task-management commands; and ties request completion back into QDIO, ERP, diagnostics, debug tracing, and SCSI completion.

## Important APIs And Functions

- Request lifetime:
  - `zfcp_fsf_req_create()` allocates `struct zfcp_fsf_req` and QTCB, initializes request id/sequence/type/header, and starts QDIO request layout.
  - `zfcp_fsf_req_send()` adds to `adapter->req_list`, timestamps, queues through QDIO, increments sequence/request ids, and enforces the async "do not touch after send" rule.
  - `zfcp_fsf_req_complete()` handles status-read special cases, deletes timers, evaluates protocol/FSF status, invokes the command handler, notifies ERP, and either frees or completes the request.
  - `zfcp_fsf_req_free()` releases request/QTCB memory via mempool or kmem cache.
  - `zfcp_fsf_req_dismiss_all()` dismisses all outstanding requests after QDIO shutdown.
  - `zfcp_fsf_reqid_check()` maps returned response SBAL request ids to requests and panics on unknown ids.
- Status-read:
  - `zfcp_fsf_status_read()` posts an unsolicited status-read buffer.
  - `zfcp_fsf_status_read_handler()` handles port-closed, incoming ELS, bit-error threshold, link down/up, notification lost, feature update alert, and version change, then refills status-read work.
  - `zfcp_fsf_fc_host_link_down()` resets FC host/link metadata.
- Status evaluation:
  - `zfcp_fsf_protstatus_eval()` handles QTCB version, sequence, duplicate id, link down, queue reestablish, and unsupported protocol statuses.
  - `zfcp_fsf_fsfstatus_eval()` and `zfcp_fsf_fsfstatus_qual_eval()` interpret high-level FSF statuses and recommendations.
  - `zfcp_fsf_link_down_info_eval()` logs link-down reasons, blocks rports, clears FC host data, and marks adapter failed.
- Exchange commands:
  - `zfcp_fsf_exchange_config_data()` / `_sync()` and handler update adapter features, topology, diagnostic config data, SCSI host data, QTCB version compatibility, and link-down incomplete state.
  - `zfcp_fsf_exchange_port_data()` / `_sync()` and handler update diagnostic port data, SCSI host port data, and FC Endpoint Security algorithms.
- CT/ELS:
  - `zfcp_fsf_send_ct()` and `zfcp_fsf_send_els()` build request/response SBALs, start timers, trace SAN payloads, and call CT/ELS completion handlers.
  - `zfcp_fsf_setup_ct_els_sbals()` supports unchained, chained, and multi-buffer data-router layouts.
- Open/close:
  - `zfcp_fsf_open_port()`, `close_port()`, `close_physical_port()`, `open_lun()`, and `close_lun()` are ERP-owned async commands with handlers that mutate port/LUN handles and status.
  - `zfcp_fsf_open_wka_port()` and `close_wka_port()` support FC generic-service WKA port lifecycle and wake WKA wait queues.
- SCSI I/O and error handling:
  - `zfcp_fsf_fcp_cmnd()` creates and sends FCP I/O commands from `struct scsi_cmnd`, including DIF/DIX protection SGs.
  - `zfcp_fsf_fcp_cmnd_handler()` evaluates FSF/FCP status, sets SCSI result/sense/errors, records latency and blktrace data, emits SCSI debug, clears host_scribble, and calls `scsi_done()`.
  - `zfcp_fsf_abort_fcp_cmnd()` sends abort for an old FSF request id from `host_scribble`.
  - `zfcp_fsf_fcp_task_mgmt()` sends TMF commands and `zfcp_fsf_fcp_task_mgmt_handler()` marks TM failure.
- Miscellaneous:
  - `zfcp_fsf_convert_portspeed()` maps FSF speed bits to FC transport speed bits.
  - `zfcp_fsf_scnprint_fc_security()` formats FC Endpoint Security flags.

## Control Flow

All active FSF commands follow a common pattern: lock QDIO request queue, wait for/free an SBAL, create request/QTCB, fill command-specific QTCB bottom and SBAL entries, set a handler/timer/status bits, send through QDIO, and then never dereference async requests after send. QDIO response interrupts call `zfcp_fsf_reqid_check()`, which removes each request from `adapter->req_list` and completes it. Completion first classifies transport/protocol status, then command-specific FSF status, then calls the handler. ERP-owned requests notify their ERP action so the ERP thread can continue.

Status-read buffers are special requests with no QTCB. They return unsolicited events from firmware and are freed/refilled continuously. Link and notification events often trigger FC event posting, port scans, rport blocking, adapter reopen, or version-change work.

SCSI commands are asynchronous cleanup requests. On completion, the handler holds `adapter->abort_lock` until after `scsi_done()` to prevent abort/completion races. For synchronous exchange commands, the caller waits on `req->completion`, checks request status, then frees the request.

## State And Persistence

FSF persists state in adapter fields (`req_no`, `fsf_req_seq_no`, feature flags, hardware versions, topology/peer info, status-read counters, FC security algorithms), port fields (handles, open/physical-open/access/security state), SCSI-device fields (LUN handle, latency counters), request-list membership, and diagnostic buffers. Request objects themselves are temporary but their ids are used as the durable correlation token between QDIO SBALs, SCSI `host_scribble`, ERP action `fsf_req_id`, and debug traces.

## Dependencies And Integration

The file integrates with QDIO for queueing/SBAL layout, ERP for recovery and timers, zfcp request list for completion lookup, FC for CT/ELS and incoming ELS handling, diagnostics for xconfig/xport caches, SCSI transport for host/rport/link updates, SCSI mid-layer for command completion, block layer for blktrace driver data, and debug feature tracing for HBA/SAN/SCSI records.

## Risks And Edge Cases

- Unknown request ids in `zfcp_fsf_reqid_check()` trigger a kernel panic because they imply possible memory corruption.
- Request lifetime is highly race-sensitive. Async requests may complete and be freed immediately after QDIO submission; code after send must not touch them.
- `zfcp_fsf_req_send()` removes requests on QDIO send failure by id and logs if already gone; this protects against unexpected list races.
- Incomplete exchange-config/port data is not fatal but must mark diagnostics incomplete and link down while still allowing later link-up events.
- FSF status handling mixes recoverable, retryable, fatal, and informational statuses. Incorrect classification can either cause needless adapter shutdowns or miss required recovery.
- CT/ELS chained SBAL layout depends on hardware features and data-router state; mismatch can cause `FSF_SBAL_MISMATCH` or unsupported operation.
- SCSI command `host_scribble` stores the FSF request id cast through pointer-sized storage; build-time size assertion protects this.
- Protection/DIF directions and SG layout must match hardware expectations or data integrity errors are reported.
- `zfcp_fsf_req_trace()` updates latency only when measurement data is supported and request succeeded; tests must not assume latency on every command.

## Test Signals

Important validation signals include:

- Every FSF command sets correct QTCB command/type, port/lun handles, data direction, and SBAL flags.
- Status-read events trigger expected actions: link down blocks rports and marks adapter failed; link up reopens adapter; notification lost triggers scan/work; bit-error threshold optionally shuts down.
- Synchronous exchange functions return `0`, `-EIO`, `-EAGAIN`, `-ENOMEM`, or `-EOPNOTSUPP` according to request and incomplete status.
- ERP-owned requests notify ERP exactly once and clear `fsf_req_id` on send failure/dismissal.
- SCSI FCP completion sets SCSI status/sense/residual/DID codes correctly and calls `scsi_done()` under abort-lock protection.
- Abort and TMF paths distinguish succeeded, not-needed, transport error, and task-management failure states.
- FC security changes generate debug/log messages only when old and new representations differ.
