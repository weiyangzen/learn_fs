<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/register_node.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/register_node.rs

**Purpose:** Handles explicit node registration and returns assigned node ID, gRPC port, and filesystem UUID.

**Important APIs/types/functions:** Defines `COMPATFLAG_CLIENT_SUPPORTS_REGREJ = 1`; implements `HandleWithResponse` for `RegisterNode`, response `RegisterNodeResp`; calls `common::update_node`.

**Control flow:** Fails during pre-shutdown, derives whether the caller supports registration rejection from the request header compatibility flags, updates/registers the node through shared logic, reads `FsUuid` from config table, and returns the node numeric ID, configured gRPC port, and filesystem UUID bytes.

**State and persistence behavior:** Mutates the same node/NIC/meta target/root/address/notification state as `update_node`. Reads persistent filesystem UUID.

**Dependencies and integration points:** Classic registration entry point for clients, meta nodes, and storage nodes. Integrates with licensing, registration-disable config, and gRPC discovery.

**Risks:** Missing filesystem UUID turns a successful registration update into a handler error. Rejection behavior depends on a single compatibility flag; older clients may receive warnings rather than hard denial in some license-limit scenarios.

**Test signals:** Register new and existing nodes, verify response gRPC port and fs UUID, compatibility-flag rejection behavior, and pre-shutdown TRY_AGAIN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/register_node.rs -->
