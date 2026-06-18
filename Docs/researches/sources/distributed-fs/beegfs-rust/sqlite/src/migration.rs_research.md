## sources/distributed-fs/beegfs-rust/sqlite/src/migration.rs

### Purpose
Provides build-time and runtime SQLite migration utilities: reading numbered SQL files, generating Rust migration slices, flattening schemas, checking DB versions, applying migrations, and backing up DB files.

### Important APIs, Types, and Functions
- `Migration` stores static versioned SQL for runtime use.
- `OwnedMigration` stores owned SQL read from files at build time.
- `read_migrations(src_dir)` reads `n.sql` files, sorts by version, rejects empty/non-contiguous sets, and returns owned migrations.
- `migrations_slice_code` emits Rust code for a `&[::sqlite::Migration]` literal.
- `flatten_migrations` applies migrations to an in-memory database and extracts ordered SQL from `sqlite_schema`.
- `check_schema(tx, migrations)` compares `PRAGMA user_version` to migration base/latest and reports whether migration is needed.
- `migrate_schema(tx, migrations)` applies pending migrations and updates `user_version`.
- `backup_db(conn)` copies the current database to `<db_file>.v<version>`.
- `check_migration_versions` validates contiguity and returns `(base, latest)`.

### Control Flow and State
Build-time functions read SQL files and generate code/schema snapshots. Runtime migration reads `user_version`, normalizes new DB version `0` to `base - 1`, skips already-applied migrations by index, executes remaining SQL batches, and updates `user_version`. Backup uses rusqlite's backup API.

### Dependencies and Integration Points
Uses `rusqlite`, `anyhow`, filesystem APIs, and `std::fmt::Write`. Integrated into build scripts and runtime database startup paths. `sqlite_check` depends on flattened schema output.

### Risks and Edge Cases
If the first remaining migration has version `0`, `base - 1` underflows, but migration versions are expected to start at positive integers. `migrations_slice_code` embeds SQL in a raw string using `r#"... "#`; SQL containing the delimiter sequence could break generated Rust. `flatten_migrations` emits schema SQL ordered by type/name, which may still miss dependencies beyond the chosen order in unusual schemas. `check_schema` treats database version `0` as invalid unless latest is also zero; runtime callers should use `migrate_schema` for new DBs.

### Test Signals
Unit tests cover migration application across contiguous versions, dropping early migrations after a new base, failure when up-to-date, non-contiguous migration failure, and schema flattening order for tables/indexes/views.
