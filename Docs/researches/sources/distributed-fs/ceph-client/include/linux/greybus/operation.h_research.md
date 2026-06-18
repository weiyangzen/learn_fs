<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/operation.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/operation.h

Purpose: This header defines Greybus operations: request/response RPC objects sent over a connection.

Important APIs/types/functions: `enum gb_operation_result` maps Greybus result codes. `struct gb_message` stores operation pointer, wire header, payload pointer/size, backing buffer, and host-controller private pointer. Operation flags mark incoming, unidirectional, short-response allowed, and core. `struct gb_operation` stores connection, request/response messages, flags, type, id, errno result, work, callback, completion, timeout timer, kref, waiter count, active marker, connection list links, and private data. APIs create operations, allocate responses, send async/sync with timeout, cancel, receive on a connection, handle message-sent callbacks, perform one-shot sync/unidirectional operations, and init/exit operation core.

Control flow, state, and persistence: Outgoing calls create an operation, fill request payload, send via host driver, wait for completion or callback, then drop references. Incoming messages create incoming operations and dispatch work to handlers. Timers convert missing responses to timeout errors; cancellation wakes waiters and detaches active operations.

Dependencies/integration: It sits on `gb_connection`, host `gb_message` transport, workqueues, timers, completions, krefs, and packed message headers from `greybus_protocols.h`.

Risks and test signals: Races among send completion, timeout, cancel, incoming response, and connection disable are the main risk. Tests should cover sync success/error/timeout, short responses, unidirectional operations, incoming request dispatch, malformed headers, reference lifetime, and operation-core init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/operation.h -->
