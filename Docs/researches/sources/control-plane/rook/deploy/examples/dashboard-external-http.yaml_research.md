<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-external-http.yaml -->
# sources/control-plane/rook/deploy/examples/dashboard-external-http.yaml

Purpose: exposes the active Ceph manager dashboard HTTP port through a Kubernetes `NodePort` Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-external-http`, namespace `rook-ceph`, port/targetPort `7000`, selector labels `app: rook-ceph-mgr`, `mgr_role: active`, and `rook_cluster`.
Control flow: Kubernetes routes NodePort traffic to the active mgr pod matching the selector. State is only the Service object and endpoint slices derived from pod labels. Dependencies are a Ceph manager dashboard listening on HTTP port 7000 and Rook labels. Risks: HTTP exposure is unauthenticated transport unless dashboard itself enforces auth, active mgr label changes must update endpoints, and NodePort opens cluster nodes. Test signals: Service endpoints point to one active mgr, NodePort responds, and failover updates endpoints.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-external-http.yaml -->
