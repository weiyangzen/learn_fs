# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-snapshotter.yaml

## Purpose
This manifest deploys the external CSI snapshotter sidecar as a separate StatefulSet for the split Kubernetes 1.30 test deployment. It turns Kubernetes VolumeSnapshot controller events into CSI snapshot RPCs.

## Important APIs, Types, And Functions
The resource is `StatefulSet` `csi-hostpath-snapshotter`, service account `csi-snapshotter`, image `registry.k8s.io/sig-storage/csi-snapshotter:v8.2.0`, arguments `-v=5` and `--csi-address=/csi/csi.sock`, and a privileged mount of the hostpath driver socket directory.

## Control Flow
Pod affinity colocates it with the plugin. After startup it connects to `/csi/csi.sock` and calls snapshot RPCs for VolumeSnapshotContent lifecycle events.

## State, Persistence, And Dependencies
Snapshot state is coordinated through Kubernetes snapshot CRDs and the driver's JSON state plus `.snap` files. The manifest depends on external-snapshotter RBAC, installed CRDs, and socket availability.

## Integration Points
It works with `csi-hostpath-snapshotclass.yaml`, snapshot examples, restore examples, and controller server snapshot methods. Deploy script version parsing uses this file to derive snapshotter RBAC path.

## Risks
Snapshot CRD/RBAC version skew is a frequent failure mode. The sidecar is privileged for socket access. Because hostpath snapshots are `tar` or file copies, large volumes can make snapshot RPCs slow and block the driver's serialized state mutex.

## Test Signals
Snapshot creation and deletion should progress to ready/deleted states, restore PVCs should be populated, and logs should show calls to `CreateSnapshot`, `ListSnapshots`, and `DeleteSnapshot`.
