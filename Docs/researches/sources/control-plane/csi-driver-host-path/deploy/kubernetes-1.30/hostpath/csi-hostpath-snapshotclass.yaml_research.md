# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-snapshotclass.yaml

## Purpose
This manifest defines the default hostpath `VolumeSnapshotClass` used by snapshot examples and storage e2e tests. It binds snapshot requests to the hostpath CSI driver and deletes underlying snapshots when snapshot objects are deleted.

## Important APIs, Types, And Functions
The resource is `snapshot.storage.k8s.io/v1`, kind `VolumeSnapshotClass`, named `csi-hostpath-snapclass`. It sets `driver: hostpath.csi.k8s.io` and `deletionPolicy: Delete` with the standard deployment labels.

## Control Flow
When a `VolumeSnapshot` references this class, external-snapshotter routes the request to the hostpath driver's `CreateSnapshot`/`DeleteSnapshot` controller RPCs. DeletionPolicy `Delete` asks the snapshot controller to remove the backend snapshot via CSI.

## State, Persistence, And Dependencies
The class persists in Kubernetes. Actual snapshot archive files persist under the driver state directory until deleted. It depends on snapshot CRDs and compatible external-snapshotter deployment.

## Integration Points
It is referenced by `examples/csi-snapshot-v1.yaml`, block snapshot examples, and `test-driver.yaml` snapshot capability configuration. The driver name must match plugin and CSIDriver resources.

## Risks
The comment notes v1 snapshot API dependency on external-snapshotter v4.x or newer. A class/driver mismatch leaves snapshot requests unhandled. Delete policy can remove snapshot data during cleanup.

## Test Signals
Creating a VolumeSnapshot with this class should produce a ready snapshot, driver logs should show snapshot archive creation, and deletion should remove the corresponding `.snap` file and state entry.
