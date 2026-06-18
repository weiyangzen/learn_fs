<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/dashboard-external-http.yaml -->
# sources/control-plane/rook/deploy/examples/external/dashboard-external-http.yaml

Purpose: external-cluster variant of the Ceph dashboard HTTP NodePort Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-external-http`, namespace `rook-ceph`, port `7000`, selector labels for active mgr, and `type: NodePort`.
Control flow: Kubernetes exposes the active mgr dashboard HTTP endpoint discovered/imported for the external cluster. State is Service/endpoints only. Dependencies are external cluster mgr dashboard service/pods represented by Rook labels and namespace consistency. Risks: HTTP administrative dashboard exposure, active mgr endpoint availability in external mode, and hard-coded namespace/cluster labels. Test signals: endpoints resolve, NodePort responds on port 7000, and active mgr failover updates endpoints.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/dashboard-external-http.yaml -->
