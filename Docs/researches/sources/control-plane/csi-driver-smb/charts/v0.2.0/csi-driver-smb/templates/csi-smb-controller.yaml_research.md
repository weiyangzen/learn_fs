## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: introduces the controller Deployment for dynamic provisioning in chart v0.2.0. It runs external provisioner, liveness probe, and SMB controller sharing a CSI socket.

Important behavior: hard-coded deployment name `csi-smb-controller`, Linux node selection, controller service account, provisioner sidecar from values, liveness health port 29632, and privileged SMB container with endpoint and driver name. State is controller pods and socket `emptyDir`. Dependencies include v1.4.0 provisioner and RBAC template. Risks include older liveness flags, no resizer sidecar, fixed ports, and limited scheduling/resource configuration. Test signal is dynamic provisioning on v0.2.0 installs.
