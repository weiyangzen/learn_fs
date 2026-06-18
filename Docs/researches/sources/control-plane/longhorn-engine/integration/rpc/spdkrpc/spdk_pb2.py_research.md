# sources/control-plane/longhorn-engine/integration/rpc/spdkrpc/spdk_pb2.py

Purpose: generated protobuf definitions for SPDK engine/replica/disk/log/backup RPCs.

Important APIs/types/functions: data messages include `Lvol`, `Replica`, `Engine`, replica and engine create/delete/get/list/snapshot/rebuild requests, backup create/status/restore requests and responses, restore status maps, disk create/get/delete messages, log level/flag messages, and version output. Enum `ReplicaMode` contains `WO`, `RW`, and `ERR`. `SPDKService` descriptor covers replica lifecycle/watch/rebuild/backup/restore, engine lifecycle/watch/replica membership/backup/restore, disk management, log settings, and version detail. `ReplicaWatch` and `EngineWatch` are server-streaming RPCs.

Control flow: import-time descriptor registration only. The module defines schemas and service descriptors; concrete RPC transport would be in the matching generated gRPC file outside this work item.

State and persistence behavior: no local persistence. Messages represent SPDK logical volume, replica, engine, disk, and operation status state received from or sent to the remote SPDK service.

Dependencies and integration points: imports `empty_pb2` and protobuf builder internals. Integrates with SPDK-backed Longhorn instance management and with generated gRPC bindings/clients using `spdkrpc` package names.

Risks: many numeric storage sizes use unsigned/int64-like protobuf types while some related non-SPDK replica schemas use strings, so cross-client conversions need tests. Watch methods are streaming in the descriptor; clients must not treat every method as unary. Credentials are map fields and should be handled carefully in logs. Manual edits are fragile.

Test signals: descriptor tests for `SPDKService`, especially streaming flags for watch RPCs; serialization round trips for `Engine`, `Replica`, backup credentials, restore status maps, and disk messages; schema compatibility tests against SPDK service implementations.
