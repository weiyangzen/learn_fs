# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose

This template creates the service account and RBAC for the optional v4.6.0 external snapshot-controller deployment.

## APIs, control flow, and state

When `.Values.externalSnapshotter.enabled` is true, it renders a service account, cluster role, cluster role binding, release-namespace leader-election role, and role binding. Permissions cover PV/PVC reads and PVC updates, events, snapshot classes, snapshot contents including status, snapshots including status, and optional Node reads for distributed snapshotting. Leader-election state is stored in `coordination.k8s.io` leases in the release namespace.

## Dependencies and integration points

The RBAC is consumed by `csi-snapshot-controller.yaml` and depends on the snapshot API resources being present. It integrates with the same snapshot resources used by the NFS CSI snapshotter sidecar and by user `VolumeSnapshot` objects.

## Risks and test signals

Cluster-scoped snapshot permissions allow mutation across namespaces. The optional distributed snapshotting flag is not part of the default values file, so operators need explicit override knowledge. Test auth checks, enabled/disabled rendering, leader election, snapshot status writes, and behavior when CRDs are absent or managed externally.
