# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_qdio.c`

## Purpose

`zfcp_qdio.c` implements setup, open/close, interrupt processing, accounting, SBAL allocation, scatterlist mapping, send, and teardown for the zfcp QDIO transport queues. It is the lower transport layer between FSF request objects and the s390 QDIO/CIO hardware interface.

## Important APIs And Functions

- Module parameter `datarouter` (`enable_multibuffer`) requests hardware data-router/multi-buffer support.
- Error and accounting:
  - `zfcp_qdio_handler_error()` converts QDIO errors into SIOSL logging, adapter shutdown, or adapter reopen.
  - `zfcp_qdio_zero_sbals()` clears queue buffers after completion or rollback.
  - `zfcp_qdio_account()` accumulates request-queue utilization over TOD-clock time.
- Interrupt/tasklet processing:
  - `zfcp_qdio_int_req()` handles request queue errors.
  - `zfcp_qdio_request_tasklet()` inspects output queue completions, frees SBALs, updates accounting, wakes waiters, and arms a rescan timer.
  - `zfcp_qdio_request_timer()` schedules request completion scanning.
  - `zfcp_qdio_int_resp()` processes input/response queue completions, logs multi-buffer default errors, calls `zfcp_fsf_reqid_check()` for each returned SBAL, and reposts input buffers.
  - `zfcp_qdio_irq_tasklet()` polls input queue and restarts QDIO interrupts.
  - `zfcp_qdio_poll()` schedules IRQ tasklet from QDIO polling.
- SBAL helpers:
  - `zfcp_qdio_sbals_from_sg()` maps a scatterlist into chained SBAL/SBALE entries and rolls back on exhaustion.
  - `zfcp_qdio_sbal_get()` waits up to five seconds for a free request SBAL while holding/releasing `req_q_lock`.
  - `zfcp_qdio_send()` submits prepared SBALs to the output queue and updates queue indices/free count.
- Lifecycle:
  - `zfcp_qdio_setup()` allocates and initializes `struct zfcp_qdio`, queues, locks, tasklets, and timer.
  - `zfcp_qdio_open()` establishes QDIO, reads SSQD capabilities, configures data division/multi-buffer flags, posts response buffers, enables tasklets, and updates SCSI host queue limits.
  - `zfcp_qdio_close()` clears QDIOUP under the request lock, wakes waiters, disables tasklets/timers/IRQs, shuts down QDIO, clears used outbound SBALs, and resets free count.
  - `zfcp_qdio_destroy()` kills tasklets, frees QDIO structures and buffers.
  - `zfcp_qdio_shost_update()` sets SCSI host SG table size and max sectors from QDIO limits.
  - `zfcp_qdio_siosl()` triggers hardware logging once per shutdown cycle.

## Control Flow

FSF callers hold `qdio->req_q_lock`, get an SBAL, initialize a `zfcp_qdio_req`, fill QTCB/data SG entries, and call `zfcp_qdio_send()`. Send accounts current queue fill, subtracts used SBALs, calls `qdio_add_bufs_to_output_queue()`, rolls back on failure, schedules request-completion scanning when the queue is low or arms a timer otherwise, and advances the request queue index.

On response interrupts, the IRQ tasklet inspects the input queue and `zfcp_qdio_int_resp()` calls FSF request-id completion for each returned SBAL, then reposts the buffers. On output/request completion, the request tasklet inspects the output queue, zeros completed SBALs, adds them back to `req_q_free`, and wakes waiters.

Errors from QDIO usually reopen the adapter. Severe SLSB-state errors trigger SIOSL and adapter shutdown. Response errors under multi-buffer mode also collect returned SBAL pointers for debug tracing before recovery.

## State And Persistence

The persistent per-adapter QDIO state lives in `struct zfcp_qdio`: request/response queue buffer arrays, current request index, atomic free count, utilization counters, full counter, wait queue, tasklets, timer, adapter pointer, and per-request element limits. Adapter status bits track QDIOUP, SIOSL issued, data division enabled, and multi-buffer active.

## Dependencies And Integration

The file depends on Linux tasklets, timers, lockdep, QDIO/CIO APIs, s390 SSQD descriptors, zfcp ERP for recovery, zfcp FSF for request completion, zfcp debug feature for default error traces, and SCSI host update through adapter fields.

## Risks And Edge Cases

- Request queue lock and IRQ-disabled context requirements are strict. `zfcp_qdio_send()` asserts IRQs disabled because accounting is protected differently from tasklet context.
- `zfcp_qdio_sbal_get()` can sleep while using `wait_event_interruptible_lock_irq_timeout`; callers must be in process context.
- If output queue completion stalls, SBAL wait timeout increments `req_q_full` and triggers adapter reopen.
- `zfcp_qdio_sbals_from_sg()` must roll back partially filled chained SBALs on exhaustion; missed zeroing would corrupt later requests.
- Closing clears QDIOUP before shutdown so no new output buffers are submitted during `qdio_shutdown()`.
- Unknown or failed response queue reposting triggers adapter reopen; response buffers must be reposted reliably to keep status reads flowing.
- Multi-buffer limits affect SCSI host `sg_tablesize`; bad capability detection can cause overlarge I/O requests.

## Test Signals

Useful signals include:

- QDIO open detects data-division and multi-buffer capabilities and sets adapter status/limits accordingly.
- Request queue free count, index, and zeroed SBALs remain consistent across send, output completion, send failure, and close.
- Scatterlists spanning multiple pages/SBALs map correctly and fail cleanly when exceeding request limits.
- Response queue completion calls FSF request-id checking for each returned SBAL and reposts buffers.
- QDIO error injection triggers expected adapter reopen/shutdown and SIOSL only once.
- SCSI host limits update after QDIO open.
