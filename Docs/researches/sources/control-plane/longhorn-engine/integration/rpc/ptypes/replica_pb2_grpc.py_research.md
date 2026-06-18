# sources/control-plane/longhorn-engine/integration/rpc/ptypes/replica_pb2_grpc.py

Purpose: generated gRPC Python binding for `ptypes.ReplicaService`.

Important APIs/types/functions: `ReplicaServiceStub` exposes unary RPCs for replica lifecycle, snapshot/revert/expand, disk removal/replacement/preparation/marking, rebuild state, revision counter, unmap behavior, and snapshot max count/size settings. `ReplicaServiceServicer` is the unimplemented base. `add_ReplicaServiceServicer_to_server` registers handlers, and `ReplicaService` exposes experimental static methods.

Control flow: stub methods serialize request messages and deserialize reply messages. Server registration maps each method name to the concrete servicer callback with generated serializers.

State and persistence behavior: no local persistence. Stub instances retain channel callables; remote replica service implementations own replica state.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, and `ptypes.replica_pb2`. It is used by `replica_client.py` and any test server implementing replica RPCs.

Risks: request/response wrappers differ by method; several mutating operations return response messages containing `.replica`, while delete returns `Empty` and prepare remove returns operations. Client wrappers must unwrap correctly. Base methods are placeholders only.

Test signals: fake stub tests should assert wrapper clients call the correct generated methods. In-process server tests should verify handler registration and method paths under `/ptypes.ReplicaService/...`.
