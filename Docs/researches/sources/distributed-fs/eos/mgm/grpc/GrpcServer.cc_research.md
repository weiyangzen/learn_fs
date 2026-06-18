<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcServer.cc -->
# sources/distributed-fs/eos/mgm/grpc/GrpcServer.cc

## Purpose
`GrpcServer.cc` implements the main EOS MGM gRPC service under `EOS_GRPC`. It exposes namespace RPCs, command execution, ping, and traffic-shaping monitoring, and maps gRPC authentication material into EOS `VirtualIdentity` objects.

## Important APIs, types, and functions
`RequestServiceImpl` derives from generated `eos::rpc::Eos::Service`. It implements `Ping`, `FileInsert`, `ContainerInsert`, `MD`, `Find`, `NsStat`, `Exec`, and `TrafficShapingRate`. Namespace operations delegate to `GrpcNsInterface`. `TrafficShapingRate` streams `TrafficShapingRateResponse` reports built by `BuildTrafficShapingRateReport`.

Static helpers on `GrpcServer` are `DN`, `IP`, and `Vid`. `DN` reads x509 identity properties from the gRPC auth context. `IP` parses `context->peer()` into an IP address. `Vid` builds an `XrdSecEntity`, selects a non-secret tident (`DN`, `eostoken`, `grpc-key`, or `grpc-anon` plus peer data), optionally attaches the authkey as endorsements, and calls `Mapping::IdMap`.

`GrpcServer::Run` loads TLS material from `EOS_MGM_GRPC_SSL_CERT`, `EOS_MGM_GRPC_SSL_KEY`, and `EOS_MGM_GRPC_SSL_CA`, enforces TLS unless `EOS_MGM_GRPC_ALLOW_INSECURE` is present, configures gRPC credentials, registers the service, starts the server, and waits.

## Control flow
Each RPC logs peer/IP/DN, maps the caller to a `VirtualIdentity`, waits for MGM boot via `WAIT_BOOT` where needed, and delegates. `MD` switches on request type: file/container/stat use `GrpcNsInterface::Stat`, listing uses `GrpcNsInterface::StreamMD`, and unsupported types return `INVALID_ARGUMENT`. `TrafficShapingRate` maps without an auth key, requires root or sudoer, then loops until cancellation, emitting reports roughly every 100 ms.

Startup first attempts to load TLS files when all three TLS environment variables are set. Without TLS, startup is refused unless `EOS_MGM_GRPC_ALLOW_INSECURE` is set; insecure mode binds only `127.0.0.1`. TLS mode binds `0.0.0.0` and normally requires and verifies client certificates, unless `EOS_MGM_GRPC_DONT_REQUEST_CLIENT_CERTIFICATE` downgrades to token-only behavior. The service is registered and `mServer->Wait()` blocks until shutdown.

## State and persistence behavior
The server owns `mServer` and TLS strings. It does not persist data itself. RPCs can mutate namespace state through `GrpcNsInterface::{FileInsert,ContainerInsert,Exec}` and stream live monitoring state through traffic shaping. Identity mapping can depend on EOS mapping configuration and supplied auth keys/tokens.

## Dependencies and integration points
The file integrates generated `proto/Rpc.grpc.pb.h`, `GrpcNsInterface`, `Mapping`, `SymKey`, XRootD `XrdSecEntity`, `TrafficShaping`, gRPC reflection/credentials, and MGM boot macros. It relies on environment variables for transport security and on `Mapping::IdMap` for auth-to-VID conversion.

## Risks and edge cases
Transport security is central. The implementation now refuses public insecure binding unless explicitly allowed, and insecure mode is loopback-only. `EOS_MGM_GRPC_DONT_REQUEST_CLIENT_CERTIFICATE` is a deliberate downgrade and should be rare. `Vid` avoids logging raw auth keys by using a tident sentinel and only debug-level short fingerprints; regression tests should protect this because audit logs are otherwise a credential leakage vector.

`DN` looks for `x509_common_name` first and then SAN, despite the comment noting gRPC prioritization behavior; deployments relying on SAN identity should validate actual auth-context properties. `IP` parsing is duplicated with the REST server and can fail closed to an empty string for unexpected peer formats. `TrafficShapingRate` streams sensitive monitoring data and correctly requires admin/sudoer, but uses an empty authkey, so authorization is certificate/mapping driven only.

## Test signals
Unit tests should cover `DN`, `IP`, and `Vid` for mTLS, EOS token, SSS/shared-secret authkey, no auth, and malformed peer strings. Startup tests should verify TLS load failures, refusal without TLS, loopback-only insecure mode, and client-cert downgrade logging. RPC integration tests should cover MD type dispatch, namespace insert delegation, `Exec`, `Find`, and permission denial for `TrafficShapingRate`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcServer.cc -->
