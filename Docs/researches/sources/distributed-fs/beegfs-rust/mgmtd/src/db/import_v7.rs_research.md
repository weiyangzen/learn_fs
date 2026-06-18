<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7.rs

Purpose: imports a BeeGFS 7.2/7.4 management data directory into a fresh Rust mgmtd SQLite database.

Important APIs/types/functions: public `import_v7()` orchestrates the import. Helpers validate `format.conf`, target states, deserialize v7 node/NIC files, import meta/storage nodes and targets, parse buddy group maps, import storage pools, set root inode state, and import quota default/specific limits.

Control flow: import requires a new DB (`MAX(uid) <= 2`), `format.conf` version 5, and all meta/storage target states GOOD. It imports storage nodes/targets/groups/pools first, then meta nodes/groups/root, then quota if a quota directory exists. Storage-pool alias conflicts or invalid aliases prompt interactively for replacement aliases.

State and persistence: writes persistent nodes, targets, buddy groups, pools, root inode, NICs, and quota limit rows. It intentionally ignores ephemeral quota usage, clients, and refreshed runtime data. Large v7 quota values beyond signed 63-bit are treated as unlimited/skipped with notes.

Dependencies and integration points: called by `main.rs` database initialization when `--import-from-v7` is provided. It depends on shared BeeSerde decoders for legacy on-disk formats, DB helpers for inserts, and SQLite transactions for all-or-nothing behavior.

Risks: format support is intentionally narrow. Interactive alias repair can block automation. The code assumes old management is shut down and clients unmounted; those conditions are documented but not fully enforceable. SQL writes must stay aligned with schema views and v7 binary layouts.

Test signals: covered by `import_v7/test.rs`, which extracts a fixed v7.4 fixture and validates nodes, targets, groups, root, pools, and quota rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7.rs -->
