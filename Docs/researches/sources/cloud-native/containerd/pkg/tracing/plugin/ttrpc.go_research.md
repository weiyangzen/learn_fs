<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/plugin/ttrpc.go -->
# sources/cloud-native/containerd/pkg/tracing/plugin/ttrpc.go

## Purpose
Registers ttrpc OpenTelemetry interceptor plugin.

## Important APIs, Types, And Functions
init registers plugin ID otelttrpc of type TTRPCPlugin. otelttrpcopts implements UnaryServerInterceptor and UnaryClientInterceptor.

## Control Flow
Plugin init returns a stateless otelttrpcopts value; callers request interceptors when composing ttrpc servers/clients.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by shim event publisher and shim ttrpc server when plugin registry loads tracing ttrpc integration.

## Risks And Edge Cases
Always registers; actual tracing depends on global OpenTelemetry setup.

## Test Signals
No direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/plugin/ttrpc.go -->
