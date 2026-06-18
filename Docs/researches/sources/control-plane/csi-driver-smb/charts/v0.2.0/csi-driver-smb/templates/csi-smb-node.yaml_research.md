## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the v0.2.0 Linux node DaemonSet, still close to v0.1.0 but coexisting with the new controller chart resources.

Important behavior: liveness probe health port 39613, registrar socket registration, privileged SMB plugin, Linux node selector, kubelet hostPath and plugin directories. State is node plugin pods and host mount state. Dependencies include legacy sidecar images and privileged mount propagation. Risks include fixed labels/ports, older liveness flag names, no resource settings, and no feature toggles. Test signal is Linux node registration and static/dynamic mount use.
