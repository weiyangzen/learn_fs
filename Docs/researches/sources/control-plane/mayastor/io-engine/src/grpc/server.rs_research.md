# sources/control-plane/mayastor/io-engine/src/grpc/server.rs

Purpose: this file owns process-local startup and shutdown of the tonic gRPC server. It builds a single `MayastorGrpcServer` instance, binds the TCP endpoint, and conditionally registers v0 and v1 service implementations based on the advertised `ApiVersion` list.

Important APIs/types/functions: `MayastorGrpcServer` stores an async-channel receiver/sender pair used as a termination signal. `get_or_init` initializes the global `OnceCell`, `fini` closes the sender, and `run` constructs service instances, binds `TcpIncoming`, wires generated `*Server` wrappers, and races server completion against the shutdown channel.

Control flow: `run` creates shared v1 `PoolService` and `ReplicaService` so stats, snapshot, snapshot-rebuild, and test services operate over the same lock contexts. Optional v1 services include bdev, json, pool, replica, test, snapshot, snapshot rebuild, host, nexus, and stats. Optional v0 services include mayastor, json, and bdev. `futures::select!` returns success on graceful shutdown, logs and returns an error on tonic server failure, or exits when the termination channel closes.

State and persistence: server state is in-memory only. Business persistence is delegated to service implementations. The static `OnceCell` means there is one server control channel per process, and closing `fini_chan` is a one-way shutdown signal.

Dependencies and integration points: integrates generated `io_engine_api` servers, `registration_grpc::ApiVersion`, tonic transport, and all gRPC service modules. It receives node identity, node NQN, endpoint, JSON-RPC address, and API-version selection from upper startup code.

Risks: service availability is controlled only by `api_versions.contains`; a misconfigured list silently omits an API generation. Binding errors are normalized to `AddrInUse`, which may hide other socket setup details. Shutdown closes the channel rather than using tonic graceful shutdown with per-request draining. Test signals should instantiate with v0-only, v1-only, and both versions, assert binding failure messages, and verify that shared services are cloned consistently.
