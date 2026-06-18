# File Research: sources/block-storage/stratisd/src/systemd/bindings.rs

## Purpose

Includes generated systemd FFI bindings.

## Main Types and Behavior

- Suppresses naming, dead-code, FFI, and clippy lints typical of bindgen output.
- Includes `${OUT_DIR}/bindings.rs`.

## Integration Points

Used by `systemd/mod.rs` for `sd_notify` and `syslog`.
