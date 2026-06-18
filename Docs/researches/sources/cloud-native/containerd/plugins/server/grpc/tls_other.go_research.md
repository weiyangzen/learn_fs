# sources/cloud-native/containerd/plugins/server/grpc/tls_other.go

## Purpose
Provides non-Windows no-op TLS resource cleanup hooks for the gRPC TCP server.

## Important APIs, Types, And Functions
`setTLSResource` and `cleanupTLSResources` accept/handle `wintls.CertResource` but do nothing.

## Control Flow
No-op functions are called from shared gRPC server code when Windows cert-store TLS is not active.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
Compiled under `!windows`; preserves shared code compatibility with Windows TLS helper types.

## Risks
None beyond ensuring no non-Windows resource cleanup is needed.

## Test Signals
No direct tests.
