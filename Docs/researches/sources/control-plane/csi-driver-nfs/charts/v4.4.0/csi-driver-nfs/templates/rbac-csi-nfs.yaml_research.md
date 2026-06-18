# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose

This template creates service accounts and cluster RBAC for the NFS CSI controller and node components. It is guarded by `.Values.serviceAccount.create` for service accounts and `.Values.rbac.create` for the `ClusterRole`/`ClusterRoleBinding`.

## APIs, control flow, and state

When service-account creation is enabled, the template creates controller and node `ServiceAccount` resources in the release namespace. When RBAC is enabled, it creates a cluster role named `${rbac.name}-external-provisioner-role` and binds it to the controller service account. The role grants PV create/delete/list/watch, PVC list/watch/update, StorageClass and CSINode reads, Node reads, events writes, lease operations for leader election, and Secret reads.

In v4.4.0, snapshot permissions are conditionally included only when `.Values.externalSnapshotter.enabled` is true. Those permissions cover `VolumeSnapshotClass`, `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotContent/status` access needed by the provisioner/snapshot sidecar path.

## Dependencies and integration points

The controller deployment uses the controller service account for provisioning, snapshotting, event recording, and leader election. The node DaemonSet uses the node service account, but node-specific permissions are minimal here because kubelet registration happens through host paths.

## Risks and test signals

Conditional snapshot RBAC can break the always-present `csi-snapshotter` sidecar if snapshot CRDs are installed but the external snapshot-controller is disabled. Secret read access is cluster-wide and should be justified by provisioning needs. Test with `kubectl auth can-i --as system:serviceaccount:<ns>:<controller-sa>` for PV/PVC, leases, events, secrets, and snapshot resources under enabled/disabled snapshot settings, plus provisioning and snapshot workflows.
