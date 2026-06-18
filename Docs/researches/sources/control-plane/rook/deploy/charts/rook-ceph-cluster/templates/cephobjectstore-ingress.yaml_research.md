## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore-ingress.yaml

Purpose: renders Kubernetes Ingress resources for Ceph RGW object stores with ingress exposure enabled.

Important template behavior: iterates `.Values.cephObjectStores` and checks `ingress.enabled` via `dig`. For enabled stores, it creates `networking.k8s.io/v1` `Ingress` in the release namespace, with optional annotations, host/path/pathType, backend service `rook-ceph-rgw-<store-name>`, port from ingress override or RGW secure/plain port, optional ingressClassName, and optional TLS.

Control flow: per-object-store conditional output.

State and persistence: creates Ingress resources for RGW service exposure. It relies on an external ingress controller for actual routing.

Dependencies and integration points: depends on Rook RGW service naming, user-supplied host/TLS/class, and Kubernetes networking API. Risks: TLS/backend protocol annotations must match whether RGW uses securePort; host/path defaults can expose services broadly; missing ingress controller support leaves resources inert. Tests should render ingress-enabled object stores with secure and plain ports.
