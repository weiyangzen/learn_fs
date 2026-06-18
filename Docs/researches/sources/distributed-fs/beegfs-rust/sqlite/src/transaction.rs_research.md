## sources/distributed-fs/beegfs-rust/sqlite/src/transaction.rs

### Purpose
Adds convenience methods for rusqlite transactions and helper functions for array parameters and affected-row validation.

### Important APIs, Types, and Functions
- `TransactionExt` defines `execute_cached`, `query_row_cached`, and `query_map_collect`.
- Implementation for `Transaction<'_>` wraps `prepare_cached` plus execute/query helpers.
- `rarray_param(iter)` converts an iterator into `Rc<Vec<rusqlite::types::Value>>` for use with `rarray(?n)` and the loaded carray/array module.
- `check_affected_rows(affected, allowed)` returns success only if `affected` is in the allowed set; otherwise it maps to `rusqlite::Error::StatementChangedRows`.

### Control Flow and State
All helpers are synchronous transaction utilities. Cached statement preparation is delegated to rusqlite's transaction cache. `rarray_param` materializes values into an `Rc` for rusqlite parameter binding.

### Dependencies and Integration Points
Depends on `rusqlite`, `anyhow`, and `Rc`. Used by database access layers to reduce boilerplate and validate mutations.

### Risks and Edge Cases
`rarray_param` allocates the entire iterator, so huge arrays can be memory-heavy. `check_affected_rows` converts a rusqlite error through anyhow and back to `Result<()>`; callers get generic anyhow context unless they inspect the source. Statement caching effectiveness depends on stable SQL strings.

### Test Signals
No local tests. Useful tests should exercise cached query helpers, `rarray_param` with the loaded array module, and affected-row validation for zero/one/many rows.
