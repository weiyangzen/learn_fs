# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_mailbox_helper.c

Purpose: provides synchronous helper glue around the asynchronous mailbox API: copy a firmware response into caller storage, complete a wait, and send a message while waiting for completion.

Important APIs/functions: `xdna_msg_cb()` is a standard mailbox callback that accepts an `xdna_notify` handle, treats NULL data as cancellation, validates response size, copies response data from MMIO with `memcpy_fromio()`, completes the stack completion, and returns stored error. `xdna_send_msg_wait()` calls `xdna_mailbox_send_msg()`, waits up to `RX_TIMEOUT`, and returns either send error, timeout, or callback error.

Control flow: firmware command helpers declare request/response/notify/message objects using the macro in the header, populate request fields, then call `xdna_send_msg_wait()` on the management channel.

State and persistence: no long-lived state; `xdna_notify` is usually stack-scoped and completed by the mailbox RX worker. Response data is copied into caller-provided response storage.

Dependencies: mailbox API, Linux completions, MMIO copy, DRM logging through AMD XDNA device.

Risks: callback size mismatch returns `-EINVAL` and still completes. Send timeout does not cancel the pending mailbox message; later channel stop or firmware response will release it. Callers must initialize completion and response status correctly.

Test signals: normal response, timeout, NULL-data cancellation on stop, size mismatch, callback error propagation, and repeated synchronous firmware commands under concurrent mailbox RX.
