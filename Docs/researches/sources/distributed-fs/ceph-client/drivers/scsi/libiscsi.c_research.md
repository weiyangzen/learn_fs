# sources/distributed-fs/ceph-client/drivers/scsi/libiscsi.c

## Purpose

`libiscsi.c` is the transport-independent iSCSI initiator library used by software and partial-offload iSCSI low-level drivers. It owns SCSI command queueing, iSCSI task allocation, CmdSN/StatSN bookkeeping, management PDU dispatch, PDU completion, timeout handling, SCSI error-handler integration, session/connection lifecycle, and sysfs parameter plumbing. Transport drivers provide the `struct iscsi_transport` callbacks for PDU allocation, task initialization, transmit, cleanup, optional ITT parsing, and protection checking.

## Important APIs, Types, and Functions

Exported queueing and PDU helpers include `iscsi_queuecommand()`, `iscsi_conn_send_pdu()`, `iscsi_complete_pdu()`, `__iscsi_complete_pdu()`, `iscsi_complete_scsi_task()`, `iscsi_prep_data_out_pdu()`, `iscsi_requeue_task()`, `iscsi_verify_itt()`, `iscsi_itt_to_task()`, and `iscsi_itt_to_ctask()`. Host/session/connection lifecycle is provided by `iscsi_host_alloc()`, `iscsi_host_add()`, `iscsi_host_remove()`, `iscsi_host_free()`, `iscsi_session_setup()`, `iscsi_session_remove()`, `iscsi_session_free()`, `iscsi_session_teardown()`, `iscsi_conn_setup()`, `iscsi_conn_bind()`, `iscsi_conn_start()`, `iscsi_conn_stop()`, `iscsi_conn_unbind()`, and `iscsi_conn_teardown()`.

Error-handling APIs include `iscsi_eh_cmd_timed_out()`, `iscsi_eh_abort()`, `iscsi_eh_device_reset()`, `iscsi_eh_recover_target()`, `iscsi_eh_session_reset()`, `iscsi_session_failure()`, `iscsi_conn_failure()`, and `iscsi_session_recovery_timedout()`. Parameter APIs include `iscsi_set_param()`, `iscsi_session_get_param()`, `iscsi_conn_get_param()`, `iscsi_conn_get_addr_param()`, `iscsi_host_get_param()`, `iscsi_host_set_param()`, and `iscsi_switch_str_param()`.

The main runtime state is in `struct iscsi_host`, `struct iscsi_session`, `struct iscsi_conn`, `struct iscsi_task`, `struct iscsi_pool`, `struct iscsi_cmd`, and protocol headers from `iscsi_proto.h`. Session state values such as `ISCSI_STATE_LOGGED_IN`, `ISCSI_STATE_IN_RECOVERY`, `ISCSI_STATE_FAILED`, `ISCSI_STATE_RECOVERY_FAILED`, and `ISCSI_STATE_TERMINATE` gate queueing and recovery. Task states include free, pending, running, completed, requeued to SCSI, and aborted variants.

## Control Flow

Normal I/O starts at `iscsi_queuecommand()`. It validates class-session readiness, session state, leading connection presence, TX suspension, and CmdSN window space under `frwd_lock`. A task is pulled from the session `cmdpool` FIFO, attached to `iscsi_cmd(sc)->task`, and either transmitted immediately or queued on `conn->cmdqueue` for `iscsi_xmitworker()`. `iscsi_prep_scsi_cmd_pdu()` builds the SCSI Command PDU, including LUN, CDB or extended CDB AHS, immediate data length, unsolicited R2T state, read/write flags, transfer length, CmdSN, and transport-specific task initialization. The transmit worker prioritizes saved partial tasks, management PDUs, requeued Data-Out work, then new commands.

Receive-side completion enters `iscsi_complete_pdu()` or `__iscsi_complete_pdu()` under `back_lock`. It verifies ITT age/index, handles reserved-ITT async/NOP/reject PDUs, dispatches SCSI responses and Data-In status to `iscsi_scsi_cmd_rsp()` or `iscsi_data_in_rsp()`, forwards login/text/logout/async payloads to the iSCSI transport class via `iscsi_recv_pdu()`, and completes management/TMF tasks. CmdSN and ExpStatSN are updated from target responses, sense data is copied for CHECK CONDITION, residuals are checked, and task refs are released through `iscsi_complete_task()` and `iscsi_free_task()`.

