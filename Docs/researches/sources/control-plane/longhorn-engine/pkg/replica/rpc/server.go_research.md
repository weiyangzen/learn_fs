# sources/control-plane/longhorn-engine/pkg/replica/rpc/server.go

Purpose: implements the gRPC management API for replica lifecycle, disk-chain operations, configuration flags, health checks, reflection, and profiling.

Important APIs/types/functions: `ReplicaServer` embeds the generated unimplemented server and holds a `*replica.Server`. `NewReplicaServer` registers replica service, health, reflection, and profiler with identity validation. `getReplica` converts server status and replica metadata to `enginerpc.Replica`. RPC methods cover create/delete/get/open/close/reload/revert/snapshot/expand, disk remove/replace/prepare/mark, rebuilding flag, revision counter, unmap-mark flag, and snapshot max settings. `ReplicaHealthCheckServer` implements gRPC health methods.

Control flow: handlers mostly validate required fields, call the corresponding `replica.Server` method, and return a fresh `getReplica` response. `ReplicaExpand` wraps errors as JSON-encoded Longhorn typed errors with `codes.Internal`. Health returns serving when the `ReplicaServer` has a non-nil `s` pointer, not when the underlying replica is open.

State and persistence: persistent effects happen inside `replica.Server`/`Replica`. gRPC server state is registration only.

Dependencies and integration points: used by replica process startup and `replica/client`. Depends on generated Longhorn protobufs, gRPC health/reflection, profiler RPC, interceptors, and replica package types.

Risks: most errors are raw Go errors except expand's typed JSON path, so client error handling is inconsistent. Health check does not reflect replica state error/closed conditions. `getReplica` ignores `DisplayChain` errors. Snapshot/revert require non-empty name/created but do not validate naming beyond replica internals.

Test signals: no direct tests in this subset. Client/server contract tests would cover protobuf conversion and error code consistency.
