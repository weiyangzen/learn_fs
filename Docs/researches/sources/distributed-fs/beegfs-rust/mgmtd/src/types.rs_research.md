<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/types.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/types.rs

Purpose: local type utilities for mgmtd database/protobuf integration, primarily SQLite enum conversion.

Important APIs/types/functions: `SqliteEnumExt` defines `sql_variant()`, `from_sql_variant()`, and `from_row()`. The `impl_enum_sqlite!` macro implements it for `EntityType`, `NodeType`, `NodeTypeServer`, `NicType`, `TargetConsistencyState`, `QuotaIdType`, and `QuotaType`. The module re-exports entity resolution helpers from `types/entity.rs`.

Control flow: enum conversions are fixed integer mappings used by schema rows. Unknown integer values become rusqlite invalid-type errors.

State and persistence: establishes the numeric representation persisted in SQLite for core enums.

Dependencies and integration points: used throughout DB modules, gRPC handlers, import code, quota logic, and tests.

Risks: changing mappings would break existing databases unless migrations translate values. `from_sql_variant()` reports invalid type rather than a richer unknown-value error.

Test signals: no dedicated tests. Broad DB and gRPC tests exercise conversions via fixture rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/types.rs -->
