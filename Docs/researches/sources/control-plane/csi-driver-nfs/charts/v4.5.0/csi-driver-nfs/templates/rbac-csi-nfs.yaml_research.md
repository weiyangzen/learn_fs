# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose

This template creates service accounts and the controller ClusterRole/ClusterRoleBinding for the v4.5.0 NFS CSI chart.

## APIs, control flow, and state

It conditionally creates controller and node service accounts from `.Values.serviceAccount.*`, then conditionally creates a cluster role bound to the controller service account. The role grants PV/PVC/storageclass/csinode/node/event/lease/secret access needed by the external provisioner and driver. In v4.5.0, snapshot permissions are no longer conditional on `.Values.externalSnapshotter.enabled`; the controller service account always receives read/update/status access to `VolumeSnapshot*` resources.

## Dependencies and integration points

The controller deployment consumes the controller account for provisioning, snapshotter sidecar work, events, and leader election. The node DaemonSet consumes the node service account configured in values. The role assumes snapshot CRDs may exist even if this chart does not deploy the external snapshot-controller.

## Risks and test signals

Always granting snapshot permissions avoids broken snapshot sidecars but widens default RBAC in clusters not using snapshots. Cluster-wide Secret `get` remains sensitive. Test `kubectl auth can-i` for provisioning, leases, events, secrets, and snapshot resources, plus disabled `rbac.create` and custom service-account-name scenarios.
