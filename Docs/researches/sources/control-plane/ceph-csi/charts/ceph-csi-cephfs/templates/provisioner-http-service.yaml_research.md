<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-http-service.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-http-service.yaml

Purpose: optional Service exposing provisioner liveness Prometheus metrics. It mirrors service customization for clusterIP/externalIPs/loadBalancer settings and selects provisioner pods. Risk is metrics exposure or selector mismatch. Signal is metrics endpoint reachability.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-http-service.yaml -->
