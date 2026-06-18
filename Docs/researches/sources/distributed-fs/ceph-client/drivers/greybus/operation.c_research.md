# sources/distributed-fs/ceph-client/drivers/greybus/operation.c

## Purpose

`operation.c` implements the Greybus operation/message engine. It allocates request/response messages, assigns operation IDs, sends messages through host-controller callbacks, dispatches incoming requests, matches incoming responses to outgoing operations, handles synchronous waits, timeouts, cancellation, response status mapping, and operation lifecycle/refcounting.

## Important APIs, Types, and Functions

- Global caches `gb_operation_cache` and `gb_message_cache`, plus `gb_operation_completion_wq`, back operation allocation and completion callbacks.
- `gb_operation_create_flags()`, `gb_operation_create_core()`, and `gb_operation_create_incoming()` create outgoing, core, or incoming operations.
- `gb_operation_request_send()` sends an operation asynchronously; `gb_operation_request_send_sync_timeout()` and `gb_operation_sync_timeout()` provide synchronous wrappers.
- `gb_operation_unidirectional_timeout()` sends no-response operations.
- `greybus_message_sent()` is called by host drivers when transmit completes.
- `gb_connection_recv()` validates and routes incoming wire data to request or response handlers.
- `gb_operation_cancel()` and `gb_operation_cancel_incoming()` synchronously cancel operations during teardown.
- `gb_operation_result_set()` enforces the state transition from `-EBADR` to `-EINPROGRESS` to one final result.

## Control Flow

Outgoing operations allocate a request and response buffer, fill payload, assign a nonzero operation ID unless unidirectional, set result to `-EINPROGRESS`, take an extra operation reference, add the operation to the connection active list if the connection state permits, and call the host driver's `message_send()`. Completion can come from send failure, unidirectional send completion, incoming response, timeout, or cancellation. Finalization is queued to `gb_operation_completion_wq`, which deletes timers, cancels stuck sends on timeout, runs the caller callback, removes the active reference, and drops the completion reference.

Incoming data is copied into a local header first to tolerate unaligned transport buffers. Requests allocate an incoming operation in atomic context and are queued to the connection workqueue for protocol handling. Responses find an active outgoing operation by ID, validate expected response size unless short responses are allowed, copy response bytes, set the final result, and queue completion.

## State and Persistence Behavior

Operation state persists until kref release. Important fields include connection, request/response messages, operation ID, type, flags, errno state, active count, waiters, timer, work item, callback, and completion. Active operations are linked on `connection->operations` under the connection spinlock. Result updates are guarded by `gb_operations_lock`.

## Dependencies and Integration Points

This file depends on connection state and flags, host-driver `message_send`/`message_cancel`, Greybus protocol header/status definitions, workqueues, timers, wait queues, kmem caches, tracepoints, and protocol handlers installed on connections such as SVC and control.

## Risks and Edge Cases

- `gb_connection_recv()` drops incomplete messages without completing a matching outgoing operation; a later timeout is required.
- `message_cancel()` is host-driver-specific; transports with no real cancel support can leave frames in flight.
- Operation IDs wrap modulo `U16_MAX`; matching relies on active-list uniqueness during wrap.
- `gb_operation_request_send()` sets `-EINPROGRESS` before active-list insertion and send; send-path failures return directly without changing the result, so callers should use the returned errno.
- Response size validation must stay consistent with protocols that permit short responses.
- Cancellation waits on active count; missed active wakeups would deadlock teardown.

## Test Signals

Cover allocation limits, invalid operation type/flags, sync success/failure, unidirectional sends, response matching and unexpected response IDs, short/oversized responses, wire status-to-errno mapping, send failure, timeout cancel of stuck sends, interrupted synchronous wait, incoming request dispatch with and without handler, connection-state gating, active waiters, and kmem-cache init/exit.
