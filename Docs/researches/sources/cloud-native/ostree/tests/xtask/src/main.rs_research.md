# sources/cloud-native/ostree/tests/xtask/src/main.rs

## Purpose
This Rust entry point parses the xtask command line and dispatches to the TMT runner module.

## Important APIs, Types, And Functions
It uses `anyhow::Result`, `clap::Parser`, module `tmt`, enum `Opt`, and `xshell::Shell`. The only enum variant is `RunTmt(tmt::RunTmtArgs)`.

## Control Flow
`main()` parses `Opt`, constructs an `xshell::Shell`, matches the selected command, and calls `tmt::run_tmt(&sh, args)` for `RunTmt`.

## State And Persistence
No persistent state is stored here. It creates a shell context for subprocess execution.

## Dependencies And Integration Points
This integrates the Rust clap CLI with the TMT implementation in `tmt.rs` and external command execution through `xshell`.

## Risks
Any new xtask command must be added to the enum and match. Currently all behavior is delegated, so argument parsing is the main local risk.

## Test Signals
Compilation and `--help` output validate this file. Runtime validation comes from `run-tmt` execution in `tmt.rs`.
