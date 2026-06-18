## sources/distributed-fs/beegfs-rust/sqlite_check/src/lib.rs

### Purpose
Implements the `sql!` procedural macro, which validates literal SQL at compile time by preparing it against an in-memory SQLite database loaded with the generated management schema.

### Important APIs, Types, and Functions
- Global `DB_CONN: OnceLock<Arc<Mutex<rusqlite::Connection>>>` caches one schema-loaded in-memory connection per compiler process.
- `sql(input)` parses a string literal with `syn::LitStr`, prepares it on the cached connection, panics on invalid SQL, and returns the original token stream unchanged.
- `open_db()` opens an in-memory SQLite DB through the helper crate, reads `OUT_DIR/current.sql`, executes the schema, and returns the locked connection wrapper.

### Control Flow and State
The first macro invocation initializes the database from `OUT_DIR/current.sql`; later invocations reuse it. Each macro call prepares but does not execute the statement, so it validates syntax and referenced schema names without needing data.

### Dependencies and Integration Points
Depends on `sqlite::open_in_memory`, `rusqlite`, `syn`, environment variable `OUT_DIR`, and a build-script-generated `current.sql`. Used in management code to catch invalid literal queries at compile time.

### Risks and Edge Cases
Invalid SQL panics during macro expansion, which is acceptable for compile-time validation but can produce terse errors. Only string literals are supported; dynamic SQL cannot be checked. It only prepares statements, so runtime-only constraints, parameter types, and data-dependent errors are not validated. Missing `OUT_DIR` or `current.sql` causes unwrap panics.

### Test Signals
No local tests. Compile-pass/fail tests should cover valid statements, invalid table/column names, non-literal inputs, and missing schema setup.
