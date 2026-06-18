# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox_helper.h

Purpose: declares synchronous mailbox helper constants, callback state, a request/response/message declaration macro, and helper prototypes used by AIE2 firmware command wrappers.

Important APIs/types: `TX_TIMEOUT` and `RX_TIMEOUT` define nominal send and receive waits. `struct xdna_notify` carries a completion, response data pointer, expected response size, error, and status pointer. `DECLARE_XDNA_MSG_COMMON(name, op, s)` creates zeroed request, initialized response status, notify handle, and `xdna_mailbox_msg` wired to `xdna_msg_cb`.

Control flow: AIE2 message functions use the macro to reduce boilerplate, then fill request fields and call `xdna_send_msg_wait()`. The mailbox RX worker invokes `xdna_msg_cb()` to complete the wait.

State and persistence: notify objects are caller-owned and generally stack-local; no global state.

Dependencies: Linux completions and mailbox message definitions.

Risks: the macro assumes request and response types follow `<name>_req` and `<name>_resp` naming and that response has a `status` member. It initializes completion on stack, so the notify handle must not outlive the sending function.

Test signals: build all message wrappers using the macro, response-status initialization, timeout behavior, and static analysis for stack lifetime escapes.
