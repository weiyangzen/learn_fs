# sources/cloud-native/buildkit/client/client.go

## Purpose

This file implements construction and core plumbing for the BuildKit client: gRPC connection setup, credentials, tracing, dialer resolution, service accessors, readiness waiting, session dialing, and client options.

## Important APIs, Types, and Functions

- `Client` holds the gRPC connection and optional custom session dialer.
- `New` builds a client connection from an address and `ClientOpt` values.
- Service accessors: `ControlClient`, `ContentClient`, and `Dialer`.
- Lifecycle methods: `Wait` and `Close`.
- Client options include `WithContextDialer`, `WithCredentials`, `WithServerConfig`, `WithServerConfigSystem`, `WithTracerProvider`, `WithTracerDelegate`, `WithSessionDialer`, and `WithGRPCDialOption`.
- `loadCredentials` builds TLS transport credentials.
- `resolveDialer` maps connection-helper schemes to custom dialers.

## Control Flow and State

`New` starts with large default gRPC message sizes, scans options, merges TLS credential options, installs a custom context dialer or resolves one from the address, and configures tracing from explicit options or an existing span in the input context. It appends BuildKit gRPC error interceptors, optional custom dial options, and authority metadata. Empty addresses default to `appdefaults.Address`; `tcp://` addresses are converted to host form for grpc-go name resolution. It then dials and optionally sets up delegated tracing.

`loadCredentials` constructs a TLS config from system roots and/or a CA file, applies server name, and loads a client key pair when either cert or key is provided. `Wait` polls the control API `Info` endpoint until success, `Unimplemented`, context cancellation, or a non-retryable error. `Dialer` returns a hijacked session dialer over the control service.

Persistent state is the open gRPC connection and configured session dialer on the client object.

## Dependencies and Integration Points

The file depends on containerd defaults and content API, BuildKit control API, connection helpers, session hijacking, app defaults, tracing/OTLP plumbing, OpenTelemetry gRPC stats handlers, TLS/x509, and gRPC credentials/interceptors. Higher-level methods such as `Build`, `Solve`, `DiskUsage`, and cache operations all depend on clients created here.

## Risks and Edge Cases

`grpc.DialContext` is used despite deprecation warnings because behavior differs from newer APIs. Authority handling must align with TLS server name and address parsing. Supplying only cert or only key attempts to load both and returns a credential error. `Wait` treats `Unimplemented` as success for older BuildKit daemons. Tracer setup failure is ignored by design. Option merging allows later credential options to override earlier fields selectively.

## Test Signals

No direct tests for `client.go` are included in this subset. It is exercised indirectly by every integration test that calls `New`, `Wait`, service accessors, or `Close`.
