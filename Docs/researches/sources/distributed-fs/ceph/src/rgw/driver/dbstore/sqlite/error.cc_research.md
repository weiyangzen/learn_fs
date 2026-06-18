# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/error.cc

## Purpose
Defines the custom `std::error_category` for SQLite primary and extended result codes.

## APIs, Flow, And State
`error_category()` returns a static category named `dbstore:sqlite`. `message()` delegates to `sqlite3_errstr()`. `default_error_condition()` masks the low eight bits, making extended result codes compare equal to their primary result-code conditions.

## Dependencies And Integration
Used by `sqlite::error`, `open_database()`, and statement helpers to turn SQLite integer results into `std::error_code` and `std::error_condition`.

## Risks And Test Signals
The low-byte masking intentionally groups extended errors by primary code, while still allowing exact extended-code comparison. Tests should assert that `SQLITE_CONSTRAINT_PRIMARYKEY` matches both `errc::primary_key_constraint` and primary `errc::constraint` semantics.
