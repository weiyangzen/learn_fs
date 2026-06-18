<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpc.go -->
# sources/cloud-native/buildkit/session/grpc.go

Purpose: provides low-level gRPC-over-hijacked-connection support and health monitoring for BuildKit sessions.

Important APIs, types, and functions: `healthCheckConfig`, `defaultHealthCheckConfig`, `headerSessionHealthCustomTimeout`, `healthCheckConfigFromHeaders`, `serve`, `grpcClientConn`, and `monitorHealth`. `grpcClientConn` builds a one-connection gRPC client over a provided `net.Conn`, applies max message sizes, error interceptors, optional tracing stats, and starts health monitoring.

Control flow and state: health monitoring ticks every configured interval, runs gRPC health checks with adaptive timeout, counts consecutive failures/successes, and closes/cancels the connection after fatal failures. Custom test timeout header lowers interval/timeout but clamps to at least 1 second.

Dependencies and integration: uses containerd default message sizes, BuildKit tracing/error helpers, http2 server, OpenTelemetry gRPC instrumentation, and gRPC health checking. Called by session manager connection handling.

Risks and test signals: health checks can falsely fail under low bandwidth or heavy concurrency, so thresholds are intentionally tolerant. Dialer rejects more than one connection. Tests should cover custom timeout parsing, single-connection enforcement, tracing option path, and fatal health close behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/grpc.go -->
