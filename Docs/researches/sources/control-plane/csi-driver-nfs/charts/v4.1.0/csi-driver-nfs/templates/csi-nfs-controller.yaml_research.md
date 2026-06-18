# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v4.1.0 controller Deployment with affinity/nodeSelector customization.

Important APIs/types/functions: `Deployment`; Helm `tpl`/`contains` affinity branch, values for `runOnControlPlane`, `runOnMaster`, `controller.affinity`, `controller.nodeSelector`, DNS policy, service account, images, and resources.

Control flow: If explicit affinity contains nodeSelectorTerms it is used; otherwise run-on-control-plane/master booleans synthesize required node affinity. The pod then runs provisioner, liveness, and privileged NFS containers.

State and persistence: Kubelet pod hostPath and CSI socket; cluster PV/PVC/event/lease state through sidecars.

Dependencies and integration points: RBAC, CSIDriver, node scheduling labels/taints, kubeletDir.

Risks: String-based affinity detection is fragile. Scheduling booleans do not apply when custom affinity is set. Test signals: render each scheduling branch and run Helm unit/dry-run checks.
