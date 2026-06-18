## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-node.yaml

Purpose: renders the Linux SMB node DaemonSet. It deploys liveness probe, node-driver-registrar, and privileged SMB node plugin on Linux nodes.

Important behavior: the template supports node affinity, host networking, DNS policy, node service account, Linux nodeSelector, priority class, pod security context, tolerations, pull secrets, and resource blocks. The registrar can expose its own liveness endpoint. The SMB container sets driver name, endpoint, node id, get-volume-stats, and Kerberos prefix; it mounts `/csi`, kubelet with bidirectional propagation, and optional Kerberos cache directory.

State includes kubelet plugin and registration host paths, mount propagation state, optional Kerberos cache host path, and DaemonSet pods. Dependencies include privileged containers, kubelet path, sidecar images, RBAC, and Linux CIFS tooling in the image. Risks include privileged host mount access, Kerberos directory misconfiguration, socket path conflicts, and liveness settings causing restarts during slow mounts. Test signal is Linux e2e and node registration success.
