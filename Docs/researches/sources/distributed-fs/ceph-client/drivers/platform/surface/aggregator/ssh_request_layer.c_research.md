# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_request_layer.c

## Purpose
Implements the SSH request transport layer above the packet layer. It maps request objects to packet submissions, correlates responses by request ID, dispatches EC events, enforces pending limits, supports flush and cancellation, and times out requests that have been transmitted but did not receive a response.

## Important APIs, Types, And Functions
Public APIs are `ssh_request_init()`, `ssh_rtl_init()`, `ssh_rtl_destroy()`, `ssh_rtl_start()`, `ssh_rtl_submit()`, `ssh_rtl_cancel()`, `ssh_rtl_flush()`, and `ssh_rtl_shutdown()`. Key internal paths include queue/pending helpers, `ssh_rtl_tx_work_fn()`, `ssh_rtl_packet_callback()`, `ssh_rtl_complete()`, `ssh_rtl_timeout_reap()`, `ssh_rtl_rx_data()`, and `ssh_rtl_rx_command()`. The request layer wraps each request's packet ops with `ssh_rtl_packet_ops`.

## Control Flow
`ssh_rtl_submit()` validates that response-bearing requests are sequenced, binds the embedded packet to the underlying PTL, queues the request, and schedules TX work. `ssh_rtl_tx_work_fn()` processes up to `SSH_RTL_TX_BATCH` requests per workqueue run, moves requests to pending, and submits embedded packets. Packet completion calls `ssh_rtl_packet_callback()`: failed packet status completes the request; successful transmission either starts a response timeout or completes no-response requests. Inbound data from the packet layer is parsed as a command, filtered to host-targeted messages, routed to `ops.handle_event()` if the request ID encodes an event, or matched to a pending request by RQID and completed with response data.

## State And Persistence Behavior
State is in-memory only. `struct ssh_request` state bits track queued, pending, transmitting, transmitted, response received, canceled, completed, and type flags. `struct ssh_rtl` holds queue and pending lists, an atomic pending count, TX work, and delayed timeout work. Request timestamps are set once after successful packet transmission for response timeouts. Flush requests are stack-allocated wrappers with a completion and special packet/request type bits.

## Dependencies And Integration Points
Embeds and initializes `struct ssh_ptl`, uses `sshp_parse_command()`, Surface Aggregator controller/request definitions, workqueues, spinlocks, completions, tracepoints, and optional response-drop error injection. Upper layers interact through `ssam_request_do_sync*()` and controller/event infrastructure, while lower-layer data and packet completions arrive via packet-layer callbacks.

## Risks
The layer relies on precise memory ordering around `packet.ptl` publication and cancellation. Cancel paths differ for unsubmitted, queued, pending, and already transmitted requests, making race regressions likely if flags are changed. `ssh_rtl_complete()` scans pending requests by RQID and assumes responses usually arrive in order. If an unexpected or early response appears before packet ACK/transmitted state, it completes with `-EREMOTEIO`. `ssh_rtl_submit()` sets `packet.ptl` before checking RTL shutdown and does not reset it on `-ESHUTDOWN`; callers should not reuse failed request objects without reinitialization.

## Test Signals
Test response/no-response requests, unsequenced response rejection, queue saturation at `SSH_RTL_MAX_PENDING`, flush ordering, response timeout, packet failure propagation, event dispatch, host-TID filtering, cancellation before submit/in queue/in pending/after packet success, shutdown with queued and pending requests, and error-injected dropped responses.
