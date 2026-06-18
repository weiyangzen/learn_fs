## sources/control-plane/ceph-csi/examples/rbd/groupsnapshot.yaml

Purpose: Example `VolumeGroupSnapshot` selecting RBD PVCs by label for group snapshot creation.

Important API surface: `apiVersion: groupsnapshot.storage.k8s.io/v1beta2`, `kind: VolumeGroupSnapshot`, metadata name `rbd-groupsnapshot`, selector `matchLabels.group: test`, and `volumeGroupSnapshotClassName: csi-rbdplugin-groupsnapclass`.

Control flow and state: The group snapshot controller resolves PVCs with the label, invokes the RBD CSI group snapshot capability, and persists snapshot state in Kubernetes `VolumeGroupSnapshot` and backend Ceph snapshot/group metadata. The selected PVC label is provided by `pvc.yaml`.

Dependencies and risks: Requires the group snapshot CRDs/controller, RBD group snapshot support, and `groupsnapshotclass.yaml`. Selector-based inclusion risks accidental snapshots of any PVC labeled `group=test`. Test by applying labeled PVCs and verifying the group snapshot reports ready and contains expected members.
