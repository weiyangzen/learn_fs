<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/build.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/build.rs

**Purpose:** Build script that embeds SQLite migration metadata and the flattened current schema into the management binary build output.

**Important APIs/types/functions:** Reads `CARGO_MANIFEST_DIR/src/db/schema`, calls `sqlite::read_migrations`, writes `OUT_DIR/migrations.rs` from `sqlite::migrations_slice_code`, writes `OUT_DIR/current.sql` from `sqlite::flatten_migrations`.

**Control flow:** Cargo executes the script before compiling `mgmtd`; panics via `unwrap()` on missing env vars, migration read failure, code generation failure, or write failure.

**State and persistence behavior:** Writes generated files to Cargo `OUT_DIR`, not source. These files define the migration list and current schema compiled into the binary.

**Dependencies and integration points:** Depends on local `sqlite` build-dependency APIs and the `mgmtd/src/db/schema` migration tree. Runtime DB initialization/migration code includes the generated artifacts.

**Risks:** No `cargo:rerun-if-changed` directives are emitted, so Cargo's rebuild detection may be less precise unless defaults catch the migration directory. `unwrap()` failures are acceptable for build scripts but can be terse in CI logs.

**Test signals:** Touch/add a migration and rebuild `mgmtd`; verify generated migration slice and current schema update and DB migration tests still pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/build.rs -->
