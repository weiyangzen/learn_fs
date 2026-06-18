# subset-b-000400 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/proxy_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/proxy_pb2_grpc.py

Purpose: generated gRPC Python binding for `imrpc.ProxyEngineService`. It exposes client stubs, server base methods, server registration, and experimental one-shot static RPC helpers for the proxy engine API used by Longhorn integration tests.

Important APIs/types/functions: `ProxyEngineServiceStub` binds unary-unary callables for `ServerVersionGet`, volume operations, snapshot operations, backup/restore operations, replica membership/rebuild/mode operations, `MetricsGet`, and `RemountReadOnlyVolume`. `ProxyEngineServiceServicer` declares matching methods that set `UNIMPLEMENTED` and raise until a concrete test server overrides them. `add_ProxyEngineServiceServicer_to_server` registers each method with exact request deserializers and response serializers. `ProxyEngineService` mirrors the methods through `grpc.experimental.unary_unary`.

Control flow: constructing a stub stores channel callables keyed by fully qualified paths such as `/imrpc.ProxyEngineService/VolumeGet`. Server registration builds a dictionary of `grpc.unary_unary_rpc_method_handler` entries, wraps them in `grpc.method_handlers_generic_handler`, and adds them to the supplied server. The file has no business branching beyond generated method wiring.

State and persistence behavior: the module holds no persistent state. Stub instances hold channel-bound RPC callables; servicer base methods do not mutate durable state.

Dependencies and integration points: depends on `grpc`, `google.protobuf.empty_pb2`, and `imrpc.proxy_pb2`. It is tightly coupled to the generated `proxy_pb2` message classes and to the service path namespace `imrpc.ProxyEngineService`.

Risks: any mismatch between `proxy.proto`, `proxy_pb2.py`, and this generated file breaks serialization at runtime. The base servicer is not usable without overrides. The experimental static helper API is less stable than normal stubs. Because this is generated code, manual edits are likely to be overwritten.

Test signals: import the module with the same `PYTHONPATH` used by integration tests; instantiate a stub against a fake/in-process gRPC channel; verify server registration exposes every expected method path; assert base servicer methods return `UNIMPLEMENTED`; use descriptor or golden-path tests to catch request/response type drift.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/proxy_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/instance/__init__.py -->
# sources/control-plane/longhorn-engine/integration/rpc/instance/__init__.py

Purpose: package marker for the `instance` RPC client package. The file is empty and exists so Python can import modules under `integration/rpc/instance` in environments that still rely on regular packages rather than namespace packages.

Important APIs/types/functions: no runtime API is defined here. The exported behavior is package importability for sibling modules such as `instance_client.py`.

Control flow: no executable statements.

State and persistence behavior: no module state and no persistence.

Dependencies and integration points: integrates with Python import resolution and with callers that import `instance.instance_client` or import from the `instance` package path.

Risks: adding side effects here would change package import behavior for integration tests. Removing the file may break older tooling or tests that expect a concrete package.

Test signals: package import smoke tests should include `import instance` and `from instance.instance_client import InstanceClient` under the repository's integration RPC `PYTHONPATH`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/instance/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/instance/instance_client.py -->
# sources/control-plane/longhorn-engine/integration/rpc/instance/instance_client.py

Purpose: hand-written convenience client for the generated instance-manager RPC API. It wraps `imrpc.instance_pb2_grpc.InstanceServiceStub` and builds protobuf request messages for integration tests or helper scripts.

Important APIs/types/functions: `InstanceClient.__init__` creates an insecure channel and an `InstanceServiceStub`. `version_get` sends `Empty`. `instance_create` builds `ProcessInstanceSpec`, `SpdkInstanceSpec`, and `InstanceSpec`, then calls `InstanceCreate`. `instance_get`, `instance_list`, and `instance_delete` wrap corresponding RPCs. `instance_replace` first calls `InstanceCreate` to obtain an instance spec/value, then passes it to `InstanceReplace` with a terminate signal.

Control flow: methods are synchronous pass-through RPC invocations. `instance_create` always constructs both process and SPDK spec submessages, even when only one backend type may be relevant. `instance_replace` has a two-step flow: create replacement spec via the service, then invoke replace.

