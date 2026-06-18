# sources/cloud-native/containerd/internal/cri/io/streaming.go

## Purpose

This file opens CRI IO streams over sandbox-provided streaming endpoints, supporting ttrpc or gRPC transports over Unix/vsock-style addresses.

## Important APIs, Types, and Functions

`ioStream` wraps `streamingapi.Stream` plus the underlying connection/client closer. `openStdinStream` returns a byte-stream writer. `openOutputStream` returns a byte-stream reader. `openStream` parses a URL of the form `<protocol>+<scheme>://<address>?streaming_id=<id>`, dials the real address, creates a proxy stream, and returns a close-aware stream wrapper.

## Control Flow

`openStream` parses and validates the scheme, extracts `streaming_id`, reconstructs the transport address, and dials via `shim.AnonReconnectDialer`. For `ttrpc`, it creates a `ttrpc.Client` and proxy stream creator. For `grpc`, it creates an insecure gRPC client and proxy stream creator. Unsupported protocols and malformed URLs return errors.

## State and Persistence Behavior

State is one stream plus one underlying client connection per open call. `ioStream.Close` closes both the stream and connection. No local files are persisted.

## Dependencies and Integration Points

It depends on containerd streaming/proxy APIs, transfer byte-stream helpers, shim reconnect dialer, ttrpc, and gRPC. `helpers.go` uses these functions whenever FIFO config fields contain a URL.

## Risks and Edge Cases

The gRPC path shadows the earlier dialed connection with a new gRPC client from `grpc.NewClient`, so transport behavior depends on gRPC target parsing. URLs must contain `streaming_id`; older comments sometimes say `stream_id`, but code requires `streaming_id`. Insecure gRPC credentials are expected for local shim transports but would be unsafe for remote networks.

## Test Signals

Tests should cover malformed URL, missing protocol, missing stream ID, unsupported protocol, ttrpc stream creation, gRPC stream creation, and connection closure on stream close.
