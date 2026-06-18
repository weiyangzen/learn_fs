<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_targets.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_targets.rs

Purpose: returns all targets with owning node, storage pool, reachability, consistency, capacities, and computed capacity-pool classification.

Important APIs/types/functions: `get_targets()` reads target rows and implements `CapacityInfo` for target response references so `CapPoolCalculator` can classify capacity pools.

Control flow: the DB query joins targets to nodes, pools, and buddy group membership. Reachability uses `node_offline_timeout`, last update age, pre-shutdown state, and primary/secondary status. After reading, the handler computes meta capacity pools globally for meta targets and storage capacity pools separately per storage pool.

State and persistence: read-only over targets, nodes, pools, and buddy groups. Capacity values are persisted by target update paths elsewhere.

Dependencies and integration points: used by management clients and affected by `timer.rs` pre-shutdown/switchover behavior. Depends on cap-pool config and calculators.

Risks: capacity-pool calculation unwraps optional capacity through the `CapacityInfo` trait but only calls it after checking `Some`; future changes must preserve that guard. Reachability logic changes during pre-shutdown to protect primary targets. Large pool/target sets trigger repeated filtering per pool.

Test signals: no direct test in this file. Useful coverage would verify reachability thresholds, pre-shutdown behavior, meta/storage cap-pool calculations, and unmapped storage targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_targets.rs -->
