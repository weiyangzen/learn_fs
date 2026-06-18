# sources/control-plane/rook/deploy/examples/nfs-load-balancer.yaml

Purpose: exposes a Ceph NFS server instance externally through a Kubernetes `LoadBalancer` service.

Important APIs/types/functions: `Service/rook-ceph-nfs-my-nfs-load-balancer` in `rook-ceph`, port `2049`, `externalTrafficPolicy: Local`, selector `app=rook-ceph-nfs`, `ceph_nfs=my-nfs`, `instance=a`.

Control flow: cloud or bare-metal load balancer integration provisions an external address and forwards NFS traffic to the selected NFS ganesha pod.

State and persistence: no storage state; service endpoints follow matching NFS pods.

Dependencies/integration: depends on `CephNFS/my-nfs` from `nfs.yaml` or `nfs-test.yaml` and a cluster load balancer implementation.

Risks: selector pins to instance `a`, so scaling or failover patterns may require a different service strategy. Exposing NFS externally needs network and firewall review.

Test signals: external IP assignment, endpoint selection, and successful NFS mount to the exported path.
