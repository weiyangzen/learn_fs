# sources/distributed-fs/ceph-client/rust/macros/lib.rs

## Purpose
`macros/lib.rs` is the procedural macro crate entry point for Rust-for-Linux kernel macros. It documents and exposes module declaration, vtable helpers, C export checking, logging-format adaptation, identifier concatenation/pasting, and KUnit suite registration.

## Important APIs, Types, And Functions
Public proc-macro entry points are `module!`, `#[vtable]`, `#[export]`, `fmt!`, `concat_idents!`, `paste!`, and `#[kunit_tests]`. The file also declares submodules `concat_idents`, `export`, `fmt`, `helpers`, `kunit`, `module`, `paste`, and `vtable`.

## Control Flow
Each entry point parses `proc_macro::TokenStream` input with `syn::parse_macro_input!` where applicable, delegates to the specialized helper module, converts `syn::Error` into compile errors, and returns the generated token stream. `paste!` directly converts to `proc_macro2`, recursively expands `[< ... >]` groups, and returns the rewritten stream.

## State And Persistence
The crate itself stores no runtime state. Its generated code can create module metadata sections, init/exit functions, statics, KUnit arrays, no-mangle symbols, and associated constants, but those are owned by the expanded caller.

## Dependencies And Integration Points
It depends on Rust proc-macro infrastructure, `syn`, `proc_macro2`, and the helper modules in the same crate. Generated code integrates with kernel crates such as `kernel`, `pin_init`, module parameter support, KUnit, and bindgen bindings.

## Risks And Edge Cases
Because this file is the public macro facade, documentation and parser behavior must stay aligned with helper modules. Feature gates (`extract_if`, `proc_macro_span`) are tied to Rust compiler/Kconfig support. Errors should become compile diagnostics rather than panics, except for internal helpers like `paste` that currently panic on malformed paste syntax.

## Test Signals
High-value coverage includes trybuild-style expansion tests for every public macro, docs examples, kernel build tests under module and built-in cfgs, compiler-version cfg combinations, and negative tests that check useful compile errors for malformed input.
