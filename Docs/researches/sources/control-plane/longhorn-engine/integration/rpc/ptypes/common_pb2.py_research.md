# sources/control-plane/longhorn-engine/integration/rpc/ptypes/common_pb2.py

Purpose: generated protobuf message module for `ptypes/common.proto`. It provides shared message types used by controller and sync-agent RPC schemas.

Important APIs/types/functions: exports `DESCRIPTOR` and generated `SyncFileInfo` with fields `from_file_name`, `to_file_name`, and `actual_size`. The module uses `descriptor_pool.Default().AddSerializedFile` plus protobuf builder helpers to materialize classes.

Control flow: import-time descriptor registration builds the message and top-level symbols. There are no hand-written functions or branches.

State and persistence behavior: protobuf descriptors are registered in the process-global descriptor pool. The file itself persists no application state.

Dependencies and integration points: depends on `google.protobuf` descriptor, symbol database, and builder internals. `SyncFileInfo` is imported by controller rebuild replies and sync-agent file sync requests.

Risks: generated-code/runtime compatibility matters; protobuf runtime version changes can affect builder behavior. Manual edits will be overwritten. The serialized Go package option points to Longhorn engine RPC generated types, so schema drift can break cross-language compatibility.

Test signals: import the module, instantiate `SyncFileInfo`, serialize/deserialize it, and verify modules that import it (`controller_pb2`, `syncagent_pb2`) load under the expected `PYTHONPATH`.
