# sources/distributed-fs/ceph/src/rgw/rgw_sal_store.h

## Purpose
Defines shared base classes for store-backed SAL implementations. These classes provide common in-memory state and default behavior for concrete drivers such as dbstore or RADOS-derived stores, reducing duplication across user, bucket, object, multipart, serializer, notification, writer, placement, zone, restore, and Lua manager implementations.

## Important APIs, types, and functions
`RGWObjState` is the central object-state structure. It stores object identity, atomic/prefetch/compression flags, existence and delete-marker flags, size/accounted size, mtime, epoch, tags, shadow object, optional prefetched data, OLH state, version tracker, and attribute map. Its copy constructor intentionally copies selected fields and warns maintainers to keep it updated.

`StoreDriver` derives from `Driver`, supplies random request ids, and gives default unsupported topic/pubsub methods. `StoreUser` owns `RGWUserInfo`, `RGWObjVersionTracker`, and `Attrs`, and implements basic getters/setters. `StoreBucket` owns `RGWBucketInfo`, attrs, version, and mtime, and implements bucket identity, owner, placement, versioning, comparison, topic/logging defaults, and metadata accessors.

`StoreObject` owns `RGWObjState`, an optional `Bucket*`, and tracing context. It implements generic object getters/setters, state invalidation that preserves selected flags, attr access, bucket binding, object identity updates, cloud-transition default failures, torrent attr lookup, version tracker access, and printing.

Other base classes include `StoreMultipartPart`, `StoreMultipartUpload`, `StoreMPSerializer`, `StoreLCSerializer`, `StoreRestoreSerializer`, `StoreRestore`, `StoreNotification`, `StoreWriter`, `StorePlacementTier`, `StoreZoneGroup`, `StoreZone`, and `StoreLuaManager`.

## Control flow
This header is mostly inline methods. Concrete drivers inherit the base state containers and override storage operations. Common operations such as object attr lookup, bucket equality, request-id generation, and Lua path/background setters execute directly in the base classes.

## State and persistence behavior
The file defines cached SAL state but does not persist by itself. Concrete drivers decide when to load or store `RGWUserInfo`, `RGWBucketInfo`, `RGWObjState`, attrs, versions, multipart parts, and serializer locks. `StoreObject::invalidate()` is important state control: it clears loaded object state while preserving object identity and selected caller-set flags. `StoreMultipartUpload` owns a map of part wrappers and a trace context.

## Dependencies and integration points
The header includes `rgw_sal.h` and is included by concrete store implementations such as `rgw_sal_dbstore.h`. It relies on RGW types for users, buckets, objects, lifecycle, pubsub, logging, tracing, restore, and Lua.

## Risks and test signals
The `RGWObjState` copy constructor omits some fields present in the struct, including `is_dm`, `tail_tag`, `has_attrs`, and some zone/data fields, so changes to object state require careful review. Base defaults returning success for bucket topics/logging can mask unsupported persistence if a concrete driver forgets to override them. `StoreBucket::operator!=()` returns false on differing dynamic types, mirroring `operator==()` behavior and deserving caller scrutiny. Tests should cover state invalidation, attr lookup, object copy behavior, bucket equality across same/different dynamic types, torrent attr lookup, and concrete driver override coverage for any default success methods.
