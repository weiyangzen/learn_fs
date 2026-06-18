# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/values.yaml

Purpose: v4.1.0 default chart values.

Important APIs/types/functions: Images, serviceAccount controller name, RBAC name, driver features, kubeletDir, controller/node DNS, affinity, nodeSelector, tolerations, resources, and image pull secrets.

Control flow: Values drive image references, labels, scheduling, host paths, driver args, CSIDriver features, and RBAC/service account rendering.

State and persistence: Helm release configuration and rendered Kubernetes state.

Dependencies and integration points: Introduces control-plane scheduling flags and affinity/nodeSelector inputs for controller and node workloads.

Risks: `serviceAccount.node` is absent though the template creates a node account from `rbac.name`, limiting customization. Defaults still use `mountPermissions: 0777`. Test signals: render custom affinity/nodeSelector and verify pod placement.
