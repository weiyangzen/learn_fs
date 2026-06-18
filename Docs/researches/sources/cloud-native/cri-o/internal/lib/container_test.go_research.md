# sources/cloud-native/cri-o/internal/lib/container_test.go

## Purpose
Tests `ContainerServer` lookup helpers for containers by ID/name/short ID and validation of created container state.

## Important APIs, Types, And Functions
- Exercises `LookupContainer` and `GetContainerFromShortID`.
- Uses shared fixtures `addContainerAndSandbox`, `myContainer`, `mySandbox`, `containerID`, and `sandboxID`.

## Control Flow
Tests add a container/sandbox for successful lookup, call lookup helpers with empty or invalid IDs for failures, and construct a not-yet-created container in indexes/state to confirm `GetContainerFromShortID` rejects it.

## State And Persistence
Mutates in-memory server state, name/ID indexes, and sandbox/container stores. No disk state is written.

## Dependencies And Integration Points
Validates integration between registrar/truncindex lookup and in-memory OCI container state. Uses the shared lib test setup.

## Risks And Edge Cases
The not-created test documents that index presence alone is insufficient; `ctr.Created()` must be true. Empty input error strings come from lookup helpers.

## Test Signals
Focused signal for lookup correctness and guarding against operations on uncreated containers.
