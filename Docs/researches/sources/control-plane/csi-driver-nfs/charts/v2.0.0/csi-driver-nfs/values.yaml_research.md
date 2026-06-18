# sources/control-plane/csi-driver-nfs/charts/v2.0.0/csi-driver-nfs/values.yaml

Purpose: Minimal default configuration for the v2.0.0 CSI NFS chart.

Important APIs/types/functions: Image repository/tag/pullPolicy for NFS plugin, external-provisioner, livenessprobe, and node-driver-registrar; booleans `serviceAccount.create` and `rbac.create`; `controller.replicas`.

Control flow: Templates consume these values for image references, controller replica count, and optional service account/RBAC rendering.

State and persistence: Values drive rendered Kubernetes resources but are not runtime state themselves.

Dependencies and integration points: All repositories are under `k8s.gcr.io/sig-storage`, matching the era of v2 sidecars.

Risks: Sparse configurability leaves kubelet paths, names, scheduling, RBAC names, and driver name hard-coded. Registry migration from `k8s.gcr.io` may affect pulls. Test signals: `helm template` with custom image tags and install smoke on a compatible Kubernetes version.
