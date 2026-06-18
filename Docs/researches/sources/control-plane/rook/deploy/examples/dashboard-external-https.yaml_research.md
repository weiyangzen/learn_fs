<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-external-https.yaml -->
# sources/control-plane/rook/deploy/examples/dashboard-external-https.yaml

Purpose: exposes the Ceph manager dashboard HTTPS port with a `NodePort` Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-external-https`, port/targetPort `8443`, selector `app: rook-ceph-mgr`, `mgr_role: active`, `rook_cluster`, and `type: NodePort`.
Control flow: Kubernetes creates external node-level access to the active mgr dashboard HTTPS endpoint. State is Service/endpoints only; dashboard sessions remain in Ceph mgr. Dependencies are dashboard enabled on port 8443 and Rook active mgr labels. Risks: NodePort surface area, self-signed cert handling by clients, and endpoint loss during mgr failover. Test signals: endpoint exists, HTTPS request reaches dashboard, certificate/auth behavior is expected, and endpoints update after mgr failover.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-external-https.yaml -->
