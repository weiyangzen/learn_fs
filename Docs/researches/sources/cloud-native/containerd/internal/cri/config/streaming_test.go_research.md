# sources/cloud-native/containerd/internal/cri/config/streaming_test.go

## Purpose

`streaming_test.go` unit-tests TLS mode validation for CRI streaming server configuration.

## Important APIs, Types, and Functions

- `TestValidateStreamServer` table-drives `getStreamListenerMode`.

## Control Flow

The test checks default no-TLS mode, explicit x509 key pair mode, self-signed TLS mode, key/cert set while TLS disabled, and missing key/cert pair cases. Expected-error cases assert an error and return; success cases compare the selected mode.

## State and Persistence Behavior

All state is in-memory config structs.

## Dependencies and Integration Points

It depends on `DefaultServerConfig`, `ServerConfig`, and `getStreamListenerMode`.

## Risks and Edge Cases

The test validates mode selection but does not load actual cert files or run `StreamingConfig`, so address resolution and cert generation failures are covered elsewhere only indirectly.

## Test Signals

Failures point to incorrect TLS configuration validation for CRI streaming.
