## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/target.rs

### Purpose
Defines target mapping, target state, target registration, consistency-state updates, target usage reporting, and target-state refresh messages.

### Important APIs, Types, and Functions
- `GetTargetMappings` (`1025`) / `GetTargetMappingsResp` (`1026`) fetch target-to-node mappings. The response has custom serialization writing node IDs as raw `u32`.
- `GetTargetStates` (`1049`) / `GetTargetStatesResp` (`1050`) fetch parallel lists of target IDs, reachability states, and consistency states.
- `TargetReachabilityState` maps `Online`, `ProbablyOffline`, and `Offline` to `0`, `1`, and `2` and serializes as `u8`.
- `RegisterTarget` (`1041`) / `RegisterTargetResp` (`1042`) register storage targets.
- `MapTargets` (`1023`) / `MapTargetsResp` (`1024`) map target IDs to pools and owning node.
- `ChangeTargetConsistencyStates` (`1057`) and `SetTargetConsistencyStates` (`1055`) update target consistency, with corresponding `OpsErr` responses.
- `SetStorageTargetInfo` (`2099`) / response (`2100`) publish usage information for storage or metadata targets.
- `TargetInfo` includes path, total/free space, total/free inodes, and consistency state.
- `RefreshTargetStates` (`1051`) is a UDP refresh trigger.

### Control Flow and State
All state is represented in message payloads. Parallel-vector responses require consumers to combine positions into logical records. Consistency-state changes include old/new state lists for compare-and-change semantics, while set-state messages replace with provided states and may optionally set reachability online via `set_online`.

### Dependencies and Integration Points
Uses BeeSerde helpers, `OpsErr`, `NodeType`, ID aliases, `PoolId`, and `TargetConsistencyState`. It integrates with buddy-group state in `buddy_group.rs`, storage-pool mapping in `storage_pool.rs`, and management/storage message handlers.

### Risks and Edge Cases
Parallel vectors can desynchronize by length. `GetTargetMappingsResp` currently implements serialization but not an explicit custom deserializer in this file; if `BeeSerde` derive is not present, inbound decoding of this response may not compile or may be intentionally unused. `TargetInfo.path` uses aligned C-string encoding (`CStr<4>`), which must match C/C++ message definitions. Raw `u8` flags and unchecked state transition lists need handler validation.

### Test Signals
No local tests. Useful tests include target-state response vector length validation in handlers, enum conversion rejection for invalid values, and round-trip of `TargetInfo` path alignment.
