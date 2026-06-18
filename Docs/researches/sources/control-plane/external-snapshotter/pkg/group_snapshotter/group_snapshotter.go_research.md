# sources/control-plane/external-snapshotter/pkg/group_snapshotter/group_snapshotter.go

## Purpose
This package is the CSI RPC adapter for volume group snapshot operations. It exposes a small `GroupSnapshotter` interface that the sidecar/controller code can use without handling raw CSI generated clients directly.

## Important APIs, Types, And Functions
`GroupSnapshotter` defines `CreateGroupSnapshot`, `DeleteGroupSnapshot`, and `GetGroupSnapshotStatus`. `NewGroupSnapshotter(conn)` returns a `groupSnapshot` backed by a gRPC connection. `CreateGroupSnapshot` calls CSI Identity through `csirpc.GetDriverName`, then sends `CreateVolumeGroupSnapshotRequest`. `DeleteGroupSnapshot` sends `DeleteVolumeGroupSnapshotRequest`. `GetGroupSnapshotStatus` sends `GetVolumeGroupSnapshotRequest`.

## Control Flow
Each method constructs a `csi.GroupControllerClient` from the stored connection. Create first resolves the driver name and returns early on identity error, then sends source volume IDs, parameters, and secrets to CSI. It returns driver name, group snapshot ID, per-volume snapshots, creation time converted from protobuf timestamp, ready flag, and error. Delete and status calls pass group snapshot ID, individual snapshot IDs, and credentials directly to the CSI driver.

## State And Persistence Behavior
The adapter is stateless except for the gRPC connection. It does not cache driver names or snapshots and does not persist Kubernetes objects. All authoritative state comes from CSI responses and is returned to callers.

## Dependencies And Integration Points
The file depends on CSI generated Go types, `csi-lib-utils/rpc` for driver identity, gRPC, and klog. It integrates external-snapshotter group logic with CSI `GroupController` service methods.

## Risks
The implementation assumes CSI responses include non-nil `GroupSnapshot` and `CreationTime`; a nil response field could panic. It also fetches driver name on every create, which is simple but adds a dependency on Identity service availability for create operations. Context timeouts/cancellation are delegated to callers.

## Test Signals
`group_snapshotter_test.go` uses an in-process fake CSI server to cover success and RPC error paths for all methods, including custom timestamps and status codes.
