<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/grpclog.go -->
# sources/cloud-native/moby/daemon/command/grpclog.go

## Purpose
Reduces noise from gRPC's default logger by remapping gRPC info, warning, and error streams to lower daemon log levels.

## Important APIs, Types, And Functions
`configureGRPCLog` constructs a `grpclog.LoggerV2` from containerd logger writers: info to trace, warning to debug, and error to warn.

## Control Flow
The function is called before Cobra execution in `daemonRunner.Run` and globally replaces gRPC logging.

## State And Persistence Behavior
Mutates gRPC global logger state for the process lifetime.

## Dependencies And Integration Points
Depends on `containerd/log` and `google.golang.org/grpc/grpclog`. It affects BuildKit/containerd/daemon gRPC integrations.

## Risks And Test Signals
Risk is hidden diagnostics if severity mapping is too low. There are no direct tests here; operational log volume and daemon startup logs are integration signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/grpclog.go -->
