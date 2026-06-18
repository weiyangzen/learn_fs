# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_pubsub_push.cc

## Purpose
Implements concrete bucket-notification push endpoints for HTTP/S webhooks and optional AMQP/Kafka backends. It serializes S3 event payloads to JSON, manages global endpoint libraries/managers, validates endpoint arguments, and sends events with synchronous or coroutine-compatible waiting.

## Important APIs, Types, And Functions
`json_format_pubsub_event()` formats a single event inside the expected plural JSON wrapper. `get_bool()` parses boolean endpoint arguments. `RGWPubSubHTTPEndpoint` sends JSON by `RGWHTTPManager` and supports `verify-ssl`, `cloudevents`, and `http-ack-level` parsing. Optional `RGWPubSubAMQPEndpoint` supports AMQP 0-9-1 with exchange, ack level, SSL verification, and publisher confirms. Optional `RGWPubSubKafkaEndpoint` supports Kafka SSL/auth options and broker/no-ack modes.

`RGWPubSubEndpoint::create()` dispatches based on endpoint schema (`http`, `https`, `amqp`, `amqps`, `kafka`). `init_all()` initializes optional AMQP/Kafka libraries and the HTTP manager. `shutdown_all()` shuts them down. `init_http_manager()` and `shutdown_http_manager()` guard the global HTTP manager with a shared mutex and in-flight counter.

## Control Flow
HTTP send checks that the global manager exists, enforces `rgw_http_notif_max_inflight`, builds a POST request with configured connect/message timeouts, serializes the event, optionally adds CloudEvents binary-mode headers, increments pending perf counters, queues the request, waits, and decrements counters. AMQP/Kafka sends either fire-and-return for no-ack or publish with confirm, using `yield_waiter` when a coroutine yield is available and blocking waiter otherwise.

Endpoint creation first normalizes the schema. Unsupported schemas throw `configuration_error`. AMQP version defaults to `0-9-1`; AMQP 1.0 explicitly throws unsupported. The global initialization order is AMQP, Kafka, then HTTP; failure of any enabled backend aborts overall initialization.

## State And Persistence
This file persists no RGW data. Runtime singleton state includes `s_http_manager`, `s_http_manager_mutex`, and `s_http_manager_inflight`. AMQP/Kafka endpoint instances hold connection ids from their backend libraries. Perf counters record pending/failed/ok signals but are not durable.

## Dependencies And Integration Points
Depends on curl-backed RGW HTTP request classes, `RGWHTTPManager`, Ceph async waiters, JSON formatting, CloudEvents/RGW event types, endpoint argument parsing, optional `rgw_amqp.h` and `rgw_kafka.h`, RGW data sync/pubsub types, config values, and notification perf counters. It is used by `rgw_notify.cc` for immediate and persistent delivery.

## Risks And Edge Cases
HTTP `ack_level` is parsed but not yet used to interpret response status/body, so HTTP success is currently tied to request execution rather than configurable status semantics. `shutdown_http_manager()` takes an exclusive lock and stops the manager while sends use shared locks, which avoids reset during send but can block shutdown behind long requests. In-flight max returns `-EBUSY`, feeding retry behavior in persistent queues. Optional AMQP/Kafka code paths compile only when enabled, so coverage can vary by build. Tests should cover schema dispatch, invalid args, HTTP manager absent/busy, CloudEvents headers, endpoint initialization/shutdown, and AMQP/Kafka confirm/no-ack paths in enabled builds.