State and persistence behavior: the client stores `address`, `channel`, and `stub`. Durable instance state is remote, owned by the instance-manager service, not by this client.

Dependencies and integration points: depends on `grpc`, `google.protobuf.empty_pb2`, `imrpc.instance_pb2`, and `imrpc.instance_pb2_grpc`. Integrates with instance-manager services that understand process-backed and SPDK-backed instance specs.

Risks: default mutable arguments (`port_args=[]`, `args=[]`, `replica_address_map={}`) can leak caller mutation across invocations if modified. The channel is insecure, appropriate for local integration tests but not for untrusted networks. Parameter name `type` shadows the Python built-in. There is little client-side validation, so malformed requests mostly fail remotely.

Test signals: use a fake stub to assert exact protobuf request construction, especially defaults and SPDK/process fields. Integration tests should cover create/get/list/delete/replace against a real or in-process service and confirm replace uses the requested terminate signal.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/instance/instance_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/process_manager/__init__.py -->
# sources/control-plane/longhorn-engine/integration/rpc/process_manager/__init__.py

Purpose: package marker for process-manager RPC helpers. It enables package-style imports for the `process_manager` directory.

Important APIs/types/functions: no classes, functions, constants, or side effects are defined.

Control flow: no executable logic.

State and persistence behavior: no state and no persistence.

Dependencies and integration points: participates only in Python import resolution for `process_manager.process_manager_client`.

Risks: deleting it may break tests or tools that do not support namespace-package discovery. Adding import side effects could make process-manager client imports slower or more fragile.

Test signals: import smoke coverage should include `import process_manager` and `from process_manager.process_manager_client import ProcessManagerClient`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/process_manager/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/process_manager/process_manager_client.py -->
# sources/control-plane/longhorn-engine/integration/rpc/process_manager/process_manager_client.py

Purpose: hand-written gRPC convenience client for the process-manager service defined in `imrpc.imrpc_pb2(_grpc)`. It simplifies creating, inspecting, listing, deleting, and replacing managed processes.

Important APIs/types/functions: `ProcessManagerClient.__init__` opens an insecure channel and creates `ProcessManagerServiceStub`. `version_get` calls `VersionGet`. `process_create` validates `name` and `binary`, then sends `ProcessCreateRequest(ProcessSpec(...))`. `process_get`, `process_list`, `process_delete`, and `process_replace` wrap corresponding RPC methods; replace defaults to one listen port argument and `SIGHUP`.

Control flow: all methods are synchronous unary calls. Minimal local validation checks only required names and create binary; other argument semantics are deferred to the service.

State and persistence behavior: the client stores connection state only. Process lifecycle state is remote in the process-manager service.

Dependencies and integration points: depends on `grpc`, `google.protobuf.empty_pb2`, `imrpc.imrpc_pb2`, and `imrpc.imrpc_pb2_grpc`. It integrates with tests that drive process lifecycle through the instance manager.

Risks: mutable defaults (`port_args=[]` and `port_args=["--listen,localhost:"]`) can be mutated by callers. The insecure channel is intended for local test traffic. Validation is inconsistent: `process_replace` checks `name` but not `binary`, so errors may surface remotely.

Test signals: unit tests with a fake stub should verify validation failures, default port arguments, and protobuf field construction. Integration coverage should assert create/list/get/delete/replace behavior and signal propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/process_manager/process_manager_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/__init__.py -->
# sources/control-plane/longhorn-engine/integration/rpc/ptypes/__init__.py

Purpose: package marker for generated protobuf modules in `ptypes`.

Important APIs/types/functions: none directly; generated modules such as `common_pb2`, `controller_pb2`, `replica_pb2`, and `syncagent_pb2` provide the runtime API.

Control flow: no executable logic.

State and persistence behavior: no state and no persistence.

Dependencies and integration points: supports imports like `from ptypes import replica_pb2` used by RPC clients and generated gRPC files.

Risks: removing it can break imports in environments that do not treat this tree as a namespace package. Adding imports here may create ordering problems between generated protobuf modules.

