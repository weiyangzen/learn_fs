# sources/control-plane/csi-lib-utils/connection/connection.go

## Purpose
This package creates CSI gRPC client connections with secret-sanitized logging, optional metrics, optional OpenTelemetry tracing, configurable timeout, and Unix-socket connection-loss behavior.

## Important APIs, Types, And Functions
Public APIs include `SetMaxGRPCLogLength`, `Connect`, deprecated `ConnectWithoutMetrics`, options `OnConnectionLoss`, `ExitOnConnectionLoss`, `WithTimeout`, `WithMetrics`, `WithOtelTracing`, interceptor `LogGRPC`, `ExtendedCSIMetricsManager.RecordMetricsClientInterceptor`, and `RecordMetricsServerInterceptor`. Types include `Option`, `AdditionalInfo`, `AdditionalInfoKeyType`, and `ExtendedCSIMetricsManager`.

## Control Flow
`Connect` prepends a 30-second timeout and metrics option when provided, then calls `connect`. The internal function builds insecure blocking dial options with 1-second max backoff and no idle timeout, applies unary interceptors, normalizes absolute paths to `unix://`, and installs a custom Unix dialer that detects first connection loss and optionally disables reconnect. It dials in a goroutine and logs "Still connecting" every 10 seconds until dial completion. `LogGRPC` logs sanitized requests/replies and caps response length when configured. Metrics interceptors measure duration and record gRPC status, with optional migration label from context.

## State, Persistence, And Dependencies
Package-level state is `maxLogChar`. `ExitOnConnectionLoss` writes `/dev/termination-log` and exits via klog. Dependencies include grpc, klog, OpenTelemetry grpc instrumentation, csi-lib-utils metrics, and protosanitizer.

## Integration Points
CSI sidecars use this to talk to drivers. Metrics integrate with `metrics.CSIMetricsManager`; logging integrates with `protosanitizer` to avoid secret leakage.

## Risks And Test Signals
Blocking dial plus timeout controls startup behavior; `WithTimeout(0)` can wait indefinitely. Connection-loss callback is only supported for Unix addresses. The dialer uses closure state that assumes serialized dial behavior. Tests cover Unix path/prefix, timeout, reconnect/disconnect modes, metrics, and tracing.
