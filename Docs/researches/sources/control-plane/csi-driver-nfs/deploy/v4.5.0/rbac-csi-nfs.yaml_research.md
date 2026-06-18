# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/rbac-csi-nfs.yaml

## Purpose
This file provides the v4.5.0 NFS CSI service accounts and controller authorization. It is byte-identical to the v4.4.0 and v4.6.0 RBAC in this subset.

## Important APIs, Types, and Functions
It creates `csi-nfs-controller-sa`, `csi-nfs-node-sa`, `nfs-external-provisioner-role`, and `nfs-csi-provisioner-binding`. The cluster role grants PV create/delete but not patch, PVC update, storage class reads, snapshot reads and snapshot content updates/status updates, event writes, CSINode/node reads, lease writes, and secret reads.

## Control Flow, State, and Persistence
The resources persist authorization policy for the v4.5.0 controller. Sidecar API calls are admitted or denied based on these rules during provisioning, snapshotting, eventing, and leader election.

## Dependencies and Integration Points
The controller deployment references `csi-nfs-controller-sa`; the node DaemonSet references `csi-nfs-node-sa`. Snapshot-related rules integrate with `snapshot.storage.k8s.io` CRDs and the `csi-snapshotter` sidecar.

## Risks and Test Signals
Risks include missing PV patch permissions for later provisioner behavior, broad secret read permissions, and cluster-scoped access. Test signals are clean sidecar logs, successful leader election leases, PV/PVC lifecycle operations, snapshot content status updates, and positive `kubectl auth can-i` checks for each required verb.
