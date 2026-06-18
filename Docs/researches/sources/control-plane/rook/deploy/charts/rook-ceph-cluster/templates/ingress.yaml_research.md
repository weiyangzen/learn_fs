## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/ingress.yaml

Purpose: renders a Kubernetes Ingress for the Ceph dashboard when `.Values.ingress.dashboard.host` is configured.

Important template behavior: creates `Ingress` named `<clusterName>-dashboard`, applies optional labels/annotations, host/path/pathType, backend service `rook-ceph-mgr-dashboard`, backend port name `https-dashboard` when dashboard SSL is true or `http-dashboard` otherwise, optional ingressClassName, and optional TLS.

Control flow: single conditional on dashboard ingress host.

State and persistence: exposes the Ceph mgr dashboard through an ingress controller. It does not manage dashboard auth or the underlying service.

Dependencies and integration points: depends on Rook-created mgr dashboard service and ingress controller behavior. Risks: annotations must align with SSL backend behavior, especially for NGINX; only one ingress class mechanism should be used per values comments; exposing dashboard without proper TLS/auth policy is sensitive. Render tests should cover SSL true/false and TLS/class settings.
