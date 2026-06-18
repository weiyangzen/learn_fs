<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg.rs -->
# sources/distributed-fs/beegfs-rust/shared/src/bee_msg.rs

Purpose: defines core BeeGFS wire-message traits, common operation error codes, message header layout, and serialization/deserialization helpers shared by mgmtd and other Rust components.

Important APIs/types/functions: `MsgId` is a `u16`. `BaseMsg` and `Msg` mark BeeGFS messages and require an associated message ID. `OpsErr` wraps BeeGFS operation error integers with constants such as `SUCCESS`, `INTERNAL`, `UNKNOWN_NODE`, `EXISTS`, `NOTEMPTY`, `UNKNOWN_TARGET`, `INVAL`, `AGAIN`, and `UNKNOWN_POOL`. `Header` is a BeeSerde-serializable 40-byte header with feature flags, prefix, ID, target/user fields, and sequence fields. Helpers include `serialize_body()`, `serialize_header()`, `serialize()`, `deserialize_header()`, `deserialize_body()`, and `deserialize()`.

Control flow: serialization writes the body after a reserved header slot, sets total message length and message ID, then serializes the header. Deserialization validates the fixed header length and prefix before decoding the body slice indicated by `msg_len`.

State and persistence: stateless; it encodes/decodes network byte buffers used in BeeMsg TCP/UDP communication.

Dependencies and integration points: re-exports message submodules for buddy groups, misc, node, quota, storage pool, and target. Used by shared connection code, mgmtd handlers, timers, quota, and gRPC side-effect messages.

Risks: buffer sizes must be correct; `serialize()` indexes `buf[Header::LEN..]` and callers must provide enough space. `deserialize_body()` trusts `header.msg_len()` for slicing and will panic or error if inconsistent with buffer length depending on slice bounds. Header prefix compatibility is strict.

Test signals: no direct tests here. Protocol tests should cover header round trips, invalid prefixes, short buffers, body length mismatches, and all message submodule serialization compatibility with C++ BeeGFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg.rs -->
