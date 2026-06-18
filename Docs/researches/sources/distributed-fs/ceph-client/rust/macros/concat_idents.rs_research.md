# sources/distributed-fs/ceph-client/rust/macros/concat_idents.rs

## Purpose
This file implements the kernel `concat_idents!` procedural macro helper. It concatenates exactly two identifiers and emits one identifier whose span is taken from the second argument for better diagnostics at the call site.

## Important APIs, Types, And Functions
`Input` parses `a, b` as two `proc_macro2::Ident` values separated by a comma. `concat_idents(Input)` formats the two identifiers together, constructs a new `Ident` with `b.span()`, and returns it as a single-token `TokenStream`.

## Control Flow
The macro entry point in `macros/lib.rs` parses user input into `Input`. This helper performs no semantic lookup; it only joins token spellings. Invalid arity or non-ident tokens are rejected by `syn::Parse` before concatenation.

## State And Persistence
No runtime or persistent state is kept. All state is temporary parser output and a single emitted token stream.

## Dependencies And Integration Points
It depends on `proc_macro2` token types and `syn` parsing. It is re-exported through the `#[proc_macro] pub fn concat_idents` entry point and is intended for Rust kernel macro code that needs generated names.

## Risks And Edge Cases
Because it formats identifiers as strings, raw identifiers and hygiene need care. The span intentionally comes from the second identifier, so diagnostics point at the caller-provided suffix rather than the prefix. The helper only supports two identifiers; more complex pasting is handled by `paste.rs`.

## Test Signals
Useful tests cover successful prefix/suffix concatenation, malformed input, punctuation or literal rejection, raw identifier behavior, and diagnostics span placement on generated identifiers.
