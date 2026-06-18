## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/values.yaml

Purpose: provides v0.5.0 values with updated sidecar repositories and versions. It sets SMB image v0.5.0, csi-provisioner v2.0.4, livenessprobe v2.1.0, node-driver-registrar v2.0.1, service accounts, controller replicas, node maxUnavailable, and Linux/Windows flags.

State is declarative chart configuration. Dependencies include registry.k8s.io sidecar availability and legacy SMB image repo. Risks include limited scheduling/resource customization, no resizer, old CSIDriver API in templates, and Windows defaults requiring CSI Proxy. Test signal is Helm render/install and provisioning.
