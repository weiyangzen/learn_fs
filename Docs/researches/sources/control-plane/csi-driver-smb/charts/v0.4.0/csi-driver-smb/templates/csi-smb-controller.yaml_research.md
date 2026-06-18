## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-controller.yaml

Purpose: renders the v0.4.0 controller Deployment. It is close to v0.3.0, retaining provisioner, liveness probe, and SMB controller containers.

Important behavior: controller health port remains 29642, Linux scheduling remains fixed, and the chart gains small value-structure changes around node settings elsewhere. State is the Deployment and shared socket. Dependencies are old csi-provisioner/liveness sidecars and provisioner RBAC. Risks include no resizer, fixed deployment names, old sidecar flags, and privileged controller. Test signal is dynamic provisioning in v0.4.0 installs.
