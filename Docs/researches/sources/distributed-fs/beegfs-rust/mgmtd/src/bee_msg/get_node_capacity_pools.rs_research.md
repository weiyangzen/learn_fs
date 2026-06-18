<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_node_capacity_pools.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_node_capacity_pools.rs

**Purpose:** Computes capacity pool assignments for meta/storage targets or buddy groups in the classic BeeMsg format.

**Important APIs/types/functions:** Defines local `TargetOrBuddyGroup` implementing `CapacityInfo`, helpers `load_targets_info_by_type` and `load_buddy_groups_info_by_type`, and `HandleWithResponse` for `GetNodeCapacityPools`.

**Control flow:** Branches on `CapacityPoolQueryType`: meta targets, storage targets per storage pool, meta buddy groups, or storage buddy groups per storage pool. It loads free space/inodes, constructs `CapPoolCalculator` from static/dynamic config, maps each ID into Normal/Low/Emergency vector positions with `bee_msg_vec_index`, and returns a `HashMap<PoolId, Vec<Vec<u16>>>` where pool 0 is used for meta/non-storage-pool responses.

**State and persistence behavior:** Read-only. Capacity pool results are computed from latest stored capacity measurements and config thresholds.

**Dependencies and integration points:** Integrates with `cap_pool.rs`, target/buddy group database tables, and storage pool configuration. Called by nodes that need capacity pool membership.

**Risks:** Missing capacity values default to zero through `unwrap_or_default`, pushing targets toward Emergency. Storage paths iterate every storage pool and clone iterators for calculator setup; large clusters should be profiled. HashMap response ordering is not deterministic, but keys identify pools.

**Test signals:** Seed target capacities and dynamic limits, request all four query types, and verify pool grouping and Normal/Low/Emergency vector indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_node_capacity_pools.rs -->
