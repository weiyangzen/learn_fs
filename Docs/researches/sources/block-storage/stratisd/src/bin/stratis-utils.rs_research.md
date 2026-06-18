# File Research: sources/block-storage/stratisd/src/bin/stratis-utils.rs

Top-level multiplexer for utility executables.

Key behavior:
- Imports `mod utils` and dispatches to `utils::cmds()`.
- Supports invocation as `stratis-utils <executable>` or as a symlink/name matching a concrete utility.
- Validates `<executable>` against known utility command names when invoked as `stratis-utils`.
- Extracts the basename from `argv[0]` to identify which utility to run.
- Returns `ExecutableError` for invalid executable names or non-string command names.

Registered commands come from `src/bin/utils/cmds.rs`: predict usage, decode device-mapper names, and systemd generators when enabled.
