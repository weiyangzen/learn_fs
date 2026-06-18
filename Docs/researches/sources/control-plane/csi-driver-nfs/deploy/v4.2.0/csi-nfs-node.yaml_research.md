## sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-node.yaml

Purpose: Deploys the v4.2.0 NFS CSI node plugin as a DaemonSet on every Linux node. It registers `nfs.csi.k8s.io` with kubelet and performs node-side mount/publish operations for NFS-backed volumes.

Important APIs and types: The DaemonSet uses `hostNetwork: true`, `dnsPolicy: Default`, ServiceAccount `csi-nfs-node-sa`, Linux node selector, tolerates all taints, and uses rolling updates with `maxUnavailable: 1`. Containers are `livenessprobe:v2.8.0`, `csi-node-driver-registrar:v2.6.2`, and `nfsplugin:v4.2.0`. The registrar points kubelet at `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` and includes an exec liveness probe in kubelet-registration-probe mode. The NFS plugin is privileged with `SYS_ADMIN`, mounts `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/pods`, and `/var/lib/kubelet/plugins_registry`, and exposes health port 29653.

Control flow: On each node, the NFS plugin opens the CSI socket under the kubelet plugin directory. The node-driver-registrar connects to that socket and writes registration data into the kubelet plugin registry. Kubelet then calls NodePublish/NodeUnpublish against the socket for pods using NFS CSI volumes. The liveness sidecar checks socket/health state.

State and persistence behavior: DaemonSet state persists in Kubernetes. The CSI socket and plugin registration files persist on the node hostPath while the pod is running and are recreated after restart. Actual data persists on the remote NFS server; node-local mounts are under kubelet pod directories.

Dependencies and integration points: Requires kubelet plugin directories, Linux nodes with NFS client support, the matching `CSIDriver`, and controller-created PVs. Integrates with kubelet through the registrar and with pod volume lifecycle through hostPath mount propagation.

Risks: `dnsPolicy: Default` can break cluster-service NFS server names in node pods. Privileged mode and bidirectional mount propagation are required but high privilege. The registrar exec liveness probe uses old registrar behavior removed in later manifests. Nodes missing `/var/lib/kubelet/pods` or NFS utilities will fail mounts.

Test signals: Verify a DaemonSet pod on each target node, `CSINode` lists `nfs.csi.k8s.io`, kubelet plugin registration file exists, liveness probes pass, and a pod can mount/read/write an NFS CSI volume. Negative tests should cover bad DNS under host networking and absent NFS kernel/client support.
