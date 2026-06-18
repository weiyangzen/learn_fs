# File Research: sources/block-storage/stratisd/src/bin/stratisd-tools.rs

Top-level multiplexer for daemon/admin tools.

Key behavior:
- Imports `mod tools` and dispatches through `tools::cmds()`.
- Initializes `env_logger` from `RUST_LOG`, defaulting to logger defaults otherwise.
- Supports invocation as `stratisd-tools <executable>` or directly through a symlink/binary name.
- Builds top-level help listing tools whose `show_in_after_help()` returns true.
- Exits with code `1` for run errors and code `2` for unknown executable names.

This wrapper exposes metadata inspection/checking and legacy-pool test tooling.
