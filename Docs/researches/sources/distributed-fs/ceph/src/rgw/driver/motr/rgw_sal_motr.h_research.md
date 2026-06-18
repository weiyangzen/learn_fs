# sources/distributed-fs/ceph/src/rgw/driver/motr/rgw_sal_motr.h

## Purpose

This header declares the CORTX Motr implementation of the RGW Store Abstraction Layer. It defines the Motr-backed store, user, bucket, object, writer, multipart, zone, notification, Lua, cache, and helper types that the implementation uses to map RGW operations onto Motr indices and objects.

## Important APIs, Types, and Functions

- Global index names define the persistent Motr metadata roots for users, bucket instances, bucket headers, access keys, and emails.
- `MotrMetaCache` wraps `ObjectCache` and declares metadata cache get/put/remove/invalid plus placeholder distribution/watch callbacks.
- `MotrUserInfo`, `MotrEmailInfo`, and `MotrAccessKey` are encoded records for Motr user metadata and secondary lookup indices.
- `MotrNotification` is a minimal `StoreNotification` implementation whose publish methods return success.
- `MotrUser` derives from `StoreUser` and declares user load/store/remove, bucket creation, attrs/stats/usage operations, MFA verification, and helpers for user-info indices.
- `MotrBucket` derives from `StoreBucket`; it embeds encoded `MotrBucketInfo`, object listing, removal, bucket info persistence, owner linking, multipart listing, ACLs, stats/quota/check methods, and bucket cloning.
- `MotrPlacementTier`, `MotrZoneGroup`, and `MotrZone` adapt RGW placement and zone abstractions to the Motr store.
- `MotrLuaManager` declares script/package methods for Lua manager integration.
- `MotrObject` derives from `StoreObject`; it contains encoded `Meta` for Motr object id/pver/layout, nested read/delete ops, object attrs/state/copy/delete methods, omap methods, Motr object open/create/read/write/delete helpers, multipart part helpers, and version-entry update.
- `MPMotrSerializer` is a placeholder multipart lock with no real locking.
- `MotrAtomicWriter` and `MotrMultipartWriter` declare normal object and multipart part write flows.
- `MotrMultipartPart` and `MotrMultipartUpload` model multipart uploaded parts and the multipart upload lifecycle.
- `MotrStore` derives from `StoreDriver` and declares the main RGW backend API plus Motr-specific index helpers, secondary-index helpers, metadata cache initialization, and Motr client/container state.
- `obj_time_weight` implements timestamp comparison logic for conditional request checks.

## Control Flow

The declarations show RGW SAL ownership relationships: `MotrStore` creates users, buckets, objects, writers, notifications, zones, and multipart uploads; `MotrUser` creates buckets; `MotrBucket` creates objects and multipart uploads; `MotrObject` creates read/delete operations and writers manipulate `MotrObject` payload/metadata.

The persistent metadata path is declared as encoded C++ structs written into Motr indices. The object data path is declared through `MotrObject::Meta` plus `m0_obj` handles, with `MotrAtomicWriter` and `MotrMultipartWriter` responsible for publishing metadata after data IO.

## State and Persistence Behavior

`MotrStore` owns process state for Motr: `CephContext`, `m0_client`, `m0_container`, config structures, and three metadata caches. It also owns a `MotrZone` and sync module reference.

Persistent metadata structures are all Ceph-encoded into `bufferlist` values. `MotrObject::Meta` is the bridge from RGW metadata entries to actual Motr object payloads. Per-object open state is represented by `struct m0_obj* mobj`, which is closed by the object destructor or explicit close.

## Dependencies and Integration Points

The header has a hard dependency on Motr C client/config headers inside `extern "C"`, and on RGW headers including `rgw_sal_store.h`, `rgw_rados.h`, `rgw_notify.h`, `rgw_role.h`, `rgw_multi.h`, and `rgw_putobj_processor.h`. It integrates deeply with RGW SAL virtual interfaces and Ceph encoding macros.

## Risks and Edge Cases

- The header exposes a large surface where many methods are later implemented as placeholders. Callers may receive success from unsupported features.
- `MotrObject::delete_object()` declaration appears to contain typos (`td::list`, `GWObjVersionTracker`) rather than standard/RGW types, which is a build risk unless hidden by conditional compilation or stale code paths.
- `MotrZone` allocates realm/zone/period objects with `new` in constructors but its destructor is defaulted, implying leaks.
- `MotrStore` destructor deletes cache pointers that are not visibly initialized to null in the header constructor, so construction failure or missing `init_metadata_cache()` could make deletion unsafe.
- `MPMotrSerializer` does not enforce locking, so multipart serialization is not safe across concurrent clients.
- `obj_time_weight::init(RGWObjState*)` references `dpp` in an error log without a visible parameter/member in the struct, another build or stale-code risk.
- Several override signatures need to track the exact current RGW SAL interface; any drift produces compile failures.

## Test Signals

There are no tests in the header. Compile coverage against current RGW SAL interfaces is essential. Runtime tests should focus on object lifecycle, index persistence, multipart locking semantics, cache initialization/destruction, and unsupported method behavior.
