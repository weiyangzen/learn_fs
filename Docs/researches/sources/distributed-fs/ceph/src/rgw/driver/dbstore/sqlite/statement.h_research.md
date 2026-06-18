# sources/distributed-fs/ceph/src/rgw/driver/dbstore/sqlite/statement.h

## Purpose
Declares RAII pointer aliases and helper functions for prepared SQLite statement use in the config-store layer.

## APIs, Flow, And State
`stmt_ptr` owns `sqlite3_stmt*` and finalizes it. `stmt_binding` is non-owning and clears bindings on destruction. `stmt_execution` is non-owning and resets execution state on destruction. Function declarations cover prepare, binding of NULL/text/int values, zero-row and one-row execution expectations, column reads, text-row list reads, and raw query execution.

## Dependencies And Integration
Depends on `sqlite3.h`, `std::span`, strings, and `DoutPrefixProvider`. Included by `connection.h` and used by `config/sqlite.cc`.

## Risks And Test Signals
The non-owning RAII aliases rely on callers never outliving the owning `stmt_ptr`. `stmt_binding` and `stmt_execution` can be constructed around the same raw statement at the same time, so call ordering remains a convention. Tests should verify bindings are cleared between statement reuses and statements are reset after both success and exceptions.
