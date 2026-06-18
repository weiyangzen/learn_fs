# File Research: sources/block-storage/stratisd/src/lib.rs

## Purpose

Defines the crate-level feature-gated module surface and macro imports.

## Main Types and Behavior

- Imports macro crates under `engine` feature: `nix`, `serde_derive`, `log`, `serde_json`, `libcryptsetup_rs`.
- Test-only macro imports include `proptest` and `assert_matches`.
- Declares internal `macros` under `engine`.
- Exposes `engine`, `dbus`, `stratis`, `jsonrpc`, and `systemd` according to features.

## Integration Points

Controls whether the full engine, D-Bus API, min JSON-RPC API, and systemd compatibility modules are compiled.
