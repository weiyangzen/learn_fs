<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/config.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/config.rs

Purpose: typed access layer for key/value configuration rows stored in SQLite, especially filesystem identity and counters used by mgmtd.

Important APIs/types/functions: `Config` enum maps known keys (`FsUuid`, `FsInitDateSecs`, `FsName`, `CounterLastClientID`, `TrialSerial`) to stable DB strings. `set()` inserts/replaces mutable config rows and blocks updates to immutable keys. `get()` parses optional stored values into caller-requested types. `delete()` removes mutable rows.

Control flow: `set()` first reads the existing value for immutable keys and bails if already present, then writes with `REPLACE INTO config`. `get()` manually prepares and steps a query to avoid an extra allocation, then parses the stored string.

State and persistence: persists management configuration in the `config` table. `FsUuid`, `FsInitDateSecs`, and `TrialSerial` are treated immutable by this API, though direct SQL could still alter them. `CounterLastClientID` preserves sequential client ID allocation across restarts.

Dependencies and integration points: used by `db::initial_entries()`, `db::node::insert()` for client ID counters, `lib.rs` for trial serial persistence, `grpc/get_license.rs`, and `grpc/get_nodes.rs`.

Risks: all values are strings, so parse failures surface at read time. API-level immutability can be bypassed outside these helpers. `delete()` requires exactly one affected row, so deleting an already absent mutable key fails.

Test signals: `set_get_delete` covers immutable update/delete rejection, mutable replacement, read-missing behavior, and deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/config.rs -->
