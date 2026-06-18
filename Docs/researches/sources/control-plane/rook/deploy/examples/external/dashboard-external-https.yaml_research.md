<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/dashboard-external-https.yaml -->
# sources/control-plane/rook/deploy/examples/external/dashboard-external-https.yaml

Purpose: external-cluster variant of the Ceph dashboard HTTPS NodePort Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-external-https`, port/targetPort `8443`, active mgr selector labels, and `type: NodePort`.
Control flow: Kubernetes routes node-level HTTPS traffic to the active mgr dashboard endpoint for the external cluster representation. State is Service/endpoints. Dependencies are dashboard HTTPS availability and Rook external mgr service labeling. Risks: administrative exposure, self-signed certificates, and endpoint mismatch if external cluster labels differ. Test signals: endpoint exists, NodePort answers HTTPS, and dashboard login works through the imported cluster credentials.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/dashboard-external-https.yaml -->
