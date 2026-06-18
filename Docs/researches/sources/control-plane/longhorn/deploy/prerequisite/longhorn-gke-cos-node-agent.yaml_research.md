<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-gke-cos-node-agent.yaml -->
# sources/control-plane/longhorn/deploy/prerequisite/longhorn-gke-cos-node-agent.yaml

Purpose: GKE COS node agent that prepares the containerized mounter rootfs for Longhorn data paths and keeps `iscsid` plus `iscsi_tcp` available.

Important APIs/types/functions: defines a ConfigMap containing `entrypoint.sh` and a privileged DaemonSet using `registry.suse.com/bci/bci-base:15.5`. Script functions include `mount_longhorn_data_dir_on_host`, `is_mounted_on_host`, `is_module_loaded_on_host`, `load_iscsi_tcp_module_on_host`, and `install_and_start_iscsid`.

Control flow: the DaemonSet mounts host `/` at `/host`, reads comma-separated `LONGHORN_DATA_PATHS`, creates paths in host and containerized mounter rootfs, bind-mounts and marks them shared, remounts the Longhorn path executable, installs open-iscsi with `zypper`, starts `/sbin/iscsid`, loads `iscsi_tcp`, then sleeps forever. Liveness and readiness probes verify `iscsid` and the kernel module through `nsenter`.

State and persistence: changes host mount namespace, host directories, package state inside the agent container/rootfs, running daemon state, and kernel module state. Kubernetes persists the ConfigMap and DaemonSet only.

Dependencies/integration points: depends on GKE COS layout `/home/kubernetes/containerized_mounter/rootfs`, privileged mount namespace access, `chroot`, `nsenter`, `findmnt`, `zypper`, `iscsid`, and `modprobe`. It integrates with Longhorn iSCSI attachment and data path access on COS nodes.

Risks/test signals: path assumptions are GKE/COS-specific; bad `LONGHORN_DATA_PATHS` or mount propagation can break data path visibility. Test signals are DaemonSet readiness, probe stability, `findmnt` output on host, loaded `iscsi_tcp`, running `iscsid`, and successful Longhorn volume attach on COS nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-gke-cos-node-agent.yaml -->
