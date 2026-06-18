<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/datastore_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/datastore/datastore_test.go

## Purpose
Unit tests and dummy objects for libnetwork datastore/cache behavior.

## Important APIs, Types, And Functions
`NewTestDataStore` builds a `Store` with `MockStore`. `TestKey`, `TestKVObjectFlatKey`, and `TestAtomicKVObjectFlatKey` verify key formatting, object storage, retrieval, existence/index updates, and repeated atomic updates. `dummyObject`, `recStruct`, and `dummyKVObject` implement `KVObject` behavior and JSON marshaling.

## Control Flow
Tests store dummy objects atomically, retrieve copies by key, mutate return-value behavior, and assert successful updates using current indexes.

## State And Persistence
State lives in the in-memory mock store and cache. Dummy objects model DB index/existence flags.

## Dependencies And Integration Points
Exercises datastore against the same `KVObject` interface used by libnetwork runtime objects.

## Risks And Edge Cases
Coverage is narrow: it does not assert stale-index failure paths, delete behavior, list/map behavior, skipped persistence, or concurrent cache population.

## Test Signals
Passing tests confirm basic key contract and optimistic update happy paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/datastore_test.go -->
