# sources/control-plane/rook/deploy/examples/object-test.yaml

Purpose: minimal test object store using one-replica metadata and data pools.

Important APIs/types/functions: `CephObjectStore/my-store` with metadata/data `replicated.size: 1`, `preservePoolsOnDelete: false`, and one gateway instance on port 80.

Control flow: Rook creates the pools and a single RGW gateway for quick test use.

State and persistence: buckets and objects live in one-replica Ceph pools that can be deleted with the CR.

Dependencies/integration: requires a running Rook Ceph cluster and object CRDs.

Risks: no redundancy and pool deletion on CR removal make it unsuitable for durable data.

Test signals: store ready and simple S3 smoke tests.
