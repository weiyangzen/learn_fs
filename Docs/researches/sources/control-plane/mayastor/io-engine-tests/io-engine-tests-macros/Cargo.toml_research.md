<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/Cargo.toml -->
# sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/Cargo.toml

Purpose: Manifest for a small proc-macro crate used by `io-engine-tests`.

Important API surface: declares `[lib] proc-macro = true`, allowing `src/lib.rs` to export attribute macros. Dependencies are `proc-macro2`, `quote`, and `syn` with `extra-traits`, enough to parse function items and emit wrapper code.

Integration points: consumed by the parent test-support crate and re-exported as `spdk_test`, so tests can mark async SPDK tests with a single attribute.

State and persistence: no runtime state in the manifest. The generated macro code relies on `tokio` and `io_engine_tests` being available from the consuming test crate.

Risks and test signals: macro crate versions are pinned outside the workspace, so proc-macro parsing behavior can shift only on explicit version changes. `cargo test -p io-engine-tests-macros` mostly validates compilation; downstream macro expansion tests are more useful.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/Cargo.toml -->
