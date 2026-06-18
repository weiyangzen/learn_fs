# File Research: sources/cow-pools/bcachefs-tools/src/commands/completions.rs

This file implements the `bcachefs completions` command.

Behavior:
- Uses clap’s derive parser for a single `Shell` argument.
- Calls `clap_complete::generate()` against `super::build_cli()`.
- Writes completions to stdout.
- Registers the command as a typed `CmdDef`.

Supported shells are those provided by `clap_complete::Shell`.
