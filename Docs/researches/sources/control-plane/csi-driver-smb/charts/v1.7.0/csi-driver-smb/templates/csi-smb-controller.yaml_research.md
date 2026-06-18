<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
# Research: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-controller.yaml

- Purpose: Helm template for the v1.7.0 controller Deployment. It renders the Linux-only `csi-smb-controller` control-plane pod with the external provisioner, liveness probe, and `smb` CSI controller container wired to a shared `/csi/csi.sock` socket.
- Important APIs/types/functions: emits `apps/v1` `Deployment`; consumes `.Values.controller`, `.Values.image`, `.Values.serviceAccount.controller`, `.Values.driver.name`, pod labels/annotations, pull secrets, affinity, tolerations, and optional security context. The generated containers use `csi-provisioner`, `liveness-probe`, and `smb` images from chart values.
- Control flow: Helm renders values into container args, then Kubernetes starts the sidecars. The provisioner talks to the driver over `/csi/csi.sock`, uses leader election in the release namespace, and creates metadata; the SMB container runs `--endpoint=$(CSI_ENDPOINT)`, exports metrics, and serves health checks.
- State and persistence behavior: controller state is limited to an `emptyDir` CSI socket volume. Provisioned volumes persist in Kubernetes PV/PVC objects and remote SMB shares, not in this pod. `workingMountDir` defaults to `/tmp` and is used only for temporary controller-side share mounts.
- Dependencies/integration points: Kubernetes scheduling, Helm release namespace, CSI external-provisioner, CSI liveness probe, the SMB plugin image, RBAC from the companion chart template, and optional image pull secrets. Metrics integrate through the configured controller metrics port.
- Risks: the `smb` container is privileged, leader-election RBAC must match the namespace, and incorrect image repository prefix handling can render non-pullable images. Controller DNS policy, master/control-plane node selectors, and tolerations can accidentally pin the pod to unsuitable nodes.
- Test signals: validate with `helm template` plus `kubectl apply --dry-run=server`; runtime health is visible via `/healthz`, controller metrics, and provisioner events during PVC creation.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.7.0/csi-driver-smb/templates/csi-smb-controller.yaml -->
