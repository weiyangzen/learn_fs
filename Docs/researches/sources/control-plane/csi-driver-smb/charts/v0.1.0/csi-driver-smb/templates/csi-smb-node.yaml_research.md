## sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the original Linux SMB node DaemonSet for chart v0.1.0. It deploys node liveness probe, node-driver-registrar, and SMB plugin on Linux nodes.

Important behavior: it hard-codes DaemonSet name `csi-smb-node`, namespace, labels, health port 39613, plugin socket under `/csi/csi.sock`, registration path under `/var/lib/kubelet/plugins/smb.csi.k8s.io/csi.sock`, and privileged SMB container with kubelet hostPath mount propagation.

State is Linux node plugin pods and kubelet hostPath directories. Dependencies include early sidecar images from `mcr.microsoft.com`, privileged mount propagation, and v0.1.0 image. Risks include limited configurability, old sidecar flags such as `--connection-timeout`, and no resource/security hardening. Test signal is node registration and mount success on old clusters.
