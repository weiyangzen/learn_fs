# sources/control-plane/external-snapshotter/pkg/snapshotter/snapshotter_test.go

Purpose: tests the CSI RPC wrapper using a mock CSI driver, validating request construction and returned values for create, delete, and list/status operations.

Important APIs/functions: `createMockServer`, `TestCreateSnapshot`, `TestDeleteSnapshot`, `TestGetSnapshotStatus`, and `FakeCSIVolume`. It uses gomock, csi-test mock servers, csi-lib-utils connection/metrics, protobuf matchers, and gRPC status injection.

Control flow: each test starts one mock CSI driver and gRPC connection, registers expected controller/identity RPCs, invokes a `NewSnapshotter` method, and compares errors and output values. Create tests include default, parameter, secret, transient error, and final error cases. Delete tests mirror secret and error cases. Status tests vary `LIST_SNAPSHOTS` support and list response/errors.

State and persistence: all backend state is mocked; no Kubernetes API state is touched. `FakeCSIVolume` supplies a CSI PV handle for request construction.

Dependencies and integration: validates the contract expected by sidecar controller `Handler` implementations and ensures CSI protobuf request shapes remain stable.

Risks and test signals: good signal for API-level CSI call correctness. It does not cover nil `rsp.Snapshot`, empty `ListSnapshots` response, group snapshot ID assertion, or connection lifecycle failures beyond initial connect.
