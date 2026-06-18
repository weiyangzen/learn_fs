# sources/control-plane/external-snapshotter/pkg/snapshotter/snapshotter.go

Purpose: wraps raw CSI controller RPCs behind the sidecar's `Snapshotter` interface for create, delete, and status lookup operations against a CSI driver connection.

Important APIs/types/functions: `Snapshotter` interface, concrete `snapshot`, `NewSnapshotter`, `CreateSnapshot`, `DeleteSnapshot`, `isListSnapshotsSupported`, and `GetSnapshotStatus`. Return values include driver name, snapshot ID, creation time, restore size, ready flag, group snapshot ID, and errors.

Control flow: `CreateSnapshot` resolves the driver name with `csi-lib-utils/rpc.GetDriverName`, builds a `CreateSnapshotRequest`, forwards parameters and secrets, and unwraps the CSI `Snapshot`. `DeleteSnapshot` sends `DeleteSnapshotRequest`. `GetSnapshotStatus` first asks `ControllerGetCapabilities`; if `LIST_SNAPSHOTS` is absent it assumes the snapshot exists and ready, otherwise it calls `ListSnapshots` by ID and reads the first entry.

State and persistence: the wrapper is stateless aside from holding a `grpc.ClientConn`; persistence happens in the external CSI backend and later in Kubernetes CRD status by the controller.

Dependencies and integration: depends on CSI protobufs, gRPC, csi-lib-utils RPC helpers, and klog. It is consumed by the sidecar controller handler layer.

Risks and test signals: risks include nil CSI response fields, assuming ready when `ListSnapshots` is unsupported, repeatedly querying capabilities per status call, and using only the first list result. Tests cover create/delete requests with parameters/secrets, transient/final gRPC errors, list capability gating, list credentials, and missing list support fallback.
