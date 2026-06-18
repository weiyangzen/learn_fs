<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/peer_info.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/peer_info.rs

**Purpose:** Stub handler for `PeerInfo` messages.

**Important APIs/types/functions:** Implements `HandleNoResponse` for `PeerInfo`.

**Control flow:** Returns success without action; the comment notes the message appears unused.

**State and persistence behavior:** No state changes or persistence.

**Dependencies and integration points:** Exists so the dispatcher recognizes the BeeMsg ID.

**Risks:** If future peers rely on peer metadata, this stub will silently discard it.

**Test signals:** Dispatch a `PeerInfo` message and verify no unhandled-message response is emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/peer_info.rs -->
