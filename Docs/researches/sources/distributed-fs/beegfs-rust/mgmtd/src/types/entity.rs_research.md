<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/types/entity.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/types/entity.rs

Purpose: resolves user/API entity identifiers (`uid`, alias, or legacy numeric ID) into complete `EntityIdSet` values by querying the appropriate SQLite view.

Important APIs/types/functions: `ResolveEntityId` provides `try_resolve()` and `resolve()`. Implementations exist for `EntityId`, `Uid`, `LegacyId`, and `Alias`. `try_resolve_num_id()` and `resolve_num_id()` are convenience helpers. `resolve_sql_from()` selects view-specific base SQL for nodes, targets, buddy groups, and pools.

Control flow: resolution dispatches by identifier kind, appends a `WHERE` clause, queries one row, and returns `None` or a typed `EntityIdSet`. Pool resolution hard-codes storage node type in the base select.

State and persistence: read-only over `nodes_ext`, `targets_ext`, `buddy_groups_ext`, and `pools_ext`.

Dependencies and integration points: used by nearly every gRPC mutation and DB validation path to normalize protobuf/entity references before changing state.

Risks: dynamic SQL appends controlled fragments only, but it still depends on exact view column aliases. Legacy ID resolution requires both node type and numeric ID; wrong entity-type/ID combinations return not found.

Test signals: no direct tests. `set_alias`, delete handlers, and DB creation tests indirectly exercise successful and failing resolutions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/types/entity.rs -->
