## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the Linux controller Deployment for SMB CSI. It hosts external provisioner, external resizer, liveness probe, and the `smb` controller service sharing a unix CSI socket.

Important behavior: supports explicit affinity or `runOnControlPlane`/`runOnMaster` node affinity, host networking, DNS policy, service account, Linux nodeSelector, security context, tolerations, pull secrets, and resource values. Sidecars use leader election in the release namespace, extra create metadata, VolumeAttributesClass disabled, retry tuning, and volume-in-use resize handling disabled. The driver container exposes metrics, liveness, driver name, endpoint, and working mount directory.

State is Deployment pods plus ephemeral socket `emptyDir`. Dependencies include Kubernetes sidecar images, SMB plugin image, RBAC, service accounts, and host networking. Risks include privileged controller container, Recreate strategy causing control-plane downtime, feature-gate pinning, and tight coupling to sidecar CLI flags. Test signal is Helm lint/render and dynamic provisioning/resize tests.
