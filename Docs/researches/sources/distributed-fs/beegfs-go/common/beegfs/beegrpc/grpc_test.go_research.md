# sources/distributed-fs/beegfs-go/common/beegfs/beegrpc/grpc_test.go

## Purpose
This Go test suite verifies gRPC target validation behavior in `beegrpc.NewClientConn`.

## Important Tests
`TestNewClientConnAcceptsValidIPv4` and `TestNewClientConnAcceptsValidIPv6` start local gRPC servers and expect connections to loopback `host:port` addresses with TLS disabled. `TestNewClientConnRejectsInvalidAddresses` checks missing ports, malformed IPv6, empty address, error text, IPv6 guidance, and wrapping of `*net.AddrError`. `TestNewClientConnRejectsURIScheme` ensures `dns:///...` style addresses are rejected.

## Dependencies and Integration
Tests use Go's `net`, `testing`, `errors.As`, and gRPC server/client packages. IPv6 is skipped when unavailable.

## Signals and Gaps
The suite strongly documents address validation. It does not test TLS CA handling, auth-secret metadata injection, proxy toggling, or actual RPC execution over the returned connection.
