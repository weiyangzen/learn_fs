# sources/control-plane/longhorn-engine/integration/rpc/ptypes/controller_pb2.py

Purpose: generated protobuf definitions for the Longhorn controller engine RPC API.

Important APIs/types/functions: message classes include `Volume`, `ReplicaAddress`, `ControllerReplica`, volume operation requests/replies, rebuild limit requests, `VersionOutput`, and `Metrics`. Enum `ReplicaMode` has `WO`, `RW`, and `ERR`. The embedded `ControllerService` descriptor defines volume lifecycle, snapshot, frontend, IO, replica membership/rebuild, journal, version, and metrics RPCs.

Control flow: import-time protobuf builder registration creates descriptors and Python message classes. No service implementation or business logic is present.

State and persistence behavior: descriptors live in the process descriptor pool. Message instances are caller-owned data carriers; controller state is remote.

Dependencies and integration points: imports `google.protobuf.empty_pb2` and `ptypes.common_pb2`. It is consumed by `controller_pb2_grpc.py` and any client/server code constructing controller requests.

Risks: the module includes generated map-entry internals and serialized offsets; manual edits are fragile. Field-name casing mixes protobuf styles (`replicaCount`, `last_expansion_error`), so callers must use generated Python names exactly. Schema drift against Go-generated Longhorn types can break integration.

Test signals: descriptor tests should verify the `ReplicaMode` values and `ControllerService` method signatures. Serialization round trips for representative `Volume`, `ControllerReplica`, and rebuild replies catch field regressions.
