# sources/distributed-fs/ceph-client/drivers/greybus/greybus_trace.h

## Purpose

`greybus_trace.h` defines Greybus ftrace tracepoint classes and events for message, operation, connection, bundle, interface, module, and host-device lifecycle and traffic. `core.c` instantiates these tracepoints by defining `CREATE_TRACE_POINTS`; selected events are exported from `hd.c` for other modules.

## Important APIs, Types, and Functions

- `TRACE_SYSTEM greybus` names the tracing subsystem.
- Message events include `gb_message_send`, `gb_message_recv_request`, `gb_message_recv_response`, `gb_message_cancel_outgoing`, `gb_message_cancel_incoming`, and `gb_message_submit`.
- Operation events include `gb_operation_create`, `gb_operation_create_core`, `gb_operation_create_incoming`, `gb_operation_destroy`, `gb_operation_get_active`, and `gb_operation_put_active`.
- Connection events include create/release/get/put/enable/disable.
- Bundle events include create/release/add/destroy.
- Interface events include create/release/add/del/activate/deactivate/enable/disable.
- Module events include create/release/add/del.
- Host-device events include create/release/add/del/in.

## Control Flow

Each event class declares the object pointer argument, copies stable fields into the trace entry in `TP_fast_assign`, and formats a compact line in `TP_printk`. Call sites in the Greybus implementation invoke `trace_gb_*()` around lifecycle transitions, message send/receive, cancellation, and active-list mutations.

## State and Persistence Behavior

Tracepoints do not own Greybus state. They snapshot fields while the call site is executing. Several entries read mutable fields such as operation active count, errno, waiters, connection state, interface flags, and bundle counts; the values are diagnostic observations rather than synchronization points.

## Dependencies and Integration Points

The file depends on Linux tracepoint infrastructure, little-endian conversion helpers, and public Greybus struct definitions. `TRACE_INCLUDE_PATH` is set to `.` and `TRACE_INCLUDE_FILE` to `greybus_trace`, so build-system include paths must allow the generated trace header to resolve.

## Risks and Edge Cases

- Trace events dereference object internals; call sites must only trace while objects remain valid.
- The `gb_operation` event class declares fields in one order but the print format passes operation ID, CPort, and type in a different argument order than the labels suggest, so trace consumers should verify output semantics before relying on positional text parsing.
- Dynamic connection name copies `sizeof(connection->name)` bytes, which is safe for fixed buffers but assumes the name array is NUL-terminated for printing.
- Trace ABI consumers may depend on field names, so changes should be deliberate.

## Test Signals

Enable `tracefs` events under `greybus`, run host probe, SVC hello, module insertion, operation timeout/cancel, bundle bind/unbind, interface suspend/resume, and host disconnect. Check that trace enablement does not alter behavior and that event fields are coherent with device state.