Test signals: import smoke tests for every generated `ptypes` module.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/common_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/ptypes/common_pb2.py

Purpose: generated protobuf message module for `ptypes/common.proto`. It provides shared message types used by controller and sync-agent RPC schemas.

Important APIs/types/functions: exports `DESCRIPTOR` and generated `SyncFileInfo` with fields `from_file_name`, `to_file_name`, and `actual_size`. The module uses `descriptor_pool.Default().AddSerializedFile` plus protobuf builder helpers to materialize classes.

Control flow: import-time descriptor registration builds the message and top-level symbols. There are no hand-written functions or branches.

State and persistence behavior: protobuf descriptors are registered in the process-global descriptor pool. The file itself persists no application state.

Dependencies and integration points: depends on `google.protobuf` descriptor, symbol database, and builder internals. `SyncFileInfo` is imported by controller rebuild replies and sync-agent file sync requests.

Risks: generated-code/runtime compatibility matters; protobuf runtime version changes can affect builder behavior. Manual edits will be overwritten. The serialized Go package option points to Longhorn engine RPC generated types, so schema drift can break cross-language compatibility.

Test signals: import the module, instantiate `SyncFileInfo`, serialize/deserialize it, and verify modules that import it (`controller_pb2`, `syncagent_pb2`) load under the expected `PYTHONPATH`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/common_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/common_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/ptypes/common_pb2_grpc.py

Purpose: generated gRPC companion for `ptypes/common.proto`. Because the proto defines only shared messages and no service, this file contains only the generated header/import of `grpc`.

Important APIs/types/functions: no stubs, servicers, registration functions, or experimental service helpers are exported.

Control flow: import-only module with no runtime RPC registration.

State and persistence behavior: no state and no persistence.

Dependencies and integration points: depends on `grpc` solely because the gRPC plugin emitted a companion file. It may be imported by code expecting every `*_pb2.py` to have a matching `*_pb2_grpc.py`.

Risks: its emptiness is intentional; adding service-like code here would not match the proto. Removing it can break generated import conventions.

Test signals: import smoke test is enough; service discovery should not expect handlers from this file.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/common_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/controller_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/ptypes/controller_pb2.py

Purpose: generated protobuf definitions for the Longhorn controller engine RPC API.

Important APIs/types/functions: message classes include `Volume`, `ReplicaAddress`, `ControllerReplica`, volume operation requests/replies, rebuild limit requests, `VersionOutput`, and `Metrics`. Enum `ReplicaMode` has `WO`, `RW`, and `ERR`. The embedded `ControllerService` descriptor defines volume lifecycle, snapshot, frontend, IO, replica membership/rebuild, journal, version, and metrics RPCs.

Control flow: import-time protobuf builder registration creates descriptors and Python message classes. No service implementation or business logic is present.

State and persistence behavior: descriptors live in the process descriptor pool. Message instances are caller-owned data carriers; controller state is remote.

Dependencies and integration points: imports `google.protobuf.empty_pb2` and `ptypes.common_pb2`. It is consumed by `controller_pb2_grpc.py` and any client/server code constructing controller requests.

Risks: the module includes generated map-entry internals and serialized offsets; manual edits are fragile. Field-name casing mixes protobuf styles (`replicaCount`, `last_expansion_error`), so callers must use generated Python names exactly. Schema drift against Go-generated Longhorn types can break integration.

Test signals: descriptor tests should verify the `ReplicaMode` values and `ControllerService` method signatures. Serialization round trips for representative `Volume`, `ControllerReplica`, and rebuild replies catch field regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/controller_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/controller_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/ptypes/controller_pb2_grpc.py

Purpose: generated gRPC Python binding for `ptypes.ControllerService`.

Important APIs/types/functions: `ControllerServiceStub` exposes unary-unary methods for volume get/start/shutdown/snapshot/revert/expand/frontend, snapshot limit settings, `VolumeIO`, replica list/get/create/delete/update/prepare/verify rebuild, rebuild sync limit get/set, `JournalList`, `VersionDetailGet`, and `MetricsGet`. `ControllerServiceServicer` is an unimplemented base. `add_ControllerServiceServicer_to_server` registers serializers/deserializers. `ControllerService` provides experimental static unary calls.

