<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-http-service.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-http-service.yaml

Purpose: optional Service exposing nodeplugin liveness Prometheus metrics. It supports annotations, clusterIP, externalIPs, loadBalancerIP/source ranges, servicePort, target containerPort, selector labels, and service type. Risk is exposing metrics more broadly than intended or selector mismatch. Signal is metrics endpoint reachability.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-http-service.yaml -->
