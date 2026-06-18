<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/mockstore_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/datastore/mockstore_test.go

## Purpose
In-memory kvstore implementation used by datastore tests.

## Important APIs, Types, And Functions
`MockStore` holds `db map[string]*MockData`. It implements `Put`, `Exists`, `List`, `AtomicPut`, `AtomicDelete`, `Delete`, and `Close` for the internal kvstore interface.

## Control Flow
`Put` increments per-key indexes. `List` returns keys with the requested prefix or `ErrKeyNotFound`. `AtomicPut` checks absence or matching `LastIndex`, then delegates to `Put`. `AtomicDelete` checks matching index before deleting.

## State And Persistence
All state is in-memory and process-local.

## Dependencies And Integration Points
Used by `NewTestDataStore` to test `datastore.Store` without BoltDB.

## Risks And Edge Cases
The mock returns `types.InvalidParameterErrorf` for atomic conflicts rather than the same sentinel errors a real store may return, so it may not exercise wrapper error mapping exactly. It is not synchronized and is only safe under the datastore's external mutex in tests.

## Test Signals
Datastore unit tests indirectly validate mock behavior; additional tests could cover conflict and deletion paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/mockstore_test.go -->
