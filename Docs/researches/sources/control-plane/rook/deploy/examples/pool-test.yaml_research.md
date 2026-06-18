# sources/control-plane/rook/deploy/examples/pool-test.yaml

Purpose: minimal one-replica block pool for tests.

Important APIs/types/functions: `CephBlockPool/replicapool` in `rook-ceph`, failure domain `host`, replicated size 1.

Control flow: Rook reconciles the pool for quick single-node test use.

State and persistence: data stored in the pool has no redundancy.

Dependencies/integration: usually paired with a test `StorageClass`.

Risks: replica size 1 risks data loss and can mask production placement issues.

Test signals: pool ready and PVCs using the pool bind in small clusters.
