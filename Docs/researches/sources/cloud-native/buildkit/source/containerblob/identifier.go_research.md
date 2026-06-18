# sources/cloud-native/buildkit/source/containerblob/identifier.go

## Purpose
This file defines the identifier for a single image blob source. It parses digest-qualified blob references, stores file materialization attributes, and records provenance for blob inputs.

## Important APIs and Types
`ImageBlobIdentifier` stores a containerd `reference.Spec`, scheme name, optional OCI session/store IDs, usage record type, output filename, permissions, UID, and GID. `NewImageBlobIdentifier` parses a reference and requires an object digest. `Scheme` defaults to `DockerImageBlobScheme` when unset. `Capture` validates the pinned digest and records an image blob source in provenance.

## Control Flow
Construction parses the input string and rejects references without an object. `Capture` parses the solver-provided pin, requires the reference object to be an `@digest`, parses that digest, compares it to the pin, and adds provenance with `Local` set for OCI-layout blobs.

## State and Persistence
The identifier itself is immutable after parsing except for attributes populated by `source.go`. It does not persist content. Its fields influence cache keys and snapshot materialization in `pull.go`.

## Dependencies and Integration Points
It depends on containerd reference parsing, BuildKit client usage record types, source scheme constants, provenance capture types, and OCI digest parsing. `containerblob/source.go` creates and populates these identifiers.

## Risks
Digest mismatch in `Capture` fails the provenance path, which protects correctness but can surface late depending on capture timing. The constructor only requires an object; stronger digest validation happens later through `Reference.Digest().Validate` in the puller.

## Test Signals
No direct tests in this subset. Behavior is indirectly validated by blob source resolution and provenance tests elsewhere.
