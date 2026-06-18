# sources/distributed-fs/seaweedfs/weed/filer/sqlite/sqlite_store.go

## Purpose

`sqlite/sqlite_store.go` registers a SQLite filer metadata store using the shared abstract SQL implementation. It was read as a complete 82-line file.

## Important APIs, Types, and Functions

`SqliteStore` embeds `abstract_sql.AbstractSqlStore`. It registers as `sqlite`, reads `dbFile`, configures create-table and upsert SQL, and `initialize` opens the `modernc.org/sqlite` driver.

## Control Flow

Initialization sets `SupportBucketTable`, installs a MySQL-style SQL generator with SQLite-compatible templates, opens and pings the DB, restricts max open connections to one, and creates the default table.

## State and Persistence Behavior

Metadata persists in a SQLite table with `(dirhash, name)` primary key, directory text, and meta blob. `WITHOUT ROWID` reduces storage overhead.

## Dependencies and Integration Points

Depends on build tags `(linux || darwin || windows) && sqlite`, `database/sql`, `modernc.org/sqlite`, `abstract_sql`, and SeaweedFS store registration.

## Risks and Edge Cases

Single open connection avoids SQLite concurrency issues but limits throughput. Reusing `mysql.SqlGenMysql` with SQLite templates requires care around quoting and generated queries.

## Test Signals

No SQLite-specific tests in this subset. Generic abstract SQL store tests are needed for CRUD, listing, bucket tables, and KV behavior.
