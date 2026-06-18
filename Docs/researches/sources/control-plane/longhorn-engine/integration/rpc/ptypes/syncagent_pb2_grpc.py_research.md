# sources/control-plane/longhorn-engine/integration/rpc/ptypes/syncagent_pb2_grpc.py

Purpose: generated gRPC binding for `ptypes.SyncAgentService`.

Important APIs/types/functions: `SyncAgentServiceStub` exposes unary methods for file remove/rename/send/sync, snapshot clone/export, receiver launch, backup create/remove/restore/status, reset, restore status, snapshot purge/status, replica rebuild status, snapshot clone status, snapshot hash/status/cancel, and hash lock state. It also provides unimplemented servicer base, server registration, and experimental static helpers.

Control flow: construction binds each `/ptypes.SyncAgentService/...` method to channel unary-unary callables. Registration maps servicer callbacks to deserializers and serializers.

State and persistence behavior: no durable local state. Remote sync-agent implementations own transfer, backup, restore, purge, rebuild, and hash operation state.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, and `ptypes.syncagent_pb2`. Integrates with sync-agent test services and any code monitoring long-running sync/backup operations.

Risks: many methods return `Empty` despite triggering long-running work; callers must separately poll status RPCs. Base servicer methods are placeholders. Generated mappings must remain synchronized with `syncagent_pb2.py`.

Test signals: in-process gRPC registration tests for every method path; client tests that start an operation and poll the matching status method; negative tests for unimplemented base methods.
