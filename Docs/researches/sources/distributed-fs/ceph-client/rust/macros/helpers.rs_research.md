# sources/distributed-fs/ceph-client/rust/macros/helpers.rs

## Purpose
`helpers.rs` contains shared utilities for the Rust kernel procedural macros: ASCII-only string literal parsing, proc-macro source file discovery, and cfg-attribute filtering.

## Important APIs, Types, And Functions
`AsciiLitStr` wraps `syn::LitStr`, implements `Parse`, `ToTokens`, and `value()`, and rejects non-ASCII strings. `file()` returns the current call-site source file using either `Span::source_file().path()` or stable `Span::file()` depending on `CONFIG_RUSTC_HAS_SPAN_FILE`. `gather_cfg_attrs()` filters attributes to `#[cfg(...)]`.

## Control Flow
`AsciiLitStr::parse` reads a literal and validates `value().is_ascii()`. `file()` compiles one of two span APIs using cfg flags. `gather_cfg_attrs` is a simple iterator adapter used by macros that need to propagate cfg gates to generated items.

## State And Persistence
No persistent state is kept. The file provides parser wrappers and helpers only.

## Dependencies And Integration Points
It depends on `proc_macro`, `proc_macro2`, `quote`, and `syn`. `module.rs` uses `AsciiLitStr` for module metadata, `kunit.rs` uses `file()` for assertion source reporting, and `vtable.rs` uses `gather_cfg_attrs`.

## Risks And Edge Cases
ASCII validation prevents invalid kernel metadata strings but also rejects legitimate Unicode in fields that use `AsciiLitStr`. The `file()` helper depends on compiler feature cfgs matching the actual proc-macro API. `gather_cfg_attrs()` only preserves `cfg` attributes, not `cfg_attr`.

## Test Signals
Useful tests include ASCII and non-ASCII metadata literals, source-file path reporting under both compiler cfgs, and cfg propagation through vtable and KUnit-generated items.
