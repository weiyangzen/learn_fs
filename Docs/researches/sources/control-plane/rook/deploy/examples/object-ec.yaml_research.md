# sources/control-plane/rook/deploy/examples/object-ec.yaml

Purpose: defines a production-style object store with replicated metadata and erasure-coded data pool.

Important APIs/types/functions: `CephObjectStore/my-store`; metadata pool replicated size 3; data pool erasure coded with `dataChunks: 2`, `codingChunks: 1`; compression disabled; `preservePoolsOnDelete: true`; one gateway instance on port 80; health check enabled.

Control flow: Rook creates pools, configures RGW metadata/data placement, then deploys the gateway.

State and persistence: metadata and object data persist in Ceph pools, and pool preservation prevents automatic deletion on CR removal.

Dependencies/integration: requires enough OSD failure domains for size 3 and EC profile creation.

Risks: EC pools need sufficient OSDs and may not support all workloads like replicated pools. Preserved pools require manual cleanup.

Test signals: store ready, EC pool health, and S3 put/get/delete operations.
