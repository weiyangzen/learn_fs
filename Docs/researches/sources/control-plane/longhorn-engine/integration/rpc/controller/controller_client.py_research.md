# sources/control-plane/longhorn-engine/integration/rpc/controller/controller_client.py

## Purpose
This wrapper provides a small Python client over the generated Longhorn controller gRPC service for integration tests. It normalizes request construction and maps controller replica messages into lightweight Python objects.

## Important APIs, types, and functions
- `ControllerClient.__init__(url, volume_name=None, instance_name=None)` creates an insecure gRPC channel, applies `IdentityValidationInterceptor`, and builds a `ControllerServiceStub`.
- Volume APIs: `volume_get`, `volume_start`, `volume_shutdown`, `volume_snapshot`, `volume_revert`, `volume_expand`, `volume_frontend_start`, `volume_frontend_shutdown`, and `version_detail_get`.
- Replica APIs: `replica_list`, `replica_get`, `replica_create`, `replica_delete`, and `replica_update`.
- Other APIs: `metrics_get` and `client_upgrade`.
- `ControllerReplicaInfo` exposes `address` and string `mode` using `controller_pb2.ReplicaMode.Name`.

## Control flow
Each method builds the corresponding protobuf request and immediately invokes the generated stub. `replica_list` transforms the repeated controller response into `ControllerReplicaInfo` objects. `client_upgrade` replaces the client's address/channel/stub with a new insecure channel to support engine upgrade tests.

## State and persistence behavior
The client stores `address`, `channel`, and `stub` in memory. It does not own server state but can create/delete replicas, start/shutdown frontend and volumes, expand volumes, and change replica modes through RPC side effects. The identity interceptor may add validation metadata when volume/instance names are supplied.

## Dependencies and integration points
Depends on `grpc`, generated `ptypes.controller_pb2` and `controller_pb2_grpc`, `google.protobuf.empty_pb2`, and `common.interceptor.IdentityValidationInterceptor`. It is used broadly by data and instance integration tests to interact with live Longhorn engine controllers.

## Risks and edge cases
- `volume_snapshot` uses a mutable default `labels={}`; the method does not mutate it, but the pattern is risky if changed later.
- `client_upgrade` recreates a raw insecure channel without reapplying the identity interceptor or preserving identity parameters.
- `replica_update` builds nested `ControllerReplica`/`ReplicaAddress` messages manually; field-shape changes in generated protobufs would break it.
- No deadlines are set on RPCs, so hung controller calls can stall tests.

## Test signals
Signals include successful volume start/shutdown/expand/frontend operations, returned replica modes, correct address after upgrade, metrics/version retrieval, and expected gRPC errors in negative upgrade/revert paths.
