# sources/distributed-fs/ceph/src/rgw/driver/rados/topic_migration.h

## Purpose
Declares the startup migration entry point for converting v1 pubsub topic/notification metadata to v2 format.

## Important APIs, types, and functions
- `migrate(const DoutPrefixProvider*, rgw::sal::RadosStore*, boost::asio::io_context&, boost::asio::yield_context)` runs the migration.

## Control flow
The declaration indicates coroutine/yield-based execution under Boost.Asio. Callers supply the RADOS store and logging prefix; the io context parameter is currently part of the API boundary.

## State and persistence behavior
The header documents that this migration is tied to enabling notification_v2 and runs on startup. Concrete state movement is implemented in `topic_migration.cc`.

## Dependencies and integration points
Includes Boost.Asio io_context/spawn and forward declares `RadosStore`. Used by RGW RADOS initialization code that gates feature migrations.

## Risks and edge cases
Callers need to ensure the migration runs only when the feature transition requires it and that repeated startup invocations are acceptable. API exposes a raw store pointer and coroutine yield context, so lifetime must exceed migration.

## Test signals
Integration tests should invoke this declared entry point with fixture legacy metadata and verify idempotent completion across repeated startup-style calls.
