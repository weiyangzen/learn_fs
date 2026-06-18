<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/node.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/node.rs

Purpose: database access layer for BeeGFS nodes, including registration/update, lookup, stale client cleanup, license machine counting, and deletion.

Important APIs/types/functions: `Node` models `uid`, numeric ID, node type, alias, and port. `get_with_type()` and `get_by_alias()` read nodes. `insert()` allocates/generates IDs and aliases, inserts an entity and node row. `update()` refreshes port, last contact, and machine UUID. `count_machines()` counts distinct recently active meta/storage machines for licensing. `delete_stale_clients()` and `delete()` remove nodes.

Control flow: client auto-ID allocation uses persistent `CounterLastClientID` to avoid immediate reuse and scans upward, wrapping only at `u32::MAX`. Non-client nodes allocate from `1..=0xFFFF`. Explicit IDs are checked through entity resolution before insertion.

State and persistence: writes `entities`, `nodes`, and the client-ID counter. Updates `last_contact` on heartbeat/registration and deletes stale client rows based on configured timeout.

Dependencies and integration points: used by BeeMsg registration/heartbeat paths, gRPC delete/set-alias/list paths, timers, import, and license checks.

Risks: ID reuse semantics for clients are subtle and depend on the counter being durable. `update()` replaces machine UUID with the passed optional value. License counting ignores inactive/stale nodes older than five minutes.

Test signals: tests cover insert/get/delete, duplicate ID/alias failures, alias lookup, and stale client deletion after artificially aging rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/node.rs -->
