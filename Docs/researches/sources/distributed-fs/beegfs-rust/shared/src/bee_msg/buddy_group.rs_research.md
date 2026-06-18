## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/buddy_group.rs

### Purpose
Defines BeeGFS wire message types for mirror buddy-group discovery, creation/removal, metadata mirroring enablement, target state aggregation, and storage/meta resynchronization statistics. These types are Rust protocol counterparts for BeeGFS C/C++ management, storage, metadata, client, fsck, and ctl interactions.

### Important APIs, Types, and Functions
- `GetMirrorBuddyGroups` / `GetMirrorBuddyGroupsResp` use message IDs `1047` and `1048` to query buddy groups for a `NodeType`; the response carries parallel vectors of group IDs, primary targets, and secondary targets.
- `CombinedTargetState` combines `TargetReachabilityState` from `target.rs` with `TargetConsistencyState` from shared `types.rs`.
- `BuddyGroup` stores primary and secondary `TargetId` values.
- `GetStatesAndBuddyGroups` / `GetStatesAndBuddyGroupsResp` use IDs `1053` and `1054` and return `HashMap<BuddyGroupId, BuddyGroup>` plus `HashMap<TargetId, CombinedTargetState>`.
- `RemoveBuddyGroup`, `SetMetadataMirroring`, `SetMirrorBuddyGroup`, and their responses model mutation operations and return `OpsErr` status.
- `SetMirrorBuddyGroupResp` has manual `Serializable` and `Deserializable` implementations because the BeeGFS wire format includes two trailing padding bytes after `group_id`.
- `SetLastBuddyCommOverride` and `GetStorageResyncStats` / `GetMetaResyncStats` expose mirror resync control and reporting.
- `BuddyResyncJobState` is converted with `impl_enum_bee_msg_traits!` using BeeGFS numeric values `0..5`.

### Control Flow and State
The file is declarative protocol glue: runtime control flow is in the serializer, deserializer, and connection dispatcher. Message handlers elsewhere deserialize these structs based on `Msg::ID`, execute cluster state changes or queries, and serialize the response. State represented here includes buddy group mapping, target state, metadata mirroring enablement, last buddy-communication override, and resync job counters, but the file itself persists none of it.

### Dependencies and Integration Points
Depends on `super::*` for `Msg`, `MsgId`, `OpsErr`, BeeSerde helpers, and shared BeeGFS type aliases. It imports `TargetReachabilityState` from `target.rs` and uses `TargetConsistencyState`, `NodeType`, `NodeId`, `TargetId`, and `BuddyGroupId` from `types.rs`. Integration is through `bee_msg::serialize` / `deserialize_body` and the network layers under `conn/`.

### Risks and Edge Cases
Parallel-vector response formats require consumers to verify equal lengths before zipping. The manual padding in `SetMirrorBuddyGroupResp` must remain exact for compatibility. Several integer enum fields are serialized as different raw widths (`u32`, `i32`), so changing helper annotations can break wire compatibility. Mutation messages carry `u8` boolean-ish fields (`check_only`, `force`, `allow_update`, `abort_resync`) without local validation.

### Test Signals
No local tests in this file. Coverage is indirect through BeeSerde tests, message round-trip tests elsewhere if present, and integration tests against BeeGFS peers. Useful additional tests would round-trip `SetMirrorBuddyGroupResp` padding and assert all map/sequence response formats decode correctly.
