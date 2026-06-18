# File Research: sources/block-storage/thin-provisioning-tools/src/version.rs

## Purpose
Centralizes command-line version handling.

## Main Components
- `tools_version!` macro expands to `env!("CARGO_PKG_VERSION")`.
- `version_args(cmd)` adds an exclusive `-V`/`--version` boolean flag to a `clap::Command`.
- `display_version(matches)` checks the `VERSION` flag, writes the package version and newline to stdout, flushes, and exits with status 0.

## Behavior
Broken pipe and stdout write/flush errors are ignored deliberately. If the version flag is absent, `display_version()` returns normally.

## Dependencies and Interactions
This module depends on `clap` for argument definition and `std::io::Write` for output. It is meant to be reused by individual thin-provisioning tool binaries.

## Research Notes
The version flag uses the argument id `"VERSION"` and is exclusive, so it should short-circuit other command modes when present.
