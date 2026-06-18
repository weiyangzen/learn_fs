<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/examples/lvs-eval/main.rs -->
# sources/control-plane/mayastor/io-engine/examples/lvs-eval/main.rs

Purpose: CLI example for creating/importing an LVS pool, creating replicas/filler lvols, printing allocation internals, and optionally destroying or exporting the pool.

Important APIs/types: `CliArgs` defines disk, replica count, replica cluster count, cluster size, thin flag, metadata expansion, extent-table flag, pool name, destroy flag, and filler option. `main()` creates a `MayastorTest` runtime, then runs pool/replica operations inside it. `create_lvs()` builds `PoolArgs` with a fixed UUID. `create_replica()`, `create_filler_replica()`, and `create_lvol()` create lvols with deterministic UUID patterns and optional extent-table control.

Control flow: parse CLI, set global `G_USE_EXTENT_TABLE`, start a two-reactor Mayastor environment, create pool, create fillers/replicas until failure, print, optionally destroy fillers, then destroy or export pool.

State and dependencies: mutates the disk/pool passed by CLI. Depends on `io_engine_tests::MayastorTest`, LVS backend, clap, and version-info.

Risks and test signals: uses `static mut` for extent-table flag and fixed pool UUID, so concurrent/repeated runs can collide. Intended as manual diagnostic tooling; verify by inspecting printed blobstore state.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/examples/lvs-eval/main.rs -->
