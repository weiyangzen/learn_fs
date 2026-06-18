<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_target_mappings.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_target_mappings.rs

**Purpose:** Returns storage target-to-node mappings.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `GetTargetMappings`, response `GetTargetMappingsResp`.

**Control flow:** Reads `target_id,node_id` from `storage_targets` where `node_id` is not null and collects directly into a `HashMap<TargetId, NodeId>`.

**State and persistence behavior:** Read-only. Unmapped targets are intentionally omitted.

**Dependencies and integration points:** Used by storage/meta/client peers that need storage target ownership. Relies on the `storage_targets` DB view.

**Risks:** HashMap ordering is not stable, but mappings are keyed. Duplicate target IDs would be collapsed, though the schema should prevent them.

**Test signals:** Query a seed database with mapped and unmapped targets and verify only mapped storage targets are returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_target_mappings.rs -->
