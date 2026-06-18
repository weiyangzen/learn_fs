## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the v0.6.0 controller Deployment for SMB dynamic provisioning. It is largely the same as v0.5.0, using provisioner v2.0.4, livenessprobe v2.1.0, and SMB controller image v0.6.0.

Important behavior: controller pods run on Linux, use the controller service account, share a CSI socket, and expose liveness on port 29642. State is Deployment pods and socket volume. Dependencies include provisioner RBAC and sidecar flag compatibility. Risks include no resizer, fixed names/ports, privileged SMB container, and old chart API choices. Test signal is v0.6.0 provisioning.
