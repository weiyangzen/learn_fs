<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/memory_store_test.go -->
# sources/cloud-native/moby/daemon/container/memory_store_test.go

## Purpose
Tests the in-memory container store implementation.

## Important APIs, Types, And Functions
Tests call `NewMemoryStore`, `Add`, `Get`, `Delete`, `Size`, `List`, `First`, and `ApplyAll`.

## Control Flow
Each test creates a fresh store, manipulates containers, and asserts map size, lookup result, sorted order, filter result, or reducer mutation.

## State And Persistence Behavior
In-memory only; no disk writes.

## Dependencies And Integration Points
Uses `NewBaseContainer` and `History` sorting indirectly. It validates the live daemon store contract.

## Risks And Test Signals
Signals include Add increasing size, Delete removing entries, newest-first ordering, filter match by ID, and ApplyAll running reducers on stored pointers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/memory_store_test.go -->
