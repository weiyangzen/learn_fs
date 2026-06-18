# sources/control-plane/mayastor/scripts/rust-linter.sh

Purpose: Rust clippy wrapper using the repository's SPDK Rust linter environment.

Important APIs/types/functions: sources `spdk-rs/scripts/rust-linter-env.sh` and runs `$CARGO clippy --all --all-targets --features=io-engine-testing -- -D warnings -A clippy::result-large-err`.

Control flow: linear shell execution.

State/persistence: read-only except build artifacts in target directory.

Dependencies/integration: CI style/lint gate for all Rust targets with io-engine testing features enabled.

Risks: depends on relative spdk-rs submodule path and exported `$CARGO`. Allows large error result lint while denying other warnings.

Test signals: exit `0` means clippy found no denied warnings.
