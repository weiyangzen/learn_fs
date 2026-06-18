# sources/control-plane/csi-driver-host-path/examples/csi-groupsnapshot-v1beta1.yaml

## Purpose
This example demonstrates a v1beta1 VolumeGroupSnapshot request for the hostpath CSI driver.

## Important APIs, Types, And Functions
VolumeGroupSnapshot `new-groupsnapshot-demo` selects PVCs labelled `app.kubernetes.io/name: postgresql` and uses class `csi-hostpath-groupsnapclass`.

## Control Flow
The group snapshot controller calls the driver's group controller, which snapshots each selected source volume.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
