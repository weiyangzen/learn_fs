# sources/cloud-native/containerd/core/streaming/proxy/streaming.go

## Purpose
This file adapts gRPC or TTRPC streaming clients to containerd's internal `streaming.StreamCreator` interface.

## Important APIs, Types, and Functions
`NewStreamCreator` accepts generated gRPC clients, gRPC connections, TTRPC clients/services, or an existing `streaming.StreamCreator`. `streamCreator.Create` opens a service stream, sends a `StreamInit` message containing the requested stream ID, waits for an acknowledgement, and returns a `clientStream`. `clientStream` wraps send, receive, and close operations.

## Control Flow
Creation chooses a client adapter, opens a bidirectional stream, marshals the init object through `typeurl`, sends it as protobuf `Any`, receives an ack, and then proxies future `typeurl.Any` messages.

## State and Persistence
No durable state is stored. Runtime state is the active remote stream and its negotiated ID.

## Dependencies and Integration Points
Integrates `api/services/streaming/v1`, `typeurl`, gRPC, TTRPC, and `errgrpc.ToNative`. It is used by transfer proxying and stream-backed transfer endpoints.

## Risks
Stream creation depends on the remote side accepting the init handshake. EOF handling is special-cased, but other transport errors must be normalized correctly. A missing acknowledgement prevents stream use.

## Test Signals
No direct tests in this file; transfer streaming fuzz tests and proxy transfer paths exercise the stream abstraction indirectly.
