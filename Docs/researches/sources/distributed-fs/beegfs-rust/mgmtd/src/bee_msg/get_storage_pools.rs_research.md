<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_storage_pools.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_storage_pools.rs

**Purpose:** Builds full classic BeeMsg storage-pool responses including pool aliases, targets, buddy groups, capacity pools, grouped target pools, and target-to-node mappings.

**Important APIs/types/functions:** Local `TargetOrBuddyGroup` implements `CapacityInfo`; `HandleWithResponse` for `GetStoragePools` returns `GetStoragePoolsResp` with `StoragePool`, `TargetCapacityPools`, and `BuddyGroupCapacityPools`.

**Control flow:** Reads storage pools, mapped storage targets, and storage buddy groups with min free capacity across primary/secondary targets. For each pool, filters relevant targets/groups, constructs separate capacity calculators for targets and buddy groups, populates target maps, per-capacity ID vectors, grouped target maps by node ID, and buddy group vectors.

**State and persistence behavior:** Read-only. The response reflects current target mapping, pool assignment, alias, and capacity data.

**Dependencies and integration points:** Integrates with `cap_pool.rs`, DB tables/views for storage pools/targets/buddy groups, and classic storage-pool refresh notifications.

**Risks:** Targets without node mappings are excluded. Buddy group capacity is the minimum of primary and secondary, which is conservative but depends on both capacity rows being present. HashMap key iteration affects response ordering for some fields.

**Test signals:** Seed pools with mapped/unmapped targets and buddy groups, verify target maps, grouped target pools by node, and capacity classification with dynamic limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_storage_pools.rs -->
