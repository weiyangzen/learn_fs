## sources/control-plane/ceph-csi/internal/cephfs/groupcontrollerserver_test.go

Purpose: Unit tests for group snapshot create request validation.

Important APIs: `TestControllerServer_validateCreateVolumeGroupSnapshotRequest` constructs a `ControllerServer` with a default CSI driver and table-tests `validateCreateVolumeGroupSnapshotRequest`.

Control flow and state: Cases cover a valid request, empty name, empty source volume IDs, missing clusterID, and missing fsName. The test asserts expected gRPC status codes for invalid cases and runs subtests in parallel. No Ceph or Kubernetes state is used.

Dependencies and risks: Depends on CSI protobufs, `status.Code`, and csi-common default driver validation. It validates request shape but not quiesce, journaling, cleanup, delete, or multi-volume behavior. Test signal is useful for API-level parameter enforcement but leaves most group snapshot behavior to integration tests.
