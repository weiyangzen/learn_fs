## sources/distributed-fs/beegfs-rust/sqlite/Cargo.toml

### Purpose
Declares the `sqlite` helper crate used by BeeGFS Rust components for SQLite connection pooling, migrations, and transaction utilities.

### Important APIs, Types, and Functions
- Package metadata uses workspace edition/authors/docs/homepage/publish settings.
- Dependencies: `anyhow`, `log`, `tokio`, and `rusqlite` with the `backup` feature.

### Control Flow and State
No runtime control flow. The manifest enables features needed by source files, especially database backup support in `migration.rs`.

### Dependencies and Integration Points
The crate is consumed by management/database code and by the `sqlite_check` proc-macro crate. It relies on workspace dependency versions.

### Risks and Edge Cases
Workspace dependency changes can alter SQLite behavior globally. Only `backup` is explicitly enabled here; other rusqlite features such as bundled SQLite or array support must come from workspace configuration if needed.

### Test Signals
Build and test of the `sqlite` crate validate manifest dependency consistency.
