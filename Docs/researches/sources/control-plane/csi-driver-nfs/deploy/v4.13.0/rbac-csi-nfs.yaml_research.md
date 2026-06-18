<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-csi-nfs.yaml

## Purpose
Defines NFS CSI service accounts and controller RBAC for the v4.13.0 manifests.

## Important APIs, Types, And Objects
Creates `csi-nfs-controller-sa` and `csi-nfs-node-sa`. The provisioner ClusterRole grants PV lifecycle writes, PVC updates, StorageClass reads, snapshot class/snapshot reads, snapshot content/status updates, event writes, CSINode/node reads, Lease operations, and Secret reads. The resizer ClusterRole grants PV update/patch, PVC and PVC status access, events, and Leases. Both bind to the controller service account.

## Control Flow
Updated v4.13.0 sidecars use these permissions to watch and mutate Kubernetes storage objects while reconciling provisioning, expansion, reclaim, snapshots, events, and election.

## State And Persistence Behavior
RBAC resources persist cluster policy. They authorize the controller to write durable Kubernetes storage and snapshot state but do not hold runtime state themselves.

## Dependencies And Integration Points
Must match service account names in `csi-nfs-controller.yaml` and `csi-nfs-node.yaml`. Snapshot-related rules require snapshot CRDs and are used by `csi-snapshotter:v8.4.0`.

## Risks And Edge Cases
The same broad controller permissions from v4.12.x remain, including Secret get. Sidecar major version bumps in v4.13.0 should be checked against RBAC requirements; missing new permissions would appear as forbidden errors. The node service account remains unbound to explicit roles.

## Test Signals
Run `kubectl auth can-i` for all key provisioner/resizer/snapshotter operations as `csi-nfs-controller-sa`. Execute PVC create/delete, expansion, snapshot creation, and reclaim tests under v4.13.0 sidecars.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-csi-nfs.yaml -->
