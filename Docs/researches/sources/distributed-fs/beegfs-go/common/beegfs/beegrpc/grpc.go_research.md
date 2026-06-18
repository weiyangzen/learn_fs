# sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/grpc.go

## Purpose
`grpc.go` provides common gRPC client connection setup for BeeGFS services, including target validation, TLS configuration, proxy control, custom CA certificates, and BeeGFS auth-secret metadata injection.

## APIs and Control Flow
Functional options populate `connOpts`: `WithTLSDisableVerification`, `WithTLSDisable`, `WithTLSCaCert`, `WithAuthSecret`, and `WithProxy`. `NewClientConn` rejects addresses containing URI schemes, requires `host:port` through `net.SplitHostPort`, applies `grpc.WithNoProxy` unless enabled, adds unary and stream interceptors that append `auth-secret` metadata when configured, then chooses insecure credentials or TLS credentials with system cert pool plus optional CA. It returns `grpc.NewClient(address, opts...)`.

## State, Dependencies, and Integration
The function is stateless outside option values. It depends on Go TLS/x509, net parsing, BeeGFS auth-secret generation, gRPC credentials, interceptors, and metadata. `NewMgmtd` reuses it for management clients.

## Risks and Test Signals
`TLSDisableVerification` sets `InsecureSkipVerify`, which is useful operationally but weakens security. Interceptors recompute the auth secret on each RPC. The explicit scheme rejection avoids gRPC resolver ambiguity. `grpc_test.go` covers IPv4, IPv6, invalid address diagnostics, and URI scheme rejection.
