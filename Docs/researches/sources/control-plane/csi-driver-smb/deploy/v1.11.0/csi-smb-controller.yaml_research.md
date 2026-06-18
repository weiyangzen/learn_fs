<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-controller.yaml

- Purpose: v1.11.0 static controller Deployment manifest for SMB CSI. It runs the external provisioner, liveness probe, and `smb` controller service against a shared CSI socket.
- Important APIs/types/functions: Kubernetes APIs `apps/v1`; kind `Deployment`; images include registry.k8s.io/sig-storage/csi-provisioner:v3.5.0, registry.k8s.io/sig-storage/livenessprobe:v2.10.0, registry.k8s.io/sig-storage/smbplugin:v1.11.0. Key flags include leader election, CSI socket address, health/metrics endpoints, and `--endpoint=$(CSI_ENDPOINT)`.
- Control flow: applying the manifest creates a kube-system Deployment. Sidecars talk to the SMB driver over `/csi/csi.sock`; the provisioner watches PVCs/StorageClasses and creates PVs; the resizer, when present, watches expansion requests; the SMB container exports CSI RPCs and metrics.
- State and persistence behavior: the pod uses an `emptyDir` socket volume and stores no durable controller data. Persistent state is Kubernetes PV/PVC objects, leader-election Leases, Events, and remote SMB directories.
- Dependencies/integration points: requires `csi-smb-controller-sa`, RBAC roles, CSI sidecar images compatible with the Kubernetes version, kube-system namespace, and the `CSIDriver` plus node DaemonSets.
- Risks: privileged SMB container, cluster-wide RBAC dependency, sidecar/image version skew, and leader-election namespace mismatch. Older versions use deprecated flags or v1beta1-era sidecars.
- Test signals: Deployment rollout, liveness endpoint, provisioner/resizer logs, PVC provisioning, expansion tests when resizer is included, and server-side dry-run.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/v1.11.0/csi-smb-controller.yaml -->
