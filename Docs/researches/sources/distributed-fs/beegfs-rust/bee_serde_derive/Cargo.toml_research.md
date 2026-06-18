<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/bee_serde_derive/Cargo.toml -->
## sources/distributed-fs/beegfs-rust/bee_serde_derive/Cargo.toml

**Purpose:** Cargo manifest for the BeeGFS custom serialization derive macro crate.

**Important APIs/types/functions:** Defines package `bee_serde_derive` at version `0.1.0`, inherits edition/authors/docs/homepage/publish settings, sets `[lib] proc-macro = true`, and depends on `proc-macro2`, `quote`, and `syn`.

**Control flow:** Cargo compiles this crate as a procedural macro used by workspace message/types crates to derive BeeGFS classic wire serialization.

**State and persistence behavior:** Build-time only; no runtime persistence except generated impls compiled into downstream crates.

**Dependencies and integration points:** Supports `shared::bee_serde` consumers and the numerous BeeMsg types that derive `BeeSerde`.

**Risks:** `proc-macro2`, `quote`, and `syn` versions are direct crate-local dependencies rather than workspace-pinned here, so updates can alter macro parsing behavior. Macro path generation assumes downstream crates expose `crate::bee_serde`.

**Test signals:** Compile downstream crates deriving `BeeSerde`; run round-trip serialization tests in `shared`/`mgmtd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/bee_serde_derive/Cargo.toml -->
