## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/values.yaml

Purpose: supplies v0.4.0 chart values, adding a `node` section on top of image, serviceAccount, controller, linux, and windows settings.

Important defaults include SMB image v0.4.0, csi-provisioner v1.4.0, livenessprobe v1.1.0, node-driver-registrar v1.2.0, controller replicas, node maxUnavailable, and Linux/Windows enabled flags. State is declarative Helm input. Risks include old sidecars, no resource/security settings, no resizer, and legacy registry locations. Test signal is Helm render/install.
