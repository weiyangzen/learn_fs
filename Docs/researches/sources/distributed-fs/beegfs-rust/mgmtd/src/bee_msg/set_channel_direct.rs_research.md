<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_channel_direct.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_channel_direct.rs

**Purpose:** Compatibility no-op handler for `SetChannelDirect`.

**Important APIs/types/functions:** Implements `HandleNoResponse` for `SetChannelDirect`.

**Control flow:** Returns success without action.

**State and persistence behavior:** No state changes.

**Dependencies and integration points:** Registered so classic peers can send this message without receiving an unhandled response.

**Risks:** If the message should influence connection routing in future protocol versions, this no-op would be insufficient.

**Test signals:** Dispatch the message and verify no response or mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/set_channel_direct.rs -->
