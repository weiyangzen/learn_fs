# sources/cloud-native/nydus/api/src/error.rs

## Purpose
This module provides standardized `std::io::Error` construction macros for the Nydus API crate, with optional feature-gated backtrace/error-location logging.

## Important APIs, Types, and Functions
- `make_error(err, raw, file, line)` logs debug context and optional backtrace when `error-backtrace` is enabled and `RUST_BACKTRACE` is not `0`, then returns the original error.
- `define_error_macro!` and `define_libc_error_macro!` generate exported macros.
- Exported macros include `einval!`, `enoent!`, `ebadf!`, `eacces!`, `enotdir!`, `eisdir!`, `ealready!`, `enosys!`, `epipe!`, `eio!`, `last_error!`, and `eother!`.
- `bail_einval!` and `bail_eio!` return early with formatted errors.

## Control Flow
Callers invoke a macro with no argument for a basic error or one argument for contextual logging through `make_error`. Bail macros format a message and immediately return `Err(...)`. With `error-backtrace`, logging behavior depends on `RUST_BACKTRACE`.

## State and Persistence
There is no persistent state. Side effects are log messages when the feature is enabled. The macros embed `file!()` and `line!()` call-site metadata.

## Dependencies and Integration Points
The module depends on `libc` error constants, `std::io`, optional `backtrace`, and logging macros. It is exported at crate level and used by API and service code that wants errno-compatible errors.

## Risks and Edge Cases
The macro TODO notes no full format-string support for base error macros; only the bail macros format. `eother!()` creates an `Other` error with empty message. With `error-backtrace`, context is logged but the returned error is still the original value, so callers do not see enriched messages unless using the zero-argument generated form.

## Test Signals
Unit tests cover errno macro kinds, context variants, custom macros, `make_error`, bail macro early returns, formatted bail messages, and success paths. Feature-enabled backtrace logging needs separate feature-specific CI to observe log behavior.
