# sources/distributed-fs/juicefs/pkg/object/sql_mysql.go

Purpose: registers the MySQL-backed SQL object store when `!nomysql` is enabled.

Important APIs and types: it imports `github.com/go-sql-driver/mysql` for side-effect driver registration and calls `Register("mysql", ...)` in `init`.

Control flow and state: the registration closure strips any URI scheme from `addr` using `removeScheme`, then calls `newSQLStore("mysql", ..., user, pass)`. All object behavior, persistence schema, listing, and risks are inherited from `sql.go`.

Persistence and integration: one MySQL database stores objects in the `jfs_blob` table through xorm. Credentials are supplied through `CreateStorage` arguments and folded into the DSN in `newSQLStore`.

Risks and test signals: this file has no logic beyond registration, so primary risks are build tags and correct side-effect import availability. No MySQL-specific tests are present.
