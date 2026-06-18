# sources/control-plane/longhorn-engine/integration/rpc/ptypes/syncagent_pb2.py

Purpose: generated protobuf definitions for sync-agent file transfer, snapshot clone, backup/restore, purge, rebuild-status, and snapshot-hash operations.

Important APIs/types/functions: messages include file remove/rename/send/sync requests, `FileLocalSync`, snapshot clone/export requests, backup create/remove/status/restore requests and responses, restore/purge/rebuild/clone status responses, and snapshot hash request/status/cancel/lock-state messages. `SyncAgentService` descriptor defines 21 unary RPCs.

Control flow: import-time descriptor registration only. The generated module provides schemas, not implementation.

State and persistence behavior: descriptors are process-global. Status response messages carry remote operation state such as progress, error, backup URL, current backup, corruption flag, and lock state.

Dependencies and integration points: imports `empty_pb2` and `ptypes.common_pb2` for `SyncFileInfo`. Used by `syncagent_pb2_grpc.py` and sync-agent clients/servers.

Risks: several map/repeated fields carry credentials, parameters, labels, and source-address maps; tests must avoid logging secrets. Long-running operation status is stringly typed (`state`, `error`), so schema alone does not enforce valid state transitions. Generated code is fragile to manual edits.

Test signals: descriptor tests for all service methods; serialization tests for credentials/parameters maps, `FilesSyncRequest.sync_file_info_list`, and status responses.
