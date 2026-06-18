# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/values.yaml

Purpose: Default v4.0.0 chart values.

Important APIs/types/functions: `customLabels`, image settings, service account/RBAC names, driver `mountPermissions`, FSGroup/inline feature flags, `kubeletDir`, controller/node DNS policy, resources, tolerations, and imagePullSecrets.

Control flow: Values render image refs, scheduling, kubelet hostPath locations, CSIDriver features, service accounts/RBAC, and pod resources.

State and persistence: Helm release configuration and rendered Kubernetes resources.

Dependencies and integration points: Adds `kubeletDir` as a central integration point for node and controller templates.

Risks: Default `mountPermissions: 0777` and enabled FSGroup can alter security posture. `dnsPolicy: Default` with hostNetwork may not resolve cluster services. Test signals: render with kubeletDir override and validate DNS/PVC workflows.
