# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/values.yaml

Purpose: Default values for v3.0.0 chart.

Important APIs/types/functions: Image tags, serviceAccount/controller name, RBAC name, controller/node names and resources, tolerations, health ports, driver name, FSGroup feature flag, and image pull secrets.

Control flow: Values parameterize controller/node Deployments, RBAC naming, CSIDriver options, images, resources, and liveness ports.

State and persistence: Rendered resources persist in Kubernetes; values are Helm input and release configuration.

Dependencies and integration points: Moves to explicit controller/node naming and `registry.k8s.io`-era sidecar repositories from older defaults.

Risks: `enableFSGroupPolicy` default false may surprise users expecting fsGroup support; kubelet path remains hard-coded. Test signals: `helm template` with custom service account/RBAC names and node/controller rollout checks.
