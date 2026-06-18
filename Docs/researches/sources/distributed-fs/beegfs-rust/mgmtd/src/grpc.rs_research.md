<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc.rs

Purpose: declares and serves the mgmtd management gRPC API, wiring protobuf RPC methods to handler modules and applying TLS/authentication/shutdown/license guard helpers.

Important APIs/types/functions: `ManagementService { app }` implements `pm::management_server::Management` via `shared::impl_grpc_handler!`. `serve()` builds the tonic server, configures TLS unless disabled, attaches an `auth-secret` metadata interceptor, binds on IPv4/IPv6 unspecified address, and spawns graceful serving. `fail_on_pre_shutdown()` and `fail_on_missing_license()` centralize handler preconditions.

Control flow: each RPC is macro-generated to call a same-named async handler module, log context, and map errors. `serve()` reads certificate/key files if TLS is enabled, rejects missing/mismatched auth metadata when auth is configured, and shuts down via `RunStateHandle`.

State and persistence: no direct DB writes here; handlers perform state changes. Server state is the cloned `RuntimeApp`, TLS identity, and auth secret.

Dependencies and integration points: bridges `protobuf::management`, tonic, shared gRPC utilities, `RuntimeApp`, license verification, DB modules, and all `grpc/*` handlers.

Risks: disabling TLS logs a warning but still serves. Authentication compares a hashed `AuthSecret` from request metadata; clients must send exact metadata bytes. Handler availability during pre-shutdown depends on each handler calling the helper.

Test signals: handler modules contain focused tests. Additional integration tests should cover TLS file failures, auth metadata rejection, and generated handler error-code mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc.rs -->
