<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db.rs

Purpose: top-level SQLite database module for mgmtd. It owns migration discovery, initial database seeding, submodule exports, and test helpers for in-memory databases with fixture data.

Important APIs/types/functions: `MIGRATIONS` includes the generated migration list from `OUT_DIR`. `initial_entries()` seeds immutable config entries `FsUuid` and `FsInitDateSecs`. The module re-exports `import_v7()` and exposes submodules for entity, config, node, NIC, target, buddy group, storage pool, and miscellaneous operations.

Control flow: database creation callers migrate schema, call `initial_entries()`, optionally import v7 data, then commit. Runtime startup checks/migrates schema in `lib.rs`, then uses the submodules through transactional `App` helpers.

State and persistence: this module initializes the persistent SQLite config state containing filesystem UUID and initialization time. It relies on schema migrations and SQLite views/tables defined elsewhere under `db/schema`.

Dependencies and integration points: consumed by `main.rs` initialization, `lib.rs` migration/startup, gRPC handlers, timers, and quota update logic. It uses shared BeeGFS types, rusqlite, sqlite helper extensions, generated SQL-check macros, and UUID.

Risks: `initial_entries()` treats `FsUuid` and init time as immutable via `db/config.rs`; callers must only run it for new DBs. The migration include depends on build-script output being available and correct. Test helpers load `test_data.sql`, so schema/view drift can break broad test suites.

Test signals: built-in test helper functions are used by multiple submodule unit tests. Direct coverage should verify initial entries with and without caller-provided UUID and migration compatibility for fresh/in-memory databases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db.rs -->
