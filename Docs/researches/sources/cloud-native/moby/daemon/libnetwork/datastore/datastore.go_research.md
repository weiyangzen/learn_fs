<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/datastore.go -->
# sources/cloud-native/moby/daemon/libnetwork/datastore/datastore.go

## Purpose
Provides libnetwork's local persistent key/value datastore wrapper over BoltDB plus an in-memory cache and optimistic atomic operations.

## Important APIs, Types, And Functions
`Store` wraps `store.Store` and `cache`. `KVObject` defines key, prefix, value marshal/unmarshal, index, existence, skip, new, and copy behavior. `Key` builds rooted keys. `New` opens `local-kv.db` in the configured bucket. Store APIs include `PutObjectAtomic`, `GetObject`, `List`, `Map`, `DeleteObject`, and `DeleteObjectAtomic`.

## Control Flow
Atomic put validates object/value, uses previous index when the object exists, writes via `AtomicPut`, records returned index, then updates cache. Deletes either bypass or enforce optimistic index checks. `Map` walks raw store keys under a prefix and unmarshals objects into a trimmed-key map.

## State And Persistence
Persistent state is BoltDB under `<dir>/local-kv.db` and bucket `libnetwork` by default. Cache mirrors store content and tracks skipped objects in memory.

## Dependencies And Integration Points
Used by controller, networks, endpoints, bridge driver, and sandbox stores. Depends on internal kvstore/boltdb and libnetwork typed errors.

## Risks And Edge Cases
`PutObjectAtomic` maps `store.ErrKeyExists` to `ErrKeyModified` but other stale-index errors depend on backing store behavior. `DeleteObject` updates cache only after store delete succeeds, so missing persisted keys can leave cache entries. All store operations are serialized by one mutex.

## Test Signals
`datastore_test.go` and mock store tests cover key construction, atomic object update, value validation, and cache interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/datastore.go -->
