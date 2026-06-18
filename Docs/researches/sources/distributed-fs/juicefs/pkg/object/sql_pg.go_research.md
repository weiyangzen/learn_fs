# sources/distributed-fs/juicefs/pkg/object/sql_pg.go

Purpose: registers the PostgreSQL-backed SQL object store when `!nopg` is enabled.

Important APIs and types: it imports `github.com/jackc/pgx/v5/stdlib` for side-effect driver registration and calls `Register("postgres", ...)`.

Control flow and state: the closure removes any URI scheme and calls `newSQLStore("postgres", ..., user, pass)`. `newSQLStore` then rewrites the driver to `pgx`, builds a postgres URL, optionally honors one `search_path` schema, and creates/synchronizes the shared blob table.

Persistence and integration: persistent data is in PostgreSQL table `jfs_blob`. Runtime behavior is inherited from `sqlStore`.

Risks and test signals: multiple schemas in `search_path` are rejected. No file-local tests exist; coverage would need SQL integration tests.
