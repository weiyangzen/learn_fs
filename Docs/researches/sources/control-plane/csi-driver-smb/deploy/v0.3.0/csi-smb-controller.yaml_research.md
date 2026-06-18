<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-controller.yaml

- Purpose: v0.3.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include mcr.microsoft.com/oss/kubernetes-csi/csi-provisioner:v1.4.0, mcr.microsoft.com/oss/kubernetes-csi/livenessprobe:v1.1.0, mcr.microsoft.com/k8s/csi/smb-csi:v0.3.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v0.3.0/csi-smb-controller.yaml -->
