# sources/cloud-native/containerd/api/services/streaming/v1/streaming.proto

## Purpose

This proto defines a generic bidirectional streaming service for containerd APIs. The stream carries protobuf `Any` messages in both directions, with `StreamInit` providing a simple identifier message.

## Important APIs, Types, and Functions

`service Streaming` contains one RPC: `Stream(stream google.protobuf.Any) returns (stream google.protobuf.Any)`. `message StreamInit` contains `id = 1`. The Go package is `github.com/containerd/containerd/api/services/streaming/v1;streaming`.

## Control Flow

The proto does not prescribe a full subprotocol. A caller opens a bidirectional stream and both peers exchange `Any` messages. `StreamInit` is the only concrete message defined here and is likely used to identify or bootstrap a stream.

## State and Persistence Behavior

No persistence contract is defined. Stream state is session-scoped and controlled by the service implementation. The `id` field is the only durable-looking correlation value in the schema.

## Dependencies and Integration Points

It imports `google/protobuf/any.proto` and is generated into Go protobuf, gRPC, and ttrpc bindings. Higher-level protocols can tunnel their own protobuf messages through `Any`.

## Risks

The generic `Any` envelope gives flexibility but weak compile-time guarantees. Without a documented ordering and allowed type list, implementations can disagree about stream initialization, message framing, and error semantics.

## Test Signals

Tests should cover bidirectional send/receive, `StreamInit` negotiation, unknown `Any` types, stream cancellation, EOF behavior, and backpressure or large-message handling in concrete implementations.
