# sources/control-plane/rook/deploy/examples/rgw-external.yaml

Purpose: exposes the RGW service externally through a `NodePort` service.

Important APIs/types/functions: `Service/rook-ceph-rgw-my-store-external`, labels and selector for `app=rook-ceph-rgw`, `rook_cluster=rook-ceph`, `rook_object_store=my-store`, port 80 targeting RGW port 8080.

Control flow: Kubernetes routes node traffic to the RGW service endpoints for `my-store`.

State and persistence: no data state; endpoints follow RGW pods.

Dependencies/integration: requires `CephObjectStore/my-store` and matching service labels.

Risks: NodePort exposes RGW on cluster nodes and target port must match gateway configuration.

Test signals: service endpoints populated and S3 request succeeds through node address/assigned port.
