<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/entity.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/entity.rs

Purpose: manages globally unique entity records that back nodes, targets, pools, and buddy groups. The entity table centralizes UID and alias uniqueness across all object kinds.

Important APIs/types/functions: `get_uid()` resolves an alias to a UID; `get_alias()` resolves UID to alias; `insert()` verifies alias availability, inserts `(entity_type, alias)`, and returns the new SQLite rowid as `Uid`.

Control flow: creation checks the alias first to produce a typed value-exists error rather than relying only on a database constraint, then inserts into `entities`. Concrete object tables reference this entity row afterward.

State and persistence: writes and reads the persistent `entities` table. Entity rows are prerequisites for nodes, targets, pools, and buddy groups, and aliases are intended to be globally unique user-facing names.

Dependencies and integration points: used by `node`, `target`, `storage_pool`, `buddy_group`, and alias update gRPC paths. It depends on `TypedError`, SQLite row-count helpers, and `EntityType` SQL variant mapping.

Risks: insertion is not by itself atomic with later concrete-table inserts unless callers keep it inside one transaction. Alias validation depends on the shared `Alias` type before this layer is called. Race resistance relies on SQLite transaction/constraints.

Test signals: unit test resolves the fixture `management` alias round-trip by UID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/entity.rs -->
