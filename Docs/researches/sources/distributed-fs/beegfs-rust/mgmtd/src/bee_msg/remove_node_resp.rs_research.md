<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/remove_node_resp.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/remove_node_resp.rs

**Purpose:** Ignores server responses to `RemoveNode` notifications.

**Important APIs/types/functions:** Implements `HandleNoResponse` for `RemoveNodeResp`.

**Control flow:** Logs the remote address at debug level and returns success.

**State and persistence behavior:** No state changes.

**Dependencies and integration points:** Registered to absorb classic response messages from peers.

**Risks:** Any peer-side deletion failure result is ignored.

**Test signals:** Dispatch `RemoveNodeResp` and verify no unhandled warning or DB mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/remove_node_resp.rs -->
