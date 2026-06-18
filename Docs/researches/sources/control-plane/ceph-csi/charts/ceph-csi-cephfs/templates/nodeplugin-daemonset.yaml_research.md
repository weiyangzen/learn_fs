<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-daemonset.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-daemonset.yaml

Purpose: DaemonSet for CephFS node service. It runs privileged `csi-cephfsplugin`, privileged node-driver-registrar, optional liveness/metrics container, hostNetwork/hostPID, kubelet hostPath mounts, `/dev`, `/sys`, `/run/mount`, `/lib/modules`, optional SELinux mount, config maps, memory key dir, and mountinfo hostPath. Args wire driver name, node ID, socket, mount options, read affinity, fencing, profiling, and slow-op logging. Risks are required host privileges, kubeletDir correctness, SELinux/socket access, and config map key mismatches. Signals are DaemonSet readiness, registrar socket registration, and mount workflows.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-daemonset.yaml -->
