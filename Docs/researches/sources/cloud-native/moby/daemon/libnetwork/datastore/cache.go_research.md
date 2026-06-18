<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/cache.go -->
# sources/cloud-native/moby/daemon/libnetwork/datastore/cache.go

## Purpose
In-memory cache layer for libnetwork datastore objects, keyed by KV object prefix and full key.

## Important APIs, Types, And Functions
`cache` holds `kmm map[string]kvMap` and a backing `store.Store`. `kmap` lazily populates a prefix map from the backing store. `add`, `del`, `get`, and `list` mutate or read cached objects and optionally emulate atomic indexing for skipped persistence.

## Control Flow
On first access for a key prefix, `kmap` lists the backing store, unmarshals objects through `KVObject.New` and `SetValue`, records DB indexes, and installs the map with first-writer-wins behavior if concurrent goroutines race. Atomic cache operations compare indexes when persistence is skipped and increment indexes on add.

## State And Persistence
Cache state is in-memory only. It mirrors persisted objects and also sequences `KVObject.Skip()` objects that never hit disk.

## Dependencies And Integration Points
Used exclusively by `datastore.Store` to back `PutObjectAtomic`, `GetObject`, `List`, and deletes. Depends on the internal kvstore interface and datastore `KVObject` contract.

## Risks And Edge Cases
Objects are cached by reference, so callers mutating returned objects can affect cache unless `CopyTo` is used on reads. `list` returns cached object instances directly. Lazy population relies on prefix listing semantics and ignores empty values.

## Test Signals
Datastore tests validate flat-key reads, atomic updates, cache population, and mock-store behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/cache.go -->
