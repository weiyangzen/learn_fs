<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-deployment.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-deployment.yaml

Purpose: Deployment for CephFS controller/provisioner service. It runs the controller plugin plus external-provisioner, snapshotter, optional attacher, optional resizer, optional CSI controller helper, and optional liveness metrics. Values drive replica count, anti-affinity, hostNetwork, images, sidecar args, HTTP metrics ports, feature gates, config mounts, memory key dir, and scheduling. Risks include sidecar/RBAC mismatch, multi-replica leader election, socket sharing, configMapKey mismatch, and privileged host mounts. Signals are Deployment readiness and successful provisioning/snapshot/resize/attach paths.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-deployment.yaml -->
