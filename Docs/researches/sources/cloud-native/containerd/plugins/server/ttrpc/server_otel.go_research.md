# sources/cloud-native/containerd/plugins/server/ttrpc/server_otel.go

## Purpose
Builds TTRPC servers with OpenTelemetry interception for Windows and Solaris.

## Important APIs, Types, And Functions
`newTTRPCServer` returns `ttrpc.NewServer` with `otelttrpc.UnaryServerInterceptor`.

## Control Flow
Called by the shared TTRPC server plugin at initialization.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Compiled under `windows || solaris`; integrates with TTRPC plugin and OpenTelemetry.

## Risks
Unlike Linux, this constructor does not install Unix same-user handshaking, matching platform capabilities.

## Test Signals
No direct tests.
