# sources/distributed-fs/ceph-client/drivers/greybus/arpc.h

Purpose: wire-format definitions for APBridgeA RPC messages used by Greybus-related host transport code.

Important APIs and types: `enum arpc_result` defines success, memory, invalid, timeout, and unknown-error result codes. `arpc_request_message` and `arpc_response_message` define packed RPC headers. Request type constants cover CPort connected, quiesce, clear, flush, and shutdown. Packed request payload structs carry CPort IDs, peer space, timeout, and shutdown phase.

Control flow: no executable flow; consumers serialize and parse these packed layouts.

State and persistence: no owned state. Fields are on-wire little-endian where declared with `__le16`.

Dependencies and integration: included by APBridge/transport code that maps Greybus CPort lifecycle operations to ARPC commands.

Risks: packed wire formats require careful alignment and endian conversion. Header `size` includes header plus payload, so callers must compute it consistently.

Test signals: transport-level CPort lifecycle tests and interoperability with APBridgeA firmware.
