# sources/cloud-native/buildkit/client/buildid/metadata.go

## Purpose

This file defines the gRPC metadata key and helpers used to route gateway API calls to the active BuildKit build job.

## Important APIs, Types, and Functions

- `metadataKey` is `buildkit-controlapi-buildid`.
- `AppendToOutgoingContext` appends the build ID to outgoing gRPC metadata when non-empty.
- `FromIncomingContext` extracts exactly one build ID value from incoming gRPC metadata.

## Control Flow and State

The client-side gateway wrapper calls `AppendToOutgoingContext` before every gateway RPC. Server-side handlers can call `FromIncomingContext` to recover the target job. If no metadata exists, no IDs are present, or multiple IDs are present, extraction returns an empty string.

No persistent state is stored; build ID travels with each gRPC request.

## Dependencies and Integration Points

The helpers depend on `google.golang.org/grpc/metadata`. They are integrated by `client/build.go` and tested indirectly by gateway tests that call the bridge with missing or unknown build IDs.

## Risks and Edge Cases

`AppendToOutgoingContext` appends rather than replaces. If a context already contains the same metadata key, `FromIncomingContext` will see multiple values and return empty. This is a deliberate strictness but can surprise callers that reuse contexts. Empty build IDs are silently omitted.

## Test Signals

`build_test.go` verifies that direct gateway calls without build ID fail with "no buildid found in context" and that random unknown IDs return a not-found error. There are no direct unit tests for duplicate metadata values.
