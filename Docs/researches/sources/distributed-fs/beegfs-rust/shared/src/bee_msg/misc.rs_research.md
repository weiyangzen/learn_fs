## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/misc.rs

### Purpose
Defines miscellaneous BeeGFS control messages: generic error responses, UDP acknowledgements, stream authentication, peer identity, channel-direct hints, and capacity-pool refresh/query messages.

### Important APIs, Types, and Functions
- `GenericResponseCode` aliases `i32`; constants `TRY_AGAIN`, `INDIRECT_COMM_ERR`, and `NEW_SEQ_NO_BASE` define known generic response codes.
- `GenericResponse` (`MsgId 4009`) carries a response code and C-string description.
- `Ack` (`4003`) models UDP acknowledgement IDs.
- `AuthenticateChannel` (`4007`) carries `AuthSecret` and is used by `conn::incoming` as the only allowed pre-authentication TCP message when authentication is required.
- `PeerInfo` (`4011`) reports a `NodeType` and `NodeId`.
- `SetChannelDirect` (`4001`) carries a direct-worker hint but is documented as ignored in Rust.
- `RefreshCapacityPools` (`1035`) is a UDP invalidation/request-refresh signal.
- `GetNodeCapacityPools` (`1021`) and `GetNodeCapacityPoolsResp` (`1022`) query node capacity pools.
- `GetNodeCapacityPoolsResp` implements custom serialization for nested map/sequence data: `HashMap<PoolId, Vec<Vec<u16>>>`.
- `CapacityPoolQueryType` maps `Meta`, `Storage`, `MetaMirrored`, and `StorageMirrored` to BeeGFS integers `0..3`.

### Control Flow and State
The file itself has no mutable state. `AuthenticateChannel` affects connection state because a handler may call `Request::authenticate_connection()` after validating it, changing a `Stream`'s authenticated flag. Refresh messages trigger other nodes to request fresh state rather than embedding the state directly.

### Dependencies and Integration Points
Uses `AuthSecret`, `NodeType`, `NodeId`, and `PoolId` from shared types, and BeeSerde helpers for C strings and enum integer conversion. Integrates with TCP authentication checks in `conn/incoming.rs`, request handling in `conn/msg_dispatch.rs`, and capacity-pool state in management/meta handlers.

### Risks and Edge Cases
`GetNodeCapacityPoolsResp` uses raw `u16` inner IDs instead of typed IDs, so target/group interpretation depends on `CapacityPoolQueryType`. Nested collection serialization is manual because the derive macro does not support nested collections; drift from BeeGFS C++ layouts would be easy to miss. `Ack` can be ignored by current nodes, so callers must not rely on it as a strong delivery guarantee.

### Test Signals
No direct tests. BeeSerde nested sequence/map tests partially exercise the same serializer primitives. Targeted tests should round-trip `GetNodeCapacityPoolsResp` with multiple pools and empty inner vectors.