Management PDUs are built by `iscsi_alloc_mgmt_task()` and sent through `iscsi_send_mgmt_task()`. Login and Text reuse a preallocated connection login task; other management tasks come from the command pool and require logged-in state. NOP-Outs serve both target-requested replies and initiator pings. Reject handling can resend target-triggered NOP-Outs or complete a rejected ping while treating unsupported or malformed reject payloads as protocol errors.

Error handling is serialized by `eh_mutex`. Command timeout handling first checks whether the task or older commands have made progress, then uses NOP-Out pings to distinguish slow I/O from dead transport before allowing SCSI EH escalation. Abort and reset paths issue immediate TMF PDUs, wait on `ehwait` with a timer, and interpret `TMF_SUCCESS`, `TMF_NOT_FOUND`, `TMF_FAILED`, or `TMF_TIMEDOUT`. Device and target reset suspend TX, fail affected tasks, clear the TMF header, and restart TX. Session reset asks userspace recovery to relogin and waits for the session to become logged in or terminal.

Connection lifecycle is userspace driven through the transport class. `iscsi_conn_bind()` marks the connection bound and resets command-number windows. `iscsi_conn_start()` validates negotiated burst and timeout parameters, transitions to logged-in, arms the transport timer, handles recovery age changes, unblocks the SCSI session, and wakes EH waiters. `iscsi_conn_stop()` moves the session to recovery or terminate, deletes timers, suspends TX, blocks the session for recovery, fails SCSI and management tasks, and clears TMF state. Host/session teardown coordinates class device removal with `ihost->num_sessions` and a removal waitqueue.

## State and Persistence Behavior

The file maintains volatile kernel state only. Persistent user configuration is not stored here; userspace writes negotiated or configured values through transport-class attributes and `iscsi_set_param()`. Session fields persist for the life of the class session: target names, CHAP strings, initiator/interface/boot metadata, CmdSN windows, negotiated burst/data-ordering settings, ERL, reset/abort timeouts, command pool, and TMF state. Connection fields persist for the class connection: timeouts, digest flags, max segment lengths, ExpStatSN, persistent address/port, local address, queues, counters, and the login buffer.

Concurrency is split between `frwd_lock` for queueing/transmit/session state and `back_lock` for receive completion/task freeing. Refcounts protect tasks that may be racing between transmit, receive, timeout, and EH paths. The session `age` is embedded into ITTs unless a transport provides its own parser, preventing stale completions from a previous login from completing new-session tasks.

## Dependencies and Integration Points

This file integrates the SCSI midlayer, SCSI EH, scsi_transport_iscsi class, kernel workqueues/timers/waitqueues/kfifo/refcounting, net TCP definitions, and protocol structures from `iscsi_proto.h`. It expects low-level drivers such as software TCP iSCSI, bnx2i, cxgbi, or other offloads to provide `struct iscsi_transport` callbacks for PDU allocation, transmit, cleanup, task initialization, ITT parsing, optional T10 PI checks, and endpoint disconnect coordination. Userspace open-iscsi controls login, parameter negotiation, stop/start, recovery, and receives async/login/text/logout PDUs through the transport class.

## Risks and Edge Cases

The highest-risk areas are task lifetime races across transmit retry, receive completion, abort, and connection stop. `cleanup_queued_task()` has to remove tasks from command, management, requeue, saved-transmit, and running-aborted slots without double completion. CmdSN accounting is subtle for pending tasks, non-immediate management PDUs, and failed direct transmit paths. TMF restrictions must allow required Data-Out only when safe and reject affected LUN I/O during abort/reset. Timeout handling depends on `last_xfer`, `last_timeout`, NOP timers, and receive progress; wrong updates can cause premature EH or hung commands.

Parameter setters use simple parsing and string replacement, so callers must provide valid negotiated values before `iscsi_conn_start()`. Several getters emit nullable string fields with `%s`, making initialization expectations important. `iscsi_host_remove()` waits for userspace/class session teardown; broken recovery or session destruction can stall removal. Recovery age is four bits and wraps at 16, so stale ITT protection relies on timely cleanup as well as age comparison.

## Test Signals

Useful signals include SCSI I/O under direct-transmit and workqueue transports, CmdSN window full behavior returning `SCSI_MLQUEUE_TARGET_BUSY`, immediate and unsolicited write data, R2T requeue interaction in TCP transports, login/text/logout passthrough to userspace, NOP ping timeout and reject handling, session relogin after `STOP_CONN_RECOVER`, shutdown/host-removal behavior, and sysfs parameter round-trips. EH testing should cover abort success, abort timeout, LUN reset, target reset fallback to session reset, commands completing while EH holds references, and recovery with stale completions from a previous session age.
