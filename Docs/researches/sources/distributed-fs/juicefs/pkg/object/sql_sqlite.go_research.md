# sources/distributed-fs/juicefs/pkg/object/sql_sqlite.go

Purpose: registers the SQLite-backed SQL object store when `!nosqlite` is enabled.

Important APIs and types: it imports `github.com/mattn/go-sqlite3` for driver registration and registers the scheme `sqlite3`.

Control flow and state: the registration closure calls `newSQLStore("sqlite3", removeScheme(addr), user, pass)`. The shared SQL store handles table creation, whole-object reads and writes, head/delete, and simple listing.

Persistence and integration: object bytes persist in a local or configured SQLite database file using the `jfs_blob` table.

Risks and test signals: SQLite write concurrency and database-file durability become object-store concerns. This file has no dedicated tests; behavior depends on `sql.go`.
