<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-ingress-https.yaml -->
# sources/control-plane/rook/deploy/examples/dashboard-ingress-https.yaml

Purpose: ingress example for routing HTTPS traffic to the Ceph dashboard through nginx ingress and ACME TLS.
Important APIs/types/functions: `networking.k8s.io/v1` `Ingress`, `ingressClassName: nginx`, TLS host `rook-ceph.example.com`, service backend `rook-ceph-mgr-dashboard` port `https-dashboard`, and nginx annotations for HTTPS backend and disabled upstream cert verification.
Control flow: the ingress controller terminates external TLS for the configured host, then proxies to the dashboard Service over HTTPS while skipping backend certificate verification. State persists in the Ingress and TLS Secret; routing state is maintained by the ingress controller. Dependencies are the internal dashboard Service, nginx ingress, DNS, and ACME/cert-manager if used. Risks: `proxy_ssl_verify off` trusts the backend blindly, placeholder host/secret must be replaced, and ingress only works if the dashboard Service exists. Test signals: ingress admitted, TLS secret issued, host resolves, and browser reaches the dashboard.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-ingress-https.yaml -->