Control flow: stub construction binds channel callables to `/ptypes.ControllerService/...`. Server registration builds `grpc.unary_unary_rpc_method_handler` entries and attaches a generic handler to a server.

State and persistence behavior: no durable state. Stub instances keep channel method handles; server state belongs to concrete servicer implementations.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, and `ptypes.controller_pb2`. It is the Python transport layer for controller RPC integration tests.

Risks: generated request/response wiring must stay aligned with `controller_pb2.py`. The base servicer always returns `UNIMPLEMENTED`. The experimental static API should not be the primary extension point.

Test signals: import and stub-construction smoke tests; fake/in-process server tests for registration paths; golden tests for method-to-message mappings, especially mutating RPCs returning `Volume` versus `Empty`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/controller_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/replica_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/ptypes/replica_pb2.py

Purpose: generated protobuf definitions for replica-service RPC data structures and the `ReplicaService` descriptor.

Important APIs/types/functions: request/response types cover replica create/delete/get/open/close/reload/revert/snapshot/expand, disk remove/replace/prepare/mark, rebuilding flag, revision counter, unmap behavior, and snapshot count/size limits. State messages include `DiskInfo`, `Replica`, and `PrepareRemoveAction`.

Control flow: protobuf descriptors and classes are built at import time; no application logic exists in this module.

State and persistence behavior: process-global descriptors only. `Replica` and `DiskInfo` instances report remote replica state such as head, parent, chain, disks, revision counter, snapshot usage, and rebuild flags.

Dependencies and integration points: imports `google.protobuf.empty_pb2`. Consumed by `replica_pb2_grpc.py` and by `replica/replica_client.py`.

Risks: `ReplicaCreateRequest.size` is a string while expand and limits use integer fields, so tests should catch accidental type assumptions. Map-entry fields for disks, labels, and children depend on generated protobuf map behavior. Generated code should not be edited manually.

Test signals: instantiate key request/response messages, verify map fields and repeated chains round trip, and assert the service descriptor exposes all replica/disk/snapshot limit RPCs.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/replica_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/replica_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/ptypes/replica_pb2_grpc.py

Purpose: generated gRPC Python binding for `ptypes.ReplicaService`.

Important APIs/types/functions: `ReplicaServiceStub` exposes unary RPCs for replica lifecycle, snapshot/revert/expand, disk removal/replacement/preparation/marking, rebuild state, revision counter, unmap behavior, and snapshot max count/size settings. `ReplicaServiceServicer` is the unimplemented base. `add_ReplicaServiceServicer_to_server` registers handlers, and `ReplicaService` exposes experimental static methods.

Control flow: stub methods serialize request messages and deserialize reply messages. Server registration maps each method name to the concrete servicer callback with generated serializers.

State and persistence behavior: no local persistence. Stub instances retain channel callables; remote replica service implementations own replica state.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, and `ptypes.replica_pb2`. It is used by `replica_client.py` and any test server implementing replica RPCs.

Risks: request/response wrappers differ by method; several mutating operations return response messages containing `.replica`, while delete returns `Empty` and prepare remove returns operations. Client wrappers must unwrap correctly. Base methods are placeholders only.

Test signals: fake stub tests should assert wrapper clients call the correct generated methods. In-process server tests should verify handler registration and method paths under `/ptypes.ReplicaService/...`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/replica_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/syncagent_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/ptypes/syncagent_pb2.py

Purpose: generated protobuf definitions for sync-agent file transfer, snapshot clone, backup/restore, purge, rebuild-status, and snapshot-hash operations.

Important APIs/types/functions: messages include file remove/rename/send/sync requests, `FileLocalSync`, snapshot clone/export requests, backup create/remove/status/restore requests and responses, restore/purge/rebuild/clone status responses, and snapshot hash request/status/cancel/lock-state messages. `SyncAgentService` descriptor defines 21 unary RPCs.

Control flow: import-time descriptor registration only. The generated module provides schemas, not implementation.

