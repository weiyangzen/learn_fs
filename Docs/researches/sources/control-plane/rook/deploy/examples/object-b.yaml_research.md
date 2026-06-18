# sources/control-plane/rook/deploy/examples/object-b.yaml

Purpose: defines a second RGW object store, `store-b`, for demonstrating multiple object stores on shared pools.

Important APIs/types/functions: `CephObjectStore/store-b`, `spec.sharedPools`, one RGW gateway on port 80, pod anti-affinity, and cluster-critical priority class.

Control flow: Rook deploys a distinct RGW gateway while reusing the shared pool topology.

State and persistence: object state is stored in shared Ceph pools; the Kubernetes CR stores desired gateway count and scheduling policy.

Dependencies/integration: pairs with shared pool manifests and separate bucket classes/claims for multi-store scenarios.

Risks: pool sharing reduces isolation, and one gateway instance is a single pod availability profile.

Test signals: independent RGW service for `store-b` and successful bucket operations isolated by store name.
