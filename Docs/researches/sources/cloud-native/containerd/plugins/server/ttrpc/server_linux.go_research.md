# sources/cloud-native/containerd/plugins/server/ttrpc/server_linux.go

## Purpose
Builds the Linux TTRPC server with same-user Unix socket handshaking and OpenTelemetry interception.

## Important APIs, Types, And Functions
`newTTRPCServer` returns `ttrpc.NewServer` with `UnixSocketRequireSameUser` and `otelttrpc.UnaryServerInterceptor`.

## Control Flow
Called during TTRPC plugin init to construct the server before service registration.

## State And Persistence
No persistence; configures runtime server behavior.

## Dependencies And Integration Points
Linux-only. Integrates with containerd TTRPC server plugin and OpenTelemetry TTRPC instrumentation.

## Risks
Same-user enforcement affects client compatibility and security posture.

## Test Signals
No direct tests.