State and persistence behavior: descriptors are process-global. Status response messages carry remote operation state such as progress, error, backup URL, current backup, corruption flag, and lock state.

Dependencies and integration points: imports `empty_pb2` and `ptypes.common_pb2` for `SyncFileInfo`. Used by `syncagent_pb2_grpc.py` and sync-agent clients/servers.

Risks: several map/repeated fields carry credentials, parameters, labels, and source-address maps; tests must avoid logging secrets. Long-running operation status is stringly typed (`state`, `error`), so schema alone does not enforce valid state transitions. Generated code is fragile to manual edits.

Test signals: descriptor tests for all service methods; serialization tests for credentials/parameters maps, `FilesSyncRequest.sync_file_info_list`, and status responses.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/syncagent_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/syncagent_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/ptypes/syncagent_pb2_grpc.py

Purpose: generated gRPC binding for `ptypes.SyncAgentService`.

Important APIs/types/functions: `SyncAgentServiceStub` exposes unary methods for file remove/rename/send/sync, snapshot clone/export, receiver launch, backup create/remove/restore/status, reset, restore status, snapshot purge/status, replica rebuild status, snapshot clone status, snapshot hash/status/cancel, and hash lock state. It also provides unimplemented servicer base, server registration, and experimental static helpers.

Control flow: construction binds each `/ptypes.SyncAgentService/...` method to channel unary-unary callables. Registration maps servicer callbacks to deserializers and serializers.

State and persistence behavior: no durable local state. Remote sync-agent implementations own transfer, backup, restore, purge, rebuild, and hash operation state.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, and `ptypes.syncagent_pb2`. Integrates with sync-agent test services and any code monitoring long-running sync/backup operations.

Risks: many methods return `Empty` despite triggering long-running work; callers must separately poll status RPCs. Base servicer methods are placeholders. Generated mappings must remain synchronized with `syncagent_pb2.py`.

Test signals: in-process gRPC registration tests for every method path; client tests that start an operation and poll the matching status method; negative tests for unimplemented base methods.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/ptypes/syncagent_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/replica/__init__.py -->
# sources/control-plane/longhorn-engine/integration/rpc/replica/__init__.py

Purpose: package marker for replica RPC client helpers.

Important APIs/types/functions: no direct API; `replica_client.py` provides the package's substantive client wrapper.

Control flow: no executable logic.

State and persistence behavior: no state and no persistence.

Dependencies and integration points: supports import paths such as `from replica.replica_client import ReplicaClient` under the integration RPC tree.

Risks: removal can break package imports in older tooling. Side effects added here would run for every replica client import.

Test signals: package import smoke test plus direct import of `ReplicaClient`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/replica/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/replica/replica_client.py -->
# sources/control-plane/longhorn-engine/integration/rpc/replica/replica_client.py

Purpose: hand-written convenience client for `ptypes.ReplicaService`, used by tests to manage a replica over gRPC.

Important APIs/types/functions: `ReplicaClient.__init__` creates an insecure channel, wraps it with `IdentityValidationInterceptor`, records `url` as `tcp://<address>`, and creates `ReplicaServiceStub`. Methods wrap create/delete/get/open/close/reload/snapshot/expand, disk remove/prepare/mark, rebuild flag setting, and unmap mark-disk-chain-removed setting. Most methods unwrap response `.replica`.

Control flow: each method is a synchronous unary RPC wrapper. Identity validation is enabled only when volume and instance names are provided to the interceptor; defaults disable it.

State and persistence behavior: local state is limited to address/channel/url/stub. Replica disk/snapshot/rebuild state is remote and reflected in returned `Replica` messages.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, `ptypes.replica_pb2`, `ptypes.replica_pb2_grpc`, and `common.interceptor.IdentityValidationInterceptor`. Integrates with identity-aware Longhorn RPC servers.

Risks: `replica_snapshot` uses mutable default `labels={}`. Insecure channel is intended for local integration tests. Wrapper coverage is partial compared with the full generated service; for example disk replace, revision counter, and snapshot max setters are not exposed here.

