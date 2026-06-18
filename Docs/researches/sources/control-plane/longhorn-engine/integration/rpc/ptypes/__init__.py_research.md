# sources/control-plane/longhorn-engine/integration/rpc/ptypes/__init__.py

Purpose: package marker for generated protobuf modules in `ptypes`.

Important APIs/types/functions: none directly; generated modules such as `common_pb2`, `controller_pb2`, `replica_pb2`, and `syncagent_pb2` provide the runtime API.

Control flow: no executable logic.

State and persistence behavior: no state and no persistence.

Dependencies and integration points: supports imports like `from ptypes import replica_pb2` used by RPC clients and generated gRPC files.

Risks: removing it can break imports in environments that do not treat this tree as a namespace package. Adding imports here may create ordering problems between generated protobuf modules.

Test signals: import smoke tests for every generated `ptypes` module.
