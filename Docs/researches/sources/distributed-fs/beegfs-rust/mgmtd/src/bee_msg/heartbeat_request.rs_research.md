<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/heartbeat_request.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/heartbeat_request.rs

**Purpose:** Responds to a peer request for the management node's heartbeat identity and NICs.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `HeartbeatRequest`, response `Heartbeat`; uses management constants `MGMTD_UID` and `MGMTD_ID`.

**Control flow:** Reads the management alias and NICs from the database, falling back to defaults if the read fails, maps NICs to BeeMsg format, and returns a management `Heartbeat` with configured BeeMsg port and no machine UUID.

**State and persistence behavior:** Read-only; exposes management identity and network address state.

**Dependencies and integration points:** Used by classic peers probing the management service. Depends on DB entity/NIC state and static config `beemsg_port`.

**Risks:** `unwrap_or_default` hides DB read errors and can return an empty alias/NIC list, which may make peer diagnostics harder. Both `port` and `port_tcp_unused` are set from the same config value.

**Test signals:** Verify response contains management node type, ID, port, alias, and expected NICs; add a DB failure test if fallback behavior is important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/heartbeat_request.rs -->
