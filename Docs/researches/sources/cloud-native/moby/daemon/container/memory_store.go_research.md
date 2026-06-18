<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/memory_store.go -->
# sources/cloud-native/moby/daemon/container/memory_store.go

## Purpose
Implements the daemon container `Store` interface with a mutex-protected in-memory map.

## Important APIs, Types, And Functions
`memoryStore`, `NewMemoryStore`, `Add`, `Get`, `Delete`, `List`, `Size`, `First`, `ApplyAll`, and private `all`.

## Control Flow
Add overwrites existing IDs. Read operations copy pointers under read lock. `List` sorts via `History`. `ApplyAll` snapshots all containers, then invokes the reducer concurrently for every container and waits.

## State And Persistence Behavior
Runtime-only map from IDs to container pointers. It does not persist or deep-copy containers.

## Dependencies And Integration Points
Satisfies `Store` used by daemon live container registry. `register` in daemon code writes here before checkpointing.

## Risks And Test Signals
Risks include overwriting existing IDs, reducers mutating containers concurrently, and store modifications inside reducers being prohibited only by comment. Tests cover CRUD, ordering, first-filter, and ApplyAll pointer mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/memory_store.go -->
