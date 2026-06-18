# sources/distributed-fs/ceph/src/rgw/rgw_amqp.cc

## Purpose
Implements RGW AMQP notification publishing with connection reuse, bounded message queueing, optional publisher confirms, SSL support, and a background manager thread.

## Important APIs, Types, and Functions
- Public namespace functions: `init`, `shutdown`, `connect`, `publish`, `publish_with_confirm`, metric getters, and `status_to_string`.
- `connection_id_t` identifies broker host/port/vhost/exchange/SSL.
- `connection_t` owns rabbitmq-c connection state, reply queue, callbacks, credentials, SSL settings, and reconnect timing.
- `new_state()` opens sockets, logs in, opens channels, enables confirms, verifies exchange, and declares/consumes a private reply queue.
- `Manager` owns connections, a lock-free message queue, counters, and the runner thread.

## Control Flow
`init()` creates the singleton manager. `connect()` parses an AMQP URL, reuses or creates a connection entry, and attempts state creation. `publish()` and `publish_with_confirm()` enqueue heap-allocated messages. The background thread consumes queued messages, publishes them to either the normal or confirming channel, records callbacks by delivery tag for confirm mode, scans connections for ACK/NACK/RETURN/CLOSE frames, invokes callbacks, destroys failed connection state, deletes idle connections, and retries failed connections after a short delay.

## State and Persistence
Runtime state includes the singleton manager pointer, connection map, message queue, callback vectors, counters, and rabbitmq-c connection resources. AMQP messages may be published with persistent delivery mode for confirm path, but this file does not persist RGW metadata.

## Dependencies and Integration Points
Depends on rabbitmq-c headers/APIs, OpenSSL, Boost lockfree queue/hash/optional, Ceph logging/time/thread naming, and RGW notification subsystem. It is used by RGW pubsub/notification code to publish events to AMQP endpoints.

## Risks and Edge Cases
The connection-map iteration relies on no rehashing and coarse locking; additions/removals while iterating are delicate. Confirm callbacks are limited by `max_inflight`; overflow invokes an immediate error after the message was already published successfully. Non-confirm publish errors destroy the connection without per-message retry. Reconnect backoff is fixed and short. `mandatory_delivery` is stored in `connection_t::mandatory` but not visibly assigned from the connect argument in the constructor call path, which should be checked. URL parsing uses a mutable copy because rabbitmq-c stores pointers.

## Test Signals
Tests should cover URL parsing and connection id reuse, SSL verify/CA failure codes, exchange/queue/confirm setup failures, queue-full behavior, manager shutdown with queued messages, ACK/NACK/multiple callback handling, connection close/retry, idle deletion, metric counters, and `mandatory_delivery` propagation.
