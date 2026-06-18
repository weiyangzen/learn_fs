<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/sync/sync_agent_client.py -->
## sources/control-plane/longhorn-engine/integration/rpc/sync/sync_agent_client.py

Purpose: small Python integration-test client for the Longhorn sync agent gRPC service.

Important APIs/types/functions: `SyncAgentClient.__init__` opens an insecure gRPC channel, wraps it with `IdentityValidationInterceptor`, and creates `SyncAgentServiceStub`. `replica_rebuild_status` calls `ReplicaRebuildStatus`. `sync_files` converts tuples into `common_pb2.SyncFileInfo` and invokes `FilesSync`. `file_send` invokes `FileSend`.

Control flow: methods construct protobuf request messages and synchronously call the stub. `sync_files` hardcodes `to_host='localhost'` and translates tuple fields `(from_file_name, to_file_name, actual_size)`.

State and persistence: instance state is limited to address, channel, intercepted channel, and stub. No filesystem writes.

Dependencies and integration points: depends on generated `ptypes.common_pb2`, `ptypes.syncagent_pb2`, `ptypes.syncagent_pb2_grpc`, `google.protobuf.empty_pb2`, and `common.interceptor.IdentityValidationInterceptor`. It integrates with sync-agent server tests and identity-validation tests.

Risks: channel is insecure and intended for local/integration use. Only a subset of service methods is implemented. Tuple-shaped sync file inputs are brittle and lack validation. Hardcoded localhost target may not cover remote topology tests.

Test signals: comment states it exists for `test_validation_fails_with_client`; additional coverage should exercise identity validation, tuple conversion, and timeout propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/sync/sync_agent_client.py -->
