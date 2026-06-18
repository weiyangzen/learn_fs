## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/storage_pool.rs

### Purpose
Defines storage-pool discovery and refresh messages plus nested capacity-pool structures for targets and buddy groups.

### Important APIs, Types, and Functions
- `GetStoragePools` (`1066`) and `GetStoragePoolsResp` (`1067`) query all storage pools.
- `StoragePool` contains pool ID, alias, target IDs, buddy group IDs, target capacity pools, and buddy-group capacity pools.
- `TargetCapacityPools` manually serializes nested `Vec<Vec<TargetId>>`, grouped target pools `Vec<HashMap<NodeId, Vec<TargetId>>>`, and a target-to-node map.
- `BuddyGroupCapacityPools` manually serializes nested `Vec<Vec<BuddyGroupId>>`.
- `RefreshStoragePools` (`1070`) is a UDP-style invalidation/request-refresh message carrying an `ack_id`.

### Control Flow and State
The file provides wire representations of management's storage-pool state. Deserialization reconstructs nested vectors/maps, while state ownership and mutation live in management/storage/meta handlers. Refresh messages notify nodes to fetch current pool state rather than embedding it.

### Dependencies and Integration Points
Uses typed BeeGFS IDs from `types.rs`, `HashMap` from `super::*`, and BeeSerde sequence/map primitives. It integrates with capacity-pool query messages in `misc.rs`, target mapping in `target.rs`, and buddy-group mapping in `buddy_group.rs`.

### Risks and Edge Cases
Nested collection serialization is manual and shape-sensitive. The comment on `BuddyGroupCapacityPools` notes BeeGFS deserializes these as target numeric IDs even though they are buddy group IDs; changing underlying ID widths must be coordinated carefully. Empty pool vectors and missing target-map entries need handler-level validation.

### Test Signals
No local tests. Round-trip tests should cover multiple capacity pools, grouped target maps, empty groups, and buddy-group IDs at type width boundaries.
