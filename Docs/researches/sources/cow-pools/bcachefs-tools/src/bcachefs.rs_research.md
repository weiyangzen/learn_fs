# File Research: sources/cow-pools/bcachefs-tools/src/bcachefs.rs

This is the Rust main entry point for the `bcachefs` CLI binary.

Responsibilities:
- Declares Rust modules for commands, device scanning, key handling, logging, qcow2, wrappers, HTTP, and utility code.
- Installs C-side fatal signal handlers early.
- Sets C stdout to line-buffered to reduce Rust/C output reordering.
- Handles symlink invocations:
  - `mkfs*` maps to `format`.
  - `fsck*` maps to `fsck`.
  - `mount.fuse*` maps to `fusemount`.
  - `mount*` maps to `mount`.
- Prints grouped command usage for missing/help commands.
- Supports hidden `_doc_gen` command to generate LaTeX CLI documentation.
- Calls `raid_init()` before dispatching commands.
- Initializes Linux shrinkers unless the command defers them.
- Warns if the running kernel lacks `CONFIG_RUST`.
- Dispatches to the command registry.

Documentation generation:
- Walks the clap command tree.
- Escapes LaTeX special characters.
- Converts `<<sec:...>>` references to LaTeX section references.
- Writes `doc/generated/cli-reference.tex`.

Dependencies:
- Uses generated C bindings from `bch_bindgen::c`.
- Uses `commands::COMMAND_GROUPS` and `commands::dispatch()`.
