<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/headless-mon-service.yaml -->
# sources/control-plane/rook/deploy/examples/headless-mon-service.yaml

Purpose: exposes Rook Ceph monitor pods through a headless Kubernetes Service.
Important APIs/types/functions: `Service` `rook-ceph-mon`, namespace `rook-ceph`, `clusterIP: None`, selector `app: rook-ceph-mon`, and port `6789`.
Control flow: Kubernetes creates DNS records/endpoints for individual monitor pods instead of load-balancing through a cluster IP. State is Service and endpoint slice data. Dependencies are monitor pods with matching labels and clients that need stable DNS-based monitor discovery. Risks: monitor protocols may also require msgr2 port 3300 in modern deployments, and selector must match Rook labels. Test signals: endpoints list mons, DNS resolves per endpoint, and Ceph clients can connect through the service.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/headless-mon-service.yaml -->
