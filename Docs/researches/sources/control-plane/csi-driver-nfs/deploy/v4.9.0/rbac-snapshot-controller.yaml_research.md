<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-snapshot-controller.yaml

## Purpose
Provides the permissions required by snapshot-controller v8.0.1 in the v4.9.0 manifest set.

## Important APIs, Types, and Functions
The manifest creates the `snapshot-controller` service account, `snapshot-controller-runner` cluster role and binding, plus `snapshot-controller-leaderelection` role and binding in `kube-system`. Rules cover PV/PVC reads, PVC update, event writes, snapshot class reads, snapshot content CRUD/status patch, snapshot update/patch, snapshot status update/patch, and lease CRUD.

## Control Flow, State, and Persistence
The controller uses cluster-level permissions to bind snapshot contents and namespace-scoped lease permissions to elect a single active reconciler. Snapshot object state is persisted in the Kubernetes API through spec/status updates.

## Dependencies and Integration Points
It integrates with the snapshot-controller deployment, snapshot CRDs, and CSI driver snapshotter sidecars. It applies cluster-wide, not just to NFS-related snapshots.

## Risks and Test Signals
Risks include status update denials causing stuck snapshots, broad delete authority on snapshot contents, and wrong namespace for leader-election RBAC. Signals are healthy lease acquisition, no forbidden errors, and snapshots reaching bound/ready status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-snapshot-controller.yaml -->
