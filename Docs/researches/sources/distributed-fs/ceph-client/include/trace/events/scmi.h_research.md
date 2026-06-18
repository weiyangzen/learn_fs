
# sources/distributed-fs/ceph-client/include/trace/events/scmi.h

## Purpose
Defines tracepoints for ARM SCMI message transport, fast-channel calls, transfer lifecycle, response waits, receive completion, and payload dumps.

## Important APIs, Types, and Functions
Events are `scmi_fc_call`, `scmi_xfer_begin`, `scmi_xfer_response_wait`, `scmi_xfer_end`, `scmi_rx_done`, and `scmi_msg_dump`. `TRACE_SCMI_MAX_TAG_LEN` bounds copied dump tags. Fields cover protocol id, message id, resource id, values, transfer id, sequence, polling mode, timeout, inflight count, status, channel id, message type, and dynamic payload bytes.

## Control Flow
SCMI drivers emit `scmi_fc_call` for fast-channel accesses, `scmi_xfer_begin` when a message transfer starts, `scmi_xfer_response_wait` while waiting, `scmi_rx_done` when an inbound response/notification arrives, `scmi_xfer_end` on completion, and `scmi_msg_dump` when raw payload logging is requested.

## State and Persistence
The header owns no SCMI state. Trace records snapshot transfer identifiers and optionally copy payload bytes into a dynamic trace array. The copied payload persists only in trace buffers and can outlive transport buffers safely.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, SCMI core transfer state, and transport channel implementations. Integrates with SCMI protocol drivers for clocks, power, sensors, performance, reset, and vendor protocols.

## Risks
Payload dumping can expose firmware data and add overhead. Tags are truncated to six bytes, so consumers should not depend on full labels. Protocol/message ids are numeric and require SCMI protocol context to interpret. Incorrect payload length passed by call sites would affect copied trace data.

## Test Signals
Signals include SCMI selftests, firmware-backed boot traces, timeout/error injection, polling versus interrupt transports, payload dump validation, and checking trace output while exercising clock/performance/sensor protocols.
