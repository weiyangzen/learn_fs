## sources/distributed-fs/beegfs-rust/sqlite_check/Cargo.toml

### Purpose
Declares the `sqlite_check` procedural macro crate for compile-time validation of literal SQL statements against the BeeGFS management SQLite schema.

### Important APIs, Types, and Functions
- Package metadata uses workspace settings.
- `[lib] proc-macro = true` enables procedural macro export.
- Dependencies: local `sqlite` crate, `syn` with `parsing`, and workspace `rusqlite`.

### Control Flow and State
No runtime behavior in the manifest. It configures the crate as a proc macro and wires dependencies needed by `src/lib.rs`.

### Dependencies and Integration Points
Consumed by crates that invoke the `sql!` macro. Depends on build scripts producing a schema file under `OUT_DIR`.

### Risks and Edge Cases
Proc-macro crates run at compile time; dependency or schema generation failures become build failures. The local path dependency requires workspace layout consistency.

### Test Signals
Builds of consumers using `sql!` validate the manifest. Dedicated compile-fail tests would be useful.
