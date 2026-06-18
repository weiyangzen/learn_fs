<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/.cargo/config.toml -->
# sources/control-plane/mayastor/io-engine/.cargo/config.toml

Purpose: Cargo target configuration ensuring io-engine test and binary execution uses the local privilege runner on Linux x86_64 and aarch64 targets.

Important configuration: sets `[target.x86_64-unknown-linux-gnu] runner = ".cargo/runner.sh"` and the same for `aarch64-unknown-linux-gnu`.

Dependencies and integration: integrates with Cargo's target runner mechanism. The referenced runner grants capabilities required by Mayastor/io-engine rather than requiring the entire cargo invocation to run as root.

State and persistence: no runtime state. It changes how `cargo run`/`cargo test` execute built binaries for these targets.

Risks and test signals: non-Linux or non-listed targets will not use the runner. Relative runner path assumes commands are launched with Cargo resolving from the package root. Test by running a small io-engine test and verifying `.cargo/runner.sh` is invoked.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/.cargo/config.toml -->
