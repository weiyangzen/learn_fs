<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/client/controller_client_test.go -->
## sources/control-plane/longhorn-engine/pkg/controller/client/controller_client_test.go

Purpose: unit tests for defensive decoding in the controller client.

Important APIs/types/functions: `fakeClientConn` implements enough of grpc client connection behavior to fake `ControllerReplicaCreate` returning a malformed successful response. `TestGetControllerReplicaInfoRejectsMalformedResponses` checks nil and missing-address responses. `TestReplicaCreateRejectsMalformedReplicaResponse` verifies `ReplicaCreate` turns malformed payloads into decode errors.

Control flow and state: tests avoid real network by using generated client with `fakeClientConn`.

Dependencies and integration points: depends on `enginerpc`, `grpc`, `types`, and Go testing. It validates the client-side guard used by controller manager/CLI callers.

Risks: coverage is narrow to one malformed response class. The fake only supports one method, so other client methods are untested here.

Test signals: strong signal for the regression where rebuild storms yielded empty successful replica responses. Additional table tests could cover `ReplicaGet`, `ReplicaUpdate`, and list decoding.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/client/controller_client_test.go -->
