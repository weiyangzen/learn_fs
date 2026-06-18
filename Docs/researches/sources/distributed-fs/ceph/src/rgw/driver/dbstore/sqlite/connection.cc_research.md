# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/connection.cc

## Purpose
Implements SQLite database opening for the config-store SQLite wrapper layer.

## APIs, Flow, And State
`open_database(filename, flags)` calls `sqlite3_open_v2()`, throws `std::system_error` on failure using the local SQLite error category, enables extended result codes with `sqlite3_extended_result_codes(db, 1)`, and returns an owning `db_ptr`.

## Dependencies And Integration
Depends on `sqlite3`, `connection.h`, and `error.h`. `ConnectionFactory` in `connection.h` calls this function for the config-store connection pool.

## Risks And Test Signals
Failure handling throws before returning an owning pointer; callers must catch exceptions at a higher boundary. Extended result codes are essential for the implementation’s constraint translation, so tests should verify primary-key/foreign-key/unique errors are distinguishable.
