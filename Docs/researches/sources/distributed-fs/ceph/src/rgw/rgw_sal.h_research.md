# sources/distributed-fs/ceph/src/rgw/rgw_sal.h

## Purpose
`rgw_sal.h` defines the RGW Store Abstraction Layer. It is the main contract separating protocol/front-end RGW code from storage backends and filters. It declares abstractions for drivers, users, buckets, objects, multipart upload, lifecycle, restore, notifications, writers, zones, placement tiers, Lua, and driver management.

## Important APIs, Types, and Functions
Core streaming abstractions are `DataProcessor`, `ObjectProcessor`, `DataProcessorFactory`, and `Writer`. `Driver` is the singleton backend/filter interface and includes account/user/group/role lookup and persistence, bucket/object creation and listing, zone and sync access, lifecycle/restore managers, notifications, pubsub topics, usage logs, quotas, rate limits, metadata listing, Lua managers, OIDC providers, IAM roles, and atomic/append writer factories.

`User` abstracts identity metadata, attrs, usage, MFA, persistence, and group listings. `Bucket` abstracts listing, attrs, ACLs, creation/removal, stats, quota, owner changes, index repair, multipart upload access, bucket notifications, and bucket logging. `Object` abstracts read/delete operations, copy, ACLs, cached state/attrs, atomic/prefetch/compression flags, transitions to and from cloud tiers, multipart part listing, OMAP helpers, versioning helpers, torrent info, chown, tracing, and object identity.

`MultipartUpload` and `MultipartPart` cover multipart state, part listing, abort, complete, writer creation, object-lock metadata, checksum type/flags, and orphan cleanup. `Serializer`, `MPSerializer`, `LCSerializer`, and `RestoreSerializer` define backend locks. `Lifecycle` and SAL `Restore` define persistent lifecycle/restore queues. `Notification` publishes reserve/commit events. `PlacementTier`, `ZoneGroup`, and `Zone` expose placement and multisite topology. `LuaManager` abstracts script/package storage. `DriverManager` declares factory helpers implemented in `rgw_sal.cc`.

## Control Flow
Protocol handlers interact with SAL objects rather than backend internals. A request resolves a `Driver`, loads a `User`/`Bucket`/`Object`, prepares read/write/delete/copy operations, streams data through processors or callbacks, and commits via virtual backend methods. Background services obtain `Lifecycle` or `Restore` handles from the driver and manipulate queue entries through serializers. Admin APIs use `DriverManager` and config stores to choose the correct backend.

## State and Persistence Behavior
This header defines persistence contracts but usually not storage details. Most methods operate on cached metadata plus explicit read/store calls. Optimistic concurrency is represented by `RGWObjVersionTracker` and writer/serializer handles. Object write visibility is defined by `ObjectProcessor::complete()`. Flags such as `FLAG_LOG_OP`, `FLAG_PREVENT_VERSIONING`, `FLAG_FORCE_OP`, and `FLAG_SKIP_UPDATE_OLH` influence backend persistence semantics. Restore status/type enums are encoded as small integer values.

## Dependencies and Integration Points
The header includes RGW common types, checksums, Lua, notifications, request context, tracing, RADOS-specific temporary headers, and many forward declarations. It is included by most RGW subsystems and every SAL backend. The RADOS-specific includes are marked as temporary subclass dependencies.

## Risks
The interface is very broad, so backend implementations can drift semantically. Several methods are marked temporary or "may be removed", indicating unstable boundaries. Many APIs use raw pointers, mutable references, and caller-owned output parameters, so lifetime and partial-mutation behavior require discipline. Adding virtual methods affects every backend/filter. Some methods expose backend-specific concepts such as bucket index repair and RADOS-style OMAP through generic SAL.

## Test Signals
Conformance tests should exercise each backend through common user/bucket/object CRUD, object range reads, copy/write/delete with versioning and conditions, multipart lifecycle, restore and lifecycle queues, notifications, topic mappings, quota/stats, role/OIDC/group/account APIs, cloud transition/restore, Lua manager, and driver filters. Compile tests should build all enabled backends after any interface change.
