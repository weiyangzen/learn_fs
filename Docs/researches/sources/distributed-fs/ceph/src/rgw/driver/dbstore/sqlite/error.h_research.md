# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/error.h

## Purpose
Declares SQLite error wrappers and typed error conditions for the config-store SQLite helper layer.

## APIs, Flow, And State
`sqlite::error` derives from `std::runtime_error` and carries a `std::error_code`, with constructors from message/code, `sqlite3*` plus code, or current extended DB error. `enum class errc` names the primary/extended result codes currently handled: ok, busy, constraint, row, done, primary-key constraint, foreign-key constraint, and unique constraint. Helper functions create error codes/conditions, and `std::is_error_condition_enum` enables comparisons like `e.code() == sqlite::errc::busy`.

## Dependencies And Integration
Depends on `<system_error>` and `sqlite3.h`. Used throughout `config/sqlite.cc` and `sqlite/statement.cc` for exception-based error propagation.

## Risks And Test Signals
Only result codes needed by current code are modeled; new SQLite behaviors may collapse to `-EIO` until added. The category is not a standard generic category, so callers should compare against `sqlite::errc`, not errno. Unit tests should verify condition matching for primary and extended constraints.
