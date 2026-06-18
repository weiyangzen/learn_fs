## sources/distributed-fs/beegfs-rust/shared/src/bee_msg/quota.rs

### Purpose
Defines quota query, response, exceeded-quota publication, and exceeded-quota request messages for BeeGFS user/group quota handling across ctl, management, metadata, and storage roles.

### Important APIs, Types, and Functions
- `GetQuotaInfo` (`2097`) models quota query type, quota ID type, range/list/single fields, transfer method, target ID, and pool ID.
- `GetQuotaInfo::with_group_ids` and `with_user_ids` build list-mode queries from `HashSet<QuotaId>`, target, and pool.
- `GetQuotaInfo` implements custom serialization/deserialization because body layout depends on `query_type`.
- `GetQuotaInfoResp` (`2098`) returns `QuotaInodeSupport` and a sequence of `QuotaEntry`.
- `SetExceededQuota` (`2077`) and `SetExceededQuotaResp` (`2078`) publish exceeded quota IDs.
- `RequestExceededQuota` (`2079`) and `RequestExceededQuotaResp` (`2080`) query and return exceeded quota state.
- Enums `GetQuotaInfoTransferMethod`, `QuotaInodeSupport`, and `QuotaQueryType` map to BeeGFS numeric constants.
- `QuotaEntry` stores space, inode count, quota ID, ID type, and a `valid` flag.

### Control Flow and State
`GetQuotaInfo::serialize` emits different fields for `Range`, `List`, and `Single`, then always serializes transfer method, target ID, and pool ID. `deserialize` mirrors that layout and fills irrelevant fields with zero or empty vectors. The file represents quota state in transit but persists none locally.

### Dependencies and Integration Points
Uses `HashSet` through `super::*`, `QuotaIdType` and `QuotaType` from shared types, BeeSerde collection helpers, and `OpsErr` for responses. Integrates with management quota commands and storage/meta quota scanners.

### Risks and Edge Cases
`HashSet::drain().collect()` produces nondeterministic ID ordering; protocol consumers should treat lists as sets. `QuotaQueryType::None` and `All` serialize no ID selector fields, so handlers must interpret omitted data correctly. The `valid` field is a raw `u8`, not a Rust `bool`. Conditional serialization makes round-trip tests more important than for derive-only messages.

### Test Signals
No local tests. Needed coverage includes all `QuotaQueryType` variants, transfer-method conversions, and response sequences with both user and group quota entries.
