# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v3.0.0 node plugin DaemonSet.

Important APIs/types/functions: `DaemonSet`; livenessprobe, node-driver-registrar, and privileged NFS containers; values for node name, update strategy, tolerations, resources, log level, and image tags.

Control flow: Runs host-networked on Linux nodes. The registrar has a liveness probe using kubelet-registration-probe mode and registers the CSI socket; NFS serves the node CSI endpoint and mounts through bidirectional kubelet pod paths.

State and persistence: HostPath socket directory, plugin registry, and pod mount directory persist on each node.

Dependencies and integration points: Kubelet plugin registration, CSINode updates, and NFS mount lifecycle.

Risks: Hard-coded `/var/lib/kubelet`, privileged mount propagation, and cluster-wide DaemonSet blast radius. Test signals: DaemonSet rollout, kubelet registration, and workload pod using an NFS PVC.
