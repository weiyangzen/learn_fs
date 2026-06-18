<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_mirror_buddy_groups_resp.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_mirror_buddy_groups_resp.rs

**Purpose:** Ignores peer responses to mirror buddy group notifications.

**Important APIs/types/functions:** Implements `HandleNoResponse` for `SetMirrorBuddyGroupResp`.

**Control flow:** Returns success without action; comment identifies it as a response from server nodes.

**State and persistence behavior:** No state changes.

**Dependencies and integration points:** Part of classic buddy group notification compatibility.

**Risks:** Peer-side failures or acknowledgements are not tracked.

**Test signals:** Dispatch response message and verify no unhandled warning or mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_mirror_buddy_groups_resp.rs -->
