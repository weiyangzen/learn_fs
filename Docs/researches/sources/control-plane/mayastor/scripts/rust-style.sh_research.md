# sources/control-plane/mayastor/scripts/rust-style.sh

Purpose: Rust formatting wrapper using the repository linter environment.

Important APIs/types/functions: sets `FMT_OPTS` default to `--config imports_granularity=Crate`, sources `rust-linter-env.sh`, and runs `$CARGO fmt --all -- $FMT_OPTS`.

Control flow: linear shell execution.

State/persistence: modifies Rust files in place when formatting changes are needed.

Dependencies/integration: formatting gate for workspace Rust code; depends on rustfmt through the selected cargo toolchain.

Risks: default import granularity can reorder imports across the whole workspace. Running it in a dirty tree may mix unrelated formatting changes.

Test signals: clean formatter run leaves Rust code in expected style.
