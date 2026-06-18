# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/connection.h

## Purpose
Declares RAII connection ownership and the connection factory used by the config-store SQLite connection pool.

## APIs, Flow, And State
`db_ptr` is a `std::unique_ptr<sqlite3, db_deleter>` that closes databases with `sqlite3_close()`. `Connection` owns a `db_ptr` and a `std::map<std::string_view, stmt_ptr>` for lazily prepared statement caching. `ConnectionFactory` captures a URI and flags and returns a `std::unique_ptr<Connection>` when invoked.

## Dependencies And Integration
Depends on SQLite C API, local `sqlite/statement.h`, and `DoutPrefixProvider`. Used by `config/sqlite.cc` through `ConnectionPool`.

## Risks And Test Signals
Statement cache keys are `std::string_view`; current call sites use string literals, which is safe, but dynamic temporary keys would dangle. `sqlite3_close()` can fail if statements remain unfinalized, but the connection member order finalizes `statements` before `db` because members are destroyed in reverse declaration order. Tests should exercise repeated calls to confirm prepared statements are reused and finalized cleanly.
