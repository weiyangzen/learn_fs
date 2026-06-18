# File Research: sources/block-storage/stratisd/src/stratis/mod.rs

## Purpose

Declares Stratis daemon runtime modules and re-exports the public runtime API.

## Main Types and Behavior

- Re-exports `StratisError`, `StratisResult`, `run`, and `VERSION`.
- Declares `dm`, `errors`, `ipc_support`, `keys`, `run`, module-inception `stratis`, `timer`, and `udev_monitor`.

## Integration Points

Imported by crate users and other modules as the main runtime facade.
