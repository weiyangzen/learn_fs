# sources/cloud-native/buildkit/frontend/gateway/client/attestation.go

## Purpose

This file converts BuildKit result attestations between in-memory generic result types and gateway protobuf messages. It allows attestations to cross the gateway API while rejecting callback-based attestation content that cannot be serialized.

## Important APIs, Types, And Functions

- `AttestationToPB[T]` converts `result.Attestation[T]` to `pb.Attestation`.
- `AttestationFromPB[T]` converts a protobuf attestation back to `result.Attestation[T]`.
- `digestSliceToPB` and `digestSliceFromPB` convert digest slices between typed `digest.Digest` and strings.

## Control Flow

`AttestationToPB` first rejects `ContentFunc`, then maps every in-toto subject to protobuf fields and copies top-level kind, metadata, path, predicate type, and subjects. `AttestationFromPB` rejects nil attestations and nil subjects, then rebuilds the generic result attestation.

## State And Persistence Behavior

There is no persistent state. Metadata maps and digest slices are passed through or shallow-copied according to protobuf/result field behavior; digest slices are explicitly cloned into new slices.

## Dependencies And Integration Points

It integrates with gateway protobuf package, BuildKit `solver/result` attestations, and Open Containers digests. Server and client return paths call these functions when solving or returning gateway results with attestations.

## Risks And Edge Cases

Callback attestations are intentionally unsupported over gateway and cause errors. Nil protobuf subjects are rejected to avoid panics or malformed attestations. Because metadata is assigned directly, callers should avoid mutating shared maps after conversion if aliasing matters.

## Test Signals

No direct test in this subset targets attestation conversion. Gateway solve and return paths exercise error behavior when attestations are present; targeted tests should cover nil input, nil subject, content callback rejection, and digest round trips.
