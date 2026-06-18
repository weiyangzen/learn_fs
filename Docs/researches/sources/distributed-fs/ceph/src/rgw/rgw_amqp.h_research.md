# sources/distributed-fs/ceph/src/rgw/rgw_amqp.h

## Purpose
Declares the RGW AMQP notification publishing API and connection identifier type.

## Important APIs, Types, and Functions
- `reply_callback_t` receives integer publish-confirm status.
- `init()`/`shutdown()` manage the global AMQP manager.
- `connect()` creates or reuses a connection for URL/exchange/SSL settings.
- `publish()` and `publish_with_confirm()` enqueue messages.
- Getter functions expose queue, connection, in-flight, and configured limit metrics.

## Control Flow
No implementation logic is present, but the API establishes an asynchronous model: connect first, then publish by returned `connection_id_t`; confirm callbacks are invoked later by the manager thread.

## State and Persistence
No state is stored in the header. `connection_id_t` is a value key copied from parsed AMQP connection info.

## Dependencies and Integration Points
Uses `CephContext`, `boost::optional`, and rabbitmq-c's `amqp_connection_info` forward declaration. Consumed by RGW notification code.

## Risks and Edge Cases
Callers must handle negative RGW-specific status codes and normal AMQP status codes. The callback can run asynchronously on the manager thread, so callback implementations must be thread-safe and nonblocking.

## Test Signals
API tests should verify lifecycle ordering, status string coverage, metric behavior before/after init, and callback invocation contracts.
