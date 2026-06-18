# sources/distributed-fs/ceph/src/rgw/rgw_sal_dbstore.h

## Purpose
Declares the dbstore implementation of RGW's Storage Abstraction Layer. The header defines concrete SAL classes for dbstore-backed users, buckets, objects, multipart uploads, writers, lifecycle, notifications, zones, placement tiers, Lua manager, and the `DBStore` driver itself.

## Important APIs, types, and functions
`DBStore` derives from `StoreDriver` and exposes the full RGW driver surface: user lookup/storage, bucket lookup/listing, object factory, lifecycle, notification, topic/account/group/role/OIDC interfaces, usage/stat APIs, metadata listing, sync hooks, quota/rate-limit hooks, writers, placement validation, initialization/finalization, and dbstore-specific `getDBStoreManager()`, `setDB()`, and `getDB()`.

`DBUser`, `DBBucket`, and `DBObject` derive from shared `StoreUser`, `StoreBucket`, and `StoreObject` base classes in `rgw_sal_store.h`. `DBObject` declares nested `DBReadOp` and `DBDeleteOp` wrappers around dbstore object operations. `DBAtomicWriter` and `DBMultipartWriter` derive from `StoreWriter` and hold backend write operation state, accumulated head/tail buffers, offsets, and sizes.

Multipart declarations include `DBMultipartPart`, `DBMPObj`, and `DBMultipartUpload`. `DBMPObj` encapsulates parsing and composing `<oid>.<upload_id>` meta object names. `DBMultipartUpload` exposes init/list/abort/complete/get-info/writer creation and stores owner, mtime, placement, and the parsed multipart identity.

Zone and lifecycle declarations include `DBPlacementTier`, `DBZoneGroup`, `DBZone`, `DBLifecycle`, `LCDBSerializer`, and `MPDBSerializer`. These provide minimal zonegroup/zone behavior, lifecycle table access, and serializer lock facades. `DBNotification` and `DBLuaManager` provide dbstore-specific notification and Lua manager objects.

## Control flow
The header establishes the object graph used by `rgw_sal_dbstore.cc`: `DBStore` creates or returns wrapper objects, wrappers retain a raw `DBStore*`, and method implementations use `store->getDB()` to reach persistence. Buckets create `DBObject` and `DBMultipartUpload` children. Multipart uploads create meta objects through their bucket, and writers carry a prepared `DB::Object::Write` operation across `prepare()`, `process()`, and `complete()`.

## State and persistence behavior
The declarations show that dbstore SAL wrappers are stateful adapters. User, bucket, and object state is inherited from `Store*` base classes; dbstore-specific classes add backend pointers, ACL caches, multipart identity, placement, and writer buffering state. `DBStore` owns a `DBStoreManager*`, stores a non-owning/default `DB*`, embeds `DBZone`, stores lifecycle and context pointers, and has a `use_lc_thread` flag. Persistence itself is delegated to `DB` and `DBStoreManager`, while this header defines the cached state and the method contracts that mutate it.

## Dependencies and integration points
The header depends on generic SAL declarations from `rgw_sal_store.h`, role/lifecycle/multisite headers, and dbstore backend headers `common/dbstore.h` and `dbstore_mgr.h`. It is the compile-time bridge between RGW front-end code and the dbstore driver implementation.

## Risks and test signals
The contract is broad, but many declared methods are only partially implemented in the `.cc`. That makes conformance drift a risk whenever SAL adds new virtual methods. Raw `DBStore*`, `DBStoreManager*`, `DB*`, and `RGWLC*` pointers require clear lifetime discipline. Serializer classes currently provide minimal lock behavior, so concurrency-sensitive multipart/lifecycle tests should verify actual guarantees expected by callers. Header-level tests are indirect: build failures catch signature drift, while integration tests should exercise user/bucket/object/multipart/lifecycle APIs through the generic SAL interface against the dbstore driver.
