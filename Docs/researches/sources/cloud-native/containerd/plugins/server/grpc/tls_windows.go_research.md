# sources/cloud-native/containerd/plugins/server/grpc/tls_windows.go

## Purpose
Stores and releases Windows certificate-store TLS resources used by the TCP gRPC server.

## Important APIs, Types, And Functions
Package variable `tlsResource` holds a `wintls.CertResource`. `setTLSResource` caches it. `cleanupTLSResources` closes it and logs failures.

## Control Flow
When TCP gRPC config uses a Windows certificate common name, setup stores the returned resource. Server close calls cleanup, which closes and clears the resource if present.

## State And Persistence
State is a process-global cached certificate resource handle. No file persistence.

## Dependencies And Integration Points
Windows-only; integrates with `internal/wintls` and `grpc-tcp` server shutdown.

## Risks
Global single-resource storage assumes one TCP server instance. Cleanup failures are logged but not returned from server close.

## Test Signals
No direct tests.
