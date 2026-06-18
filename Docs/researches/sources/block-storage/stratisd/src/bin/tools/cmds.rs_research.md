# File Research: sources/block-storage/stratisd/src/bin/tools/cmds.rs

Command registry and CLI definitions for `stratisd-tools`.

Commands:
- `stratis-dumpmetadata`: reads Stratis metadata from a device; accepts `--print-bytes/-b` and `--only pool`.
- `stratis-checkmetadata`: validates pool-level metadata JSON.
- `stratis-printmetadata`: prints a human-readable metadata representation.
- `stratis-legacy-pool`: creates a v1 pool for testing, with optional key and Clevis/Tang/TPM2 options.

Important structures:
- `ToolCommand` trait abstracts `name`, `run`, and help visibility.
- Each command owns a `clap::Command` builder and parses its own arguments.
- `cmds()` returns boxed command implementations for the multiplexer.

Testing:
- Parser debug assertions cover dump/check/print metadata commands.
