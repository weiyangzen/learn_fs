# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sal_rados.h

## Purpose
This header declares the RADOS-backed implementation of RGW's storage abstraction layer. It adapts generic `rgw::sal` concepts such as `StoreDriver`, `StoreUser`, `StoreBucket`, `StoreObject`, `StoreWriter`, `Lifecycle`, `Restore`, notifications, Lua management, and roles onto the legacy `RGWRados` service stack and librados/neorados primitives.

## Important APIs, Types, and Functions
- `RadosStore` is the central `StoreDriver` implementation, exposing `RGWRados`, `RGWServices`, `RGWCtl`, `RadosZone`, `neorados::RADOS`, and user control pointers.
- `RadosZoneGroup`, `RadosZone`, and `RadosPlacementTier` wrap zonegroup, zone, placement, tiering, and sync-policy data.
- `RadosUser`, `RadosBucket`, and `RadosObject` implement user, bucket, and object operations, including metadata, usage, ACLs, bucket index maintenance, quota checks, multipart, copy/delete/read, cloud transition, restore, Swift versioning, omap helpers, and chown.
- `RadosObject::RadosReadOp` and `RadosObject::RadosDeleteOp` bridge SAL operations to `RGWRados::Object` read/delete state.
- `RadosMultipartUpload`, serializers, lifecycle/restore classes, notification, atomic/append/multipart writers, Lua manager, and role classes cover higher-level RADOS-backed RGW features.

## Control Flow
Callers enter through generic SAL methods on `RadosStore`, `RadosBucket`, or `RadosObject`. Most work is delegated to `RGWRados`, service pointers from `svc()`, metadata controllers from `ctl()`, RADOS IO contexts, and put-object processors. Object writes flow through writer construction, `prepare()`, data `process()`, then `complete()` to make data and metadata visible. Reads and deletes use nested op objects to retain RADOS-specific operation state behind generic SAL interfaces.

## State and Persistence Behavior
Persistent state includes RGW metadata objects, bucket indexes, object heads/tails, usage logs, lifecycle and restore queues, pubsub topic metadata, Lua package/script objects, role/account/group metadata, and multipart metadata. `RadosObject` normally owns an `RGWObjectCtx` but shares it when copied, making invalidation and ownership important. Serializers persist cls lock state; writers persist object data, manifests, attrs, delete markers, version metadata, and index updates.

## Dependencies and Integration Points
The file depends on SAL base interfaces, `rgw_rados.h`, notification, roles, multipart, put-object processors, RADOS tiering services, cls lock, librados, and neorados. It is the main integration point between portable RGW request logic and the RADOS backend, including admin APIs, metadata listing/removal, usage, sync wakeups, sync-policy, and data-sync managers.

## Risks
- Broad raw-pointer exposure to services owned by `RGWRados` makes lifetime ordering critical.
- `RadosObject` copy construction shares object context and manifest pointers while changing ownership, so stale state and double-free bugs are possible if assumptions drift.
- Asynchronous lock renewal in `MPRadosSerializer` is race-prone around cancellation and unlock.
- Backend bridges touch versioning, notification, usage, and sync, so small signature changes can have wide behavioral impact.

## Test Signals
Useful signals include RGW object read/write/delete tests, multipart complete/abort/list tests, lifecycle and restore tests, pubsub notification tests, Lua reload/watch tests, role/account/group metadata tests, bucket index consistency tests, and multisite sync tests that exercise metadata/data sync wakeups.
