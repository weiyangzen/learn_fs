<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.c

Purpose: owns firmware command allocation, serialization, synchronous response tracking, timeout handling, and exported session/core command helpers.

Important APIs/functions: exported helpers include `vpu_session_configure_codec()`, `vpu_session_start()`, `vpu_session_stop()`, `vpu_session_encode_frame()`, `vpu_session_alloc_fs()`, `vpu_session_release_fs()`, `vpu_session_abort()`, `vpu_session_rst_buf()`, `vpu_session_fill_timestamp()`, `vpu_session_update_parameters()`, `vpu_core_snapshot()`, `vpu_core_sw_reset()`, `vpu_response_cmd()`, and `vpu_clear_request()`. Internal `struct vpu_cmd_t` stores the packed RPC event, expected response mapping, sequence key, and last-response pointer.

Control flow: callers request a command through `vpu_session_send_cmd()`. The command is packed through the selected iface, queued on `inst->cmd_q`, and sent under `core->cmd_lock` if no other response-waiting command is pending. Commands with expected responses become `inst->pending`. Message handling calls `vpu_response_cmd()` first with `handled=0` when a matching event is received and again with `handled=1` after handler completion; the mapping decides when the pending command is cleared. Synchronous callers wait on `core->ack_wq` using command sequence keys. Start/configure have a wakeup workaround that sends a NOOP if the first short wait times out.

State and persistence: state is in the instance command list, `pending`, monotonic `cmd_seq`, and atomic `last_response_cmd`. Core state may be marked hung via `hang_mask` on timeout. No persistent storage.

Dependencies and integration: uses iface pack/send/pre/post hooks from `vpu_rpc.c`, mailbox signaling from `vpu_mbox.c`, response events from `vpu_msgs.c`, and wait lock callbacks from codec ops.

Risks: response matching depends on firmware event order and the `handled` flag policy. A timeout clears pending and marks the core hang but queued commands may have already been sent or remain queued. `vpu_clear_request()` assumes `inst->core` exists. NOOP wakeup is explicitly a firmware workaround and can hide marginal boot/start races.

Test signals: command timeout injection, response reordering, configure/start wakeup retry, abort/reset buffer, snapshot/reset completion, concurrent queue submissions under `cmd_lock`, and streamoff while a synchronous command is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.c -->
