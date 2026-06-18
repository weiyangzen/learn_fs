## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

Purpose: renders the v0.4.0 Windows node DaemonSet. It keeps the non-HostProcess architecture and adds minor value-driven node update controls.

Important behavior: liveness probe and registrar use health port 29643, SMB plugin runs with endpoint/nodeid, and hostPath/named pipe mounts integrate with CSI Proxy. State is Windows DaemonSet and host plugin directories. Dependencies include old Windows sidecars, beta CSI Proxy pipe paths, and Kubernetes Windows support. Risks include fixed kubelet path, old pipe names, no HostProcess option, and low configurability. Test signal is Windows node plugin readiness.
