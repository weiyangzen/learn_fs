<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version.proto -->
# sources/cloud-native/containerd/api/services/version/v1/version.proto

## Purpose
Canonical proto contract for the containerd version service.

## Important APIs and Types
`service Version` exposes `Version(google.protobuf.Empty) returns (VersionResponse)`. `VersionResponse` has `version` and `revision` strings.

## Control Flow
Runtime flow is a simple unary query: client sends empty request, server returns its version metadata.

## State and Persistence
The proto carries no persistent state. Values are expected to be derived from daemon build metadata or runtime configuration.

## Dependencies and Integration Points
Imports `google/protobuf/empty.proto`. Generated bindings expose the service over gRPC and ttrpc.

## Risks
The TODO asks whether the version service should be versioned; if future service versions diverge, clients may need compatibility negotiation outside this minimal response.

## Test Signals
Tests should verify daemon version endpoint availability, non-empty expected revision/version in release builds, and generated client compatibility across transports.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/version/v1/version.proto -->