Test signals: fake-stub unit tests for request construction and response unwrapping; interceptor tests for metadata when volume/instance names are supplied; integration tests against a replica service for create/open/snapshot/remove workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/replica/replica_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/smrpc/smrpc_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/smrpc/smrpc_pb2.py

Purpose: generated protobuf definitions for share-manager RPCs.

Important APIs/types/functions: exports `FilesystemTrimRequest` with `encrypted_device` boolean and a `ShareManagerService` descriptor with `FilesystemTrim`, `Unmount`, and `Mount` unary RPCs.

Control flow: import-time descriptor registration builds message and service descriptors. No implementation logic exists.

State and persistence behavior: only protobuf descriptors are registered. Mount/trim state is remote in the share-manager service.

Dependencies and integration points: imports `google.protobuf.empty_pb2`; consumed by `smrpc_pb2_grpc.py` and share-manager RPC clients/servers.

Risks: small schema means changes are easy to miss without descriptor tests. The generated Go package option ties it to Longhorn share-manager types. Manual edits are overwritten.

Test signals: import and instantiate `FilesystemTrimRequest`; descriptor test for the three service methods and their request/response types.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/smrpc/smrpc_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/smrpc/smrpc_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/smrpc/smrpc_pb2_grpc.py

Purpose: generated gRPC Python binding for `ShareManagerService`.

Important APIs/types/functions: `ShareManagerServiceStub` provides unary callables for `FilesystemTrim`, `Unmount`, and `Mount`. `ShareManagerServiceServicer` is the unimplemented server base. `add_ShareManagerServiceServicer_to_server` registers handlers. `ShareManagerService` exposes experimental static unary helpers.

Control flow: stub construction binds `/ShareManagerService/...` channel methods. Server registration maps each method to its request deserializer and response serializer.

State and persistence behavior: no local persistent state. Actual mount/unmount/trim state belongs to a concrete share-manager service.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, and `smrpc.smrpc_pb2`. Integrates with tests that exercise share-manager filesystem operations.

Risks: service path has no package prefix in the method string, unlike `ptypes.*` and `imrpc.*` generated services. That path difference matters for clients and test servers. Base servicer methods always return `UNIMPLEMENTED`.

Test signals: in-process server registration for all three paths; client call tests for request/response serialization; base-servicer negative tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/smrpc/smrpc_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/spdkrpc/spdk_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/spdkrpc/spdk_pb2.py

Purpose: generated protobuf definitions for SPDK engine/replica/disk/log/backup RPCs.

Important APIs/types/functions: data messages include `Lvol`, `Replica`, `Engine`, replica and engine create/delete/get/list/snapshot/rebuild requests, backup create/status/restore requests and responses, restore status maps, disk create/get/delete messages, log level/flag messages, and version output. Enum `ReplicaMode` contains `WO`, `RW`, and `ERR`. `SPDKService` descriptor covers replica lifecycle/watch/rebuild/backup/restore, engine lifecycle/watch/replica membership/backup/restore, disk management, log settings, and version detail. `ReplicaWatch` and `EngineWatch` are server-streaming RPCs.

Control flow: import-time descriptor registration only. The module defines schemas and service descriptors; concrete RPC transport would be in the matching generated gRPC file outside this work item.

State and persistence behavior: no local persistence. Messages represent SPDK logical volume, replica, engine, disk, and operation status state received from or sent to the remote SPDK service.

Dependencies and integration points: imports `empty_pb2` and protobuf builder internals. Integrates with SPDK-backed Longhorn instance management and with generated gRPC bindings/clients using `spdkrpc` package names.

Risks: many numeric storage sizes use unsigned/int64-like protobuf types while some related non-SPDK replica schemas use strings, so cross-client conversions need tests. Watch methods are streaming in the descriptor; clients must not treat every method as unary. Credentials are map fields and should be handled carefully in logs. Manual edits are fragile.

Test signals: descriptor tests for `SPDKService`, especially streaming flags for watch RPCs; serialization round trips for `Engine`, `Replica`, backup credentials, restore status maps, and disk messages; schema compatibility tests against SPDK service implementations.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/spdkrpc/spdk_pb2.py -->
