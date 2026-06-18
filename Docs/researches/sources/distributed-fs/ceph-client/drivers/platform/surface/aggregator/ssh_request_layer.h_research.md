# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_request_layer.h

## Purpose
Defines the request transport layer API and state structure that sits above the SSH packet layer. It provides request submission/cancellation/lifecycle declarations and the event callback interface for the controller layer.

## Important APIs, Types, And Functions
`enum ssh_rtl_state_flags` defines `SSH_RTL_SF_SHUTDOWN_BIT`. `struct ssh_rtl_ops` exposes `handle_event()`. `struct ssh_rtl` embeds `struct ssh_ptl`, queue and pending lists, TX work, timeout reaper fields, and callback ops. Inline helpers include `ssh_rtl_get_device()` and `ssh_request_rtl()`. Declared APIs are `ssh_rtl_submit()`, `ssh_rtl_cancel()`, `ssh_rtl_init()`, `ssh_rtl_start()`, `ssh_rtl_flush()`, `ssh_rtl_shutdown()`, `ssh_rtl_destroy()`, and `ssh_request_init()`.

## Control Flow
Consumers initialize an `ssh_rtl` with serdev and ops, start the underlying packet TX/RX threads through `ssh_rtl_start()`, initialize individual `struct ssh_request` objects, set their data via serial-hub helpers, and submit them. Events received by the packet layer are lifted to `handle_event()` through the request-layer parser path.

## State And Persistence Behavior
All state is volatile runtime transport state. The request layer owns no persistent storage. The embedded PTL handles raw packet state; RTL adds request queueing, pending count, and response-timeout scheduling. `ssh_request_rtl()` recovers the containing request layer through the embedded packet's PTL pointer and returns `NULL` when a request has not yet been bound.

## Dependencies And Integration Points
Includes `linux/surface_aggregator/serial_hub.h`, `controller.h`, and `ssh_packet_layer.h`. The request layer is consumed by the Surface Aggregator controller implementation and any code using synchronous request helpers.

## Risks
The header exposes internals needed by the controller and tests, so structure layout changes affect embedding assumptions. `ssh_request_rtl()` depends on `packet.ptl` pointing to the embedded PTL of an `ssh_rtl`; using an `ssh_request` with a plain PTL would break the container cast. `rtl_info()` names its first macro argument `p` unlike adjacent macros, a minor readability hazard.

## Test Signals
Build checks should catch function signature drift. Runtime tests should validate `ssh_request_rtl()` before and after submission, shutdown rejection, flush semantics, event callback invocation, and proper teardown through `ssh_rtl_shutdown()` followed by `ssh_rtl_destroy()`.
