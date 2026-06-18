<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_mirror_buddy_groups.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_mirror_buddy_groups.rs

**Purpose:** Returns mirror buddy group IDs and their primary/secondary target IDs for a requested node type.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `GetMirrorBuddyGroups`, response `GetMirrorBuddyGroupsResp`.

**Control flow:** Performs a read transaction over `buddy_groups_ext` filtered by `node_type`, collects `(group_id, p_target_id, s_target_id)`, then splits them into three parallel vectors required by the BeeMsg response format.

**State and persistence behavior:** Read-only query; no mutation.

**Dependencies and integration points:** Used by classic peers needing buddy group topology. Depends on the buddy group DB view and shared BeeMsg buddy group types.

**Risks:** Response uses parallel vectors; any ordering bug would corrupt group-to-target association. The query preserves database order without explicit `ORDER BY`, so deterministic ordering is not guaranteed unless the view enforces it.

**Test signals:** Query seeded buddy groups and verify all vectors have equal length and aligned entries for meta and storage node types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/get_mirror_buddy_groups.rs -->
