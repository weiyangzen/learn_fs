<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/store.go -->
# sources/cloud-native/moby/daemon/container/store.go

## Purpose
Defines the abstract container store contract used by the daemon.

## Important APIs, Types, And Functions
`StoreFilter`, `StoreReducer`, and `Store` interface methods `Add`, `Get`, `Delete`, `List`, `Size`, `First`, and `ApplyAll`.

## Control Flow
No implementation; implementers decide locking and ordering. `memoryStore` is the local implementation in this subset.

## State And Persistence Behavior
The interface does not require persistence or copies. Implementations may be runtime-only.

## Dependencies And Integration Points
Used by daemon container registry code to decouple live container access from concrete storage.

## Risks And Test Signals
Risk is weak contract around duplicate IDs, mutation during `ApplyAll`, and sorted `List` expectations. Memory store tests are the immediate signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/store.go -->
