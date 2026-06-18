<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/cap_pool.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/cap_pool.rs

**Purpose:** Implements capacity-pool threshold logic for classifying targets and buddy groups as Normal, Low, or Emergency.

**Important APIs/types/functions:** `CapPoolLimits`, `CapPoolDynamicLimits`, trait `CapacityInfo`, `CapPoolCalculator::{new,new_static,new_dynamic,cap_pool}`, and internal `MinMax`. Limit structs deserialize kebab-case TOML fields with integer-unit parsing.

**Control flow:** Static construction validates low thresholds are not below emergency thresholds. Dynamic construction validates both static and dynamic limits, scans current capacity values, measures spread among Normal and Low candidates, and replaces low/emergency thresholds with dynamic values when configured spread thresholds are exceeded. `cap_pool` classifies a capacity pair by requiring both space and inode values to satisfy the selected thresholds.

**State and persistence behavior:** No persistence; calculator instances hold effective thresholds derived from config and current observed capacities. Config values originate from `beegfs-mgmtd.toml` / defaults.

**Dependencies and integration points:** Used by `get_node_capacity_pools.rs` and `get_storage_pools.rs`. Depends on `serde::Deserialize`, `shared::parser::integer_unit`, and shared `CapacityPool`.

**Risks:** `MinMax` uses zero/zero as the uninitialized sentinel, which is acceptable for positive observed values but can make all-zero observations indistinguishable from no observations. Missing capacity values are often converted to zero by callers, biasing results toward Emergency. Dynamic thresholds can significantly change pool membership based on spread, so config validation and operational documentation matter.

**Test signals:** Unit tests cover static classification, dynamic no-spread, space spread, inode spread, and invalid limit combinations. Add integration tests through storage pool handlers for real DB capacity data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/cap_pool.rs -->
