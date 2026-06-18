## sources/distributed-fs/beegfs-rust/shared/src/types.rs

### Purpose
Defines shared BeeGFS domain types, ID aliases, enums, display strings, gRPC conversions, quota/target states, and authentication-secret handling.

### Important APIs, Types, and Functions
- Re-exports `entity::*`.
- Type aliases include `Uid`, `TargetId`, `BuddyGroupId`, `Port`, `NodeId`, `PoolId`, and `QuotaId`.
- Constants include `MGMTD_ID`, `MGMTD_UID`, and `DEFAULT_STORAGE_POOL`.
- `NodeType` models meta, storage, client, and management nodes with BeeGFS integer values and user strings.
- `NodeTypeServer` restricts to meta/storage and converts to/from `NodeType`.
- `NicType` parses `tcp`/`rdma`, maps to BeeGFS integers, displays user strings, and optionally maps to protobuf NIC types.
- `CapacityPool` models normal/low/emergency and provides `bee_msg_vec_index`.
- `TargetConsistencyState` serializes/deserializes as `u8`.
- `QuotaIdType` and `QuotaType` model user/group and space/inode quota dimensions.
- `AuthSecret` is a BeeSerde wrapper over `u64`, with `hash_from_bytes`, `try_from_bytes`, and `FromStr`.

### Control Flow and State
The file is mostly type-level. Runtime behavior is validation/conversion: enum numeric conversions reject invalid values, `NodeTypeServer` rejects client/management, `NicType::from_str` rejects unknown names, and `AuthSecret` either hashes bytes with SHA-256 first eight bytes or parses a stringified integer.

### Dependencies and Integration Points
Uses `bee_serde`, `bee_serde_derive`, `anyhow`, `ring::digest`, optional protobuf modules, macros from `impl_macros.rs`, and `entity.rs`. These types are used throughout messages, connection addressing, gRPC APIs, and configuration.

### Risks and Edge Cases
Many IDs are aliases rather than newtypes, so accidental cross-use of target, buddy group, pool, and node IDs can compile. `AuthSecret::hash_from_bytes` keeps only the first eight SHA-256 bytes as little-endian `u64`, matching BeeGFS behavior but lowering entropy to 64 bits. `AuthSecret::try_from_bytes` says it expects a stringified `i64` in comments but parses into `u64` through the wrapper field type.

### Test Signals
No direct tests here. Enum conversion tests, auth-secret known vectors, and protobuf feature compile/tests would improve confidence.
