# sources/distributed-fs/juicefs/pkg/object/sql.go

Purpose: implements an object store backed by SQL rows, shared by MySQL, PostgreSQL, and SQLite registrations.

Important APIs and types: `sqlStore` holds an `xorm.Engine` and display address. `blob` maps to table `jfs_blob` with id, unique binary key, size, modified timestamp, and data blob. Methods implement `String`, `Get`, `Put`, `Head`, `Delete`, `List`, `newSQLStore`, and `removeScheme`.

Control flow and state: `Get` and `Put` read/write whole object bytes. `Put` uses PostgreSQL `ON CONFLICT` upsert when needed, otherwise insert then update. `Head` selects only key, modified, and size. `List` does ordered key pagination for simple prefix listing, but delimiter listing is unsupported. `newSQLStore` handles PostgreSQL schema/search-path restrictions, maps postgres to `pgx`, sets xorm log level from JuiceFS logger, prefixes table names with `jfs_`, and `Sync2`s the schema.

Persistence and integration: data is stored in the SQL database as one row per object. Driver registration files call `newSQLStore`.

Risks and test signals: whole-object reads/writes make this unsuitable for very large objects. Key column size is 255 bytes. SQL quoting uses backticks, which may be driver-sensitive. No SQL-object tests are in this subset.
