# sources/cloud-native/buildkit/solver/result/attestation.go

## Purpose
This file defines generic attestation payload metadata attached to BuildKit results. It covers SBOM/provenance attestation reasons, inline-only/core metadata keys, in-toto subject information, digest map conversion, and reference conversion across result backends.

## Important APIs and Types
`Attestation[T]` holds the frontend attestation kind, metadata, an optional typed reference, path, lazy `ContentFunc`, and `InTotoAttestation`. `InTotoAttestation` contains a predicate type and `InTotoSubject` entries. `ToDigestMap` and `FromDigestMap` convert between digest slices and algorithm-to-encoded maps. `ConvertAttestation` maps a referenced value from `U` to `V` while preserving metadata, path, content callback, and in-toto data.

## Control Flow
The digest map helpers iterate directly over their inputs. `ConvertAttestation` checks the zero value of the source type: zero refs are preserved as zero refs without calling the transformer, while non-zero refs are transformed and errors are returned immediately.

## State and Persistence
No persistent state is owned here. Metadata maps, content functions, and in-toto structures are passed through by reference, so callers should treat them as immutable or copy them before mutation.

## Dependencies and Integration Points
It depends on gateway protobuf attestation enums, `context`, and OCI digest types. It is consumed by `solver/result/result.go` and by image/exporter paths that attach SBOM and provenance information to result references.

## Risks
`ToDigestMap` collapses multiple digests with the same algorithm, keeping the last encoded value. `FromDigestMap` has map iteration order nondeterminism. `ConvertAttestation` does not deep-copy metadata or in-toto slices, so mutation after conversion can affect both versions.

## Test Signals
No direct tests in this subset. It is indirectly exercised by generic result conversion logic and exporter/provenance paths elsewhere.
