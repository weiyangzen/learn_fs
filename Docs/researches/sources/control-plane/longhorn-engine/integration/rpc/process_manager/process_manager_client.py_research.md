# sources/control-plane/longhorn-engine/integration/rpc/process_manager/process_manager_client.py

Purpose: hand-written gRPC convenience client for the process-manager service defined in `imrpc.imrpc_pb2(_grpc)`. It simplifies creating, inspecting, listing, deleting, and replacing managed processes.

Important APIs/types/functions: `ProcessManagerClient.__init__` opens an insecure channel and creates `ProcessManagerServiceStub`. `version_get` calls `VersionGet`. `process_create` validates `name` and `binary`, then sends `ProcessCreateRequest(ProcessSpec(...))`. `process_get`, `process_list`, `process_delete`, and `process_replace` wrap corresponding RPC methods; replace defaults to one listen port argument and `SIGHUP`.

Control flow: all methods are synchronous unary calls. Minimal local validation checks only required names and create binary; other argument semantics are deferred to the service.

State and persistence behavior: the client stores connection state only. Process lifecycle state is remote in the process-manager service.

Dependencies and integration points: depends on `grpc`, `google.protobuf.empty_pb2`, `imrpc.imrpc_pb2`, and `imrpc.imrpc_pb2_grpc`. It integrates with tests that drive process lifecycle through the instance manager.

Risks: mutable defaults (`port_args=[]` and `port_args=["--listen,localhost:"]`) can be mutated by callers. The insecure channel is intended for local test traffic. Validation is inconsistent: `process_replace` checks `name` but not `binary`, so errors may surface remotely.

Test signals: unit tests with a fake stub should verify validation failures, default port arguments, and protobuf field construction. Integration coverage should assert create/list/get/delete/replace behavior and signal propagation.
