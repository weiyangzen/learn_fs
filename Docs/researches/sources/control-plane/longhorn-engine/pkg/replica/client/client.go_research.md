# sources/control-plane/longhorn-engine/pkg/replica/client/client.go

Purpose: provides the Go client wrapper used by controllers/tasks to call replica and sync-agent gRPC services.

Important APIs/types/functions: `ReplicaClient` stores replica and sync-agent URLs, host, volume name, and instance name. `NewReplicaClient` normalizes the replica gRPC address and derives sync-agent address as replica port plus two. Lazy contexts `ReplicaServiceContext` and `SyncServiceContext` hold `grpc.ClientConn`, generated clients, and a custom `util.Once`. Conversion helpers map protobuf disk/replica/sync-file records into engine `types`. Methods cover replica lifecycle (`GetReplica`, `OpenReplica`, `CloseReplica`, `ReloadReplica`, `ExpandReplica`), disk operations, rebuild/sync file operations, backup create/status/remove/restore, restore reset/status, purge/clone/hash operations, and hash lock state.

Control flow: each RPC method lazily initializes the appropriate gRPC client, creates a context with either a common 3-minute timeout or long 24-hour/custom timeout, sends a generated protobuf request, and wraps errors with operation context. File sync and clone methods support custom gRPC timeout seconds. `SyncFiles` populates both modern `FromAddressMap` and deprecated `FromAddress` for backward compatibility.

State and persistence: client state is connection state only. Server-side methods mutate replica files, backups, restore status, and snapshot hash jobs.

Dependencies and integration points: depends on generated `enginerpc`, gRPC insecure credentials, identity metadata client interceptor, `types`, and `util.GetGRPCAddress`. It is the central typed API used by sync tasks and controllers.

Risks: sync-agent port derivation assumes a fixed port layout. `Close` ignores individual close errors. All connections use insecure transport; identity metadata is validation, not encryption/authentication. Many operations intentionally omit `instanceName` in callers that do not know it, weakening server identity validation. Long default timeouts can hide stuck operations.

Test signals: no direct tests in this file. Behavior is indirectly exercised by higher-level sync/replica tests and would benefit from fake gRPC server tests for conversion, timeouts, and error wrapping.
