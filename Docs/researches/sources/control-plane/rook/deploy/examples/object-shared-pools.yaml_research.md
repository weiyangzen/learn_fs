# sources/control-plane/rook/deploy/examples/object-shared-pools.yaml

Purpose: production-style shared RGW pool set with replicated root/meta pools and erasure-coded data.

Important APIs/types/functions: `CephBlockPool/rgw-root` and `rgw-meta-pool` with replica size 3, plus `CephBlockPool/rgw-data-pool` using EC `dataChunks: 2` and `codingChunks: 1`.

Control flow: Rook creates pool resources that object stores can reference via `sharedPools`.

State and persistence: root/meta and object data persist in shared pools.

Dependencies/integration: intended for stores such as `object-a.yaml` and `object-b.yaml`.

Risks: EC data pool requires enough OSDs and careful workload compatibility; shared pools couple store lifecycles.

Test signals: pools healthy and object stores using shared pools can provision buckets.
