# sources/control-plane/csi-driver-host-path/examples/csi-app-inline.yaml

## Purpose
This example demonstrates an inline CSI ephemeral-style pod volume for the hostpath CSI driver.

## Important APIs, Types, And Functions
Pod `my-csi-app-inline` mounts a `csi` volume with driver `hostpath.csi.k8s.io` at `/data` in a busybox container and pins scheduling to nodes with topology key `topology.hostpath.csi/node`.

## Control Flow
Kubelet calls `NodePublishVolume` directly with CSI volume context, and the driver can create an ephemeral volume when configured or when Kubernetes passes ephemeral context.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
