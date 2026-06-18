# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/rbac-snapshot-controller.yaml

## Purpose
This file authorizes the v4.6.0 snapshot controller. It is identical to the snapshot-controller RBAC files in v4.4.0, v4.5.0, and v4.7.0.

## Important APIs, Types, and Functions
It creates a `snapshot-controller` service account, a `snapshot-controller-runner` cluster role and binding, and a `snapshot-controller-leaderelection` role and binding. Permissions include PV/PVC reads, PVC update, event writes, snapshot class reads, snapshot content create/read/update/delete/patch plus status patch, snapshot update/patch plus status update/patch, and lease lifecycle verbs.

## Control Flow, State, and Persistence
Kubernetes authorization uses these resources while the snapshot controller reconciles custom resources and coordinates active leadership. The role binding is namespaced for the lease but the main snapshot permissions are cluster-scoped.

## Dependencies and Integration Points
It depends on snapshot CRDs and is referenced by the service account in `csi-snapshot-controller.yaml`. It integrates with the NFS CSI stack through shared snapshot resources that the NFS snapshotter fulfills.

## Risks and Test Signals
Risks include status updates failing if subresource verbs are incomplete, wrong lease namespace, and delete authority on snapshot contents. Test signals are successful leader election, event writes, snapshot content creation/deletion, status updates, and no authorization errors in logs.
