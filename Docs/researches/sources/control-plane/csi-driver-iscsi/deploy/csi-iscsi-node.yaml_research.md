## sources/control-plane/csi-driver-iscsi/deploy/csi-iscsi-node.yaml

Purpose: deploys the iSCSI CSI node plugin as a privileged Linux DaemonSet with liveness and node-driver-registrar sidecars, plus a ConfigMap wrapper for host `iscsiadm`.

Control flow is Kubernetes declarative scheduling. The pod uses host networking, mounts kubelet plugin and registration directories, `/dev`, the host root, a writable run directory, and a ConfigMap-provided `/sbin/iscsiadm` that chroots into the host to find and run host iSCSI tools. The main container serves `/csi/csi.sock` and exposes a health port checked by the liveness sidecar.

State and persistence are hostPath directories, kubelet registration sockets, iSCSI sessions/devices on the host, and `/var/run/iscsi.csi.k8s.io` connector JSON files. Dependencies include privileged Linux nodes, host open-iscsi tooling, sidecar images, mount propagation, and kubelet plugin registration. Risks are high privilege, host root/device access, stale sidecar image versions, hostNetwork necessity, and failure when host `iscsiadm` paths differ. Test signal includes install scripts, Pluto, yamllint, and runtime Kubernetes rollout.
