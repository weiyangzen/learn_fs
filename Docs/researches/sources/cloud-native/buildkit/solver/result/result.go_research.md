# sources/cloud-native/buildkit/solver/result/result.go

## Purpose
This file defines a generic result container for one primary reference, named reference maps, metadata, and attestations. It provides helper methods for adding, finding, iterating, comparing, and converting typed references.

## Important APIs
`Result[T]` stores `Ref`, `Refs`, `Metadata`, and `Attestations`. Methods include `Clone`, `AddMeta`, `AddRef`, `AddAttestation`, `SetRef`, `SingleRef`, `FindRef`, `EachRef`, and `IsEmpty`. Package functions `EachRef` and `ConvertResult` coordinate references between two results or convert all references from one comparable type to another.

## Control Flow
Mutation methods lazily allocate maps under a mutex. `SingleRef` rejects a map-only result where the primary ref is the zero value. `FindRef` returns an exact named ref, falls back to the only map entry if there is exactly one, and otherwise reports false. `EachRef` walks the primary ref, map refs, and attestation refs, returning the first error but continuing iteration. `ConvertResult` applies a transformer to non-zero refs and delegates attestation conversion to `ConvertAttestation`.

## State and Persistence
State is in memory. The mutex protects some methods, but `Clone`, package-level `EachRef`, and `ConvertResult` read fields without locking; callers should avoid concurrent mutation during these operations. `Clone` shallow-copies maps and slices, not metadata byte slices or attestation slices' nested fields.

## Dependencies and Integration Points
It uses Go `maps`, `sync`, and `pkg/errors`. It is the common result shape used by BuildKit frontends and exporters for multi-output references and attested artifacts.

## Risks
The mix of locked and unlocked access can race if callers mutate results concurrently. Shallow metadata copies can share byte slices. `EachRef` assumes paired results have matching keys and attestation ordering; mismatches are silently skipped.

## Test Signals
No direct tests in this subset. Behavior is indirectly covered where result references are converted or exported, but concurrency assumptions are not locally tested.
