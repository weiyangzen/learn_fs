# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates service accounts and the external-provisioner RBAC used by the v4.2.0 NFS CSI chart.

## Important APIs, Types, and Functions
With `serviceAccount.create`, it creates service accounts named `csi-{{ .Values.rbac.name }}-controller-sa` and `csi-{{ .Values.rbac.name }}-node-sa`. With `rbac.create`, it creates one `ClusterRole` and one `ClusterRoleBinding` for the external provisioner. Rules include PV create/delete, PVC update, storageclass reads, events, CSINodes, nodes, leases, and secret reads.

## Control Flow, State, and Persistence
Service account names are derived from `rbac.name`, not from `serviceAccount.controller`, even though values define a controller name. The cluster role persists cluster-wide and authorizes the controller-side provisioner through a binding to the derived controller service account.

## Dependencies and Integration Points
The controller Deployment uses `.Values.serviceAccount.controller`, whose default matches the derived service account only when `rbac.name` remains `nfs`. The node DaemonSet uses hard-coded `csi-nfs-node-sa`, also matching defaults only for the default RBAC name.

## Risks and Test Signals
The main risk is service account name drift if users customize `rbac.name` or `serviceAccount.controller`. Other risks are broad cluster permissions and absence of resizer/snapshot roles. Signals are rendered-name inspection, `kubectl auth can-i` as the controller SA, no provisioner forbidden logs, and PVC lifecycle tests.
