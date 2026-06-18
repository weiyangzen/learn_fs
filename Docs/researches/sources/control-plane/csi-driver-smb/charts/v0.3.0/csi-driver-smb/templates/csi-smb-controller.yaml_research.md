## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the v0.3.0 controller Deployment for dynamic SMB provisioning. It is structurally similar to v0.2.0 but uses the later controller health port 29642.

Important behavior: external provisioner, liveness probe, and privileged SMB controller share `/csi/csi.sock`; sidecars and service accounts come from values; Linux node scheduling is fixed. State is controller pod and socket volume. Dependencies are csi-provisioner v1.4.0, livenessprobe v1.1.0, and RBAC. Risks include no resizer, old sidecar flags, fixed names/ports, and no scheduling/resource knobs beyond values booleans. Test signal is provisioning success in v0.3.0.
