# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: Helm template for the NFS CSI node DaemonSet that registers the driver and performs node-side mounts.

Important APIs and types: creates an `apps/v1` DaemonSet with configurable update strategy, node placement, service account, priority, resources, and image values. Containers are `liveness-probe`, `node-driver-registrar`, and privileged `nfs`. Optional host mount option propagation mounts `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d`.

Control flow: the NFS driver listens on a hostPath CSI socket under `.Values.kubeletDir/plugins/csi-nfsplugin`; the registrar publishes that socket via kubelet plugin registration path. The driver mounts kubelet pods directory with bidirectional propagation and reports liveness on the configured port. Host networking is enabled to preserve NFS connections.

State and persistence: creates host directories under kubelet plugin and plugin registry paths, mounts host pods directory, and optionally host NFS config files. The DaemonSet persists one pod per eligible Linux node.

Dependencies and integration: depends on kubelet plugin registration, RBAC/service account, image values, node OS selectors, and host NFS utilities in the container image.

Risks: privileged `SYS_ADMIN` and hostPath mounts create a broad node security boundary. Incorrect `kubeletDir` breaks registration or mount propagation. Host mount option propagation may create files/directories on the host.

Test signals: DaemonSet rollout, node-driver-registrar health, `CSINode` driver entries, pod volume mounts, and liveness probes.
