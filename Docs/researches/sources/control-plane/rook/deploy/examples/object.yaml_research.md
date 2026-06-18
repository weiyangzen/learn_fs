# sources/control-plane/rook/deploy/examples/object.yaml

Purpose: standard Rook Ceph object store example for a replicated RGW deployment.

Important APIs/types/functions: `CephObjectStore/my-store`, replicated metadata/data pools size 3 with compression disabled and `bulk` data parameter, `preservePoolsOnDelete: false`, one gateway on port 80 with pod anti-affinity and cluster-critical priority, plus health checks.

Control flow: Rook creates pools, configures RGW, and deploys the gateway service/pod.

State and persistence: object metadata and data are stored in Rook-created Ceph pools; pools may be deleted when the CR is deleted.

Dependencies/integration: supports user, bucket storage class, OBC, and external service examples.

Risks: one gateway instance is not HA; `preservePoolsOnDelete: false` can remove data during deletion.

Test signals: object store status ready, RGW service healthy, and S3 bucket lifecycle passes.
