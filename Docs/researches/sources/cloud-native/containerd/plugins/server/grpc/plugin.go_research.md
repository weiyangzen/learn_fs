# sources/cloud-native/containerd/plugins/server/grpc/plugin.go

## Purpose
Registers the main local gRPC server and optional TCP gRPC server, wiring registered service plugins, namespace interceptors, telemetry, message size limits, and TLS.

## Important APIs, Types, And Functions
`config` controls local endpoint settings. `tcpConfig` controls TCP/TLS settings. `grpcServer` and `tcpServer` implement server lifecycle. Init registers `grpc` and `grpc-tcp` server plugins.

## Control Flow
Local server init validates address, builds interceptor and stats options from metrics plugins, configures message size limits, creates a gRPC server, iterates all initialized gRPC plugins and calls `Register`, initializes Prometheus metrics, and returns `grpcServer`. TCP init skips without address, builds similar options, configures file-based TLS or Windows cert-store TLS, registers only services supporting `RegisterTCP`, requires at least one, and returns `tcpServer`.

## State And Persistence
No persistent state. It owns gRPC server instances, local/TCP listeners, and optional cached Windows TLS resources.

## Dependencies And Integration Points
Requires gRPC and metrics plugins. Integrates with `pkg/sys.GetLocalListener`, `internal.Serve`, TLS credentials, Windows TLS helper, Prometheus/OTEL plugins, and all service plugins implementing registration interfaces.

## Risks
Iterating all plugins intentionally ignores failed service plugin instances. TLS configuration must be correct for TCP exposure. `TLSCName` path uses Windows cert-store resources that need cleanup. Empty local address is invalid while empty TCP address skips.

## Test Signals
No direct tests in this subset; daemon startup and service integration tests cover registration.
