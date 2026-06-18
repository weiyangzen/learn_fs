<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer.proto -->
# sources/cloud-native/containerd/api/services/transfer/v1/transfer.proto

## Purpose
Canonical protobuf contract for containerd's transfer service. It defines a single high-level `Transfer` RPC for moving artifacts between typed sources and destinations.

## Important APIs and Types
`service Transfer` has unary RPC `Transfer(TransferRequest) returns (google.protobuf.Empty)`. `TransferRequest` carries `source`, `destination`, and `options`. `TransferOptions` currently contains `progress_stream`; a comment hints at future progress interval configuration.

## Control Flow
The proto defines request shape only. Runtime flow is expected to unpack source and destination `Any` payloads, perform transfer work, optionally publish progress, and return empty success or an error status.

## State and Persistence
No persistence is implemented here. The wire contract carries references to transfer endpoints and a progress stream name; content store mutations and progress state belong to service implementations.

## Dependencies and Integration Points
Imports protobuf `Any` and `Empty`. The `Any` fields are designed to integrate with containerd transfer type protos such as image store, registry, import/export, streaming, and progress definitions.

## Risks
Because the source and destination are opaque at the service boundary, type compatibility and authorization checks are critical. Expanding `TransferOptions` should preserve field numbers and clarify progress semantics.

## Test Signals
Tests should verify generated gRPC/ttrpc bindings, `Any` type-url compatibility for known transfer endpoints, invalid source/destination rejection, and progress publication behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/transfer/v1/transfer.proto -->
