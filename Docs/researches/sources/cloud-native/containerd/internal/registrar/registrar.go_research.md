# sources/cloud-native/containerd/internal/registrar/registrar.go

## Purpose
Implements a thread-safe one-to-one reservation table between names and keys.

## Important APIs, Types, And Functions
`Registrar` owns `nameToKey` and `keyToName` maps under a mutex. `NewRegistrar`, `Reserve`, `ReleaseByName`, and `ReleaseByKey` manage mappings. `ReservedErr` reports conflicts and implements `Conflict()`.

## Control Flow
`Reserve` rejects empty fields, returns nil for idempotent same mapping, errors if either side is already reserved for a different counterpart, and otherwise inserts both map entries. Release methods delete both directions if present.

## State And Persistence
All reservations are in-memory only.

## Dependencies And Integration Points
Uses `sync` and `fmt`. The `Conflict()` marker can integrate with containerd error classification.

## Risks
No lookup API is provided. Error messages expose existing names/keys. Callers must release reservations on lifecycle cleanup to avoid leaks.

## Test Signals
`registrar_test.go` covers reservation, idempotence, conflicts, releases, re-reservation, and same-name/key mapping.
