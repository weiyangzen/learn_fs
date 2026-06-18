# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_pubsub_push.h

## Purpose
Declares the polymorphic endpoint interface for RGW pubsub notification delivery. Implementations send `rgw_pubsub_s3_event` payloads to configured webhook, AMQP, Kafka, or future endpoint types.

## Important APIs And Types
`RGWPubSubEndpoint` is non-copyable and uses `std::unique_ptr` alias `Ptr`. `create()` is the factory taking endpoint URI, topic, parsed HTTP-style args, and optional Ceph context. `send()` is the virtual delivery method and accepts a `DoutPrefixProvider`, event, and optional coroutine yield. `to_str()` returns a human-readable endpoint description. `configuration_error` is a `logic_error` subclass used for invalid endpoint configuration. `init_all()` and `shutdown_all()` manage global backend resources.

## Control Flow And State
The header defines the contract only. Endpoint construction may throw configuration errors; callers should catch them and decide whether to retry or fail the notification. Runtime state is owned by concrete derived classes and global backend managers in the implementation file.

## Dependencies And Integration Points
Depends on common forward declarations, `optional_yield`, `RGWHTTPArgs`, and `rgw_pubsub_s3_event`. It integrates with `rgw_notify.cc`, which creates endpoints during persistent queue processing or immediate commit and calls `send()`.

## Risks And Test Signals
Because `send()` returns negative errno-style values and construction throws exceptions, callers must handle both failure styles. Endpoint lifetime is per factory result unless callers add caching. Tests should verify factory failure handling, polymorphic deletion through the virtual destructor, and coroutine/non-coroutine send behavior for each compiled backend.
