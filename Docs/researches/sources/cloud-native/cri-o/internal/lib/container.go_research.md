# sources/cloud-native/cri-o/internal/lib/container.go

## Purpose
Provides lookup helpers on `ContainerServer` for resolving containers and sandboxes by name, full ID, or short ID, and for retrieving the storage container/top layer associated with an OCI container.

## Important APIs, Types, And Functions
- `GetStorageContainer`, `GetContainerTopLayerID`, `GetContainerFromShortID`, `LookupContainer`, `getSandboxFromRequest`, and `LookupSandbox`.

## Control Flow
Container lookup validates non-empty input, resolves names through registrars when possible, falls back to treating input as an ID, resolves short IDs through truncindex, retrieves objects from in-memory stores, and validates containers are created. Storage helpers first resolve the OCI container and then query the containers/storage store for container metadata/layer ID. Sandbox lookup mirrors the container path with pod name and ID indexes.

## State And Persistence
Reads in-memory registrars/truncindex/memorystore and the storage backend. It does not mutate state.

## Dependencies And Integration Points
Integrates `registrar` name reservations, `truncindex` ID prefix lookup, in-memory CRI-O container/sandbox stores, OCI container state, and containers/storage metadata.

## Risks And Edge Cases
Empty IDs/names fail fast. Registrar errors other than name-not-reserved abort lookup. A resolved ID missing from memory or a not-yet-created container returns an error. Short ID ambiguity is handled by truncindex.

## Test Signals
`container_test.go` covers successful lookup, empty input errors, invalid short IDs, and the not-created container guard.
