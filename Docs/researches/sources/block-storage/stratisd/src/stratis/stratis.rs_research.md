# File Research: sources/block-storage/stratisd/src/stratis/stratis.rs

## Purpose

Defines the daemon version constant.

## Main Types and Behavior

- `VERSION` is populated from Cargo package metadata with `env!("CARGO_PKG_VERSION")`.

## Integration Points

Re-exported by `stratis/mod.rs` and logged during daemon startup.
