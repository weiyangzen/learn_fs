# Research: sources/distributed-fs/ceph-client/rust/syn/lifetime.rs

## Purpose
`lifetime.rs` defines the AST representation of a Rust lifetime such as `'a`, including construction, span handling, parsing, printing, display, ordering, equality, and hashing behavior.

## Important APIs, Types, And Functions
`Lifetime` stores two pieces of state: `apostrophe: Span` and `ident: proc_macro2::Ident`. `Lifetime::new(symbol, span)` validates that the symbol begins with an apostrophe, is not only an apostrophe, and that the name after the apostrophe satisfies Syn's identifier XID rules. `span()` joins the apostrophe and identifier spans when possible, and `set_span()` updates both components. Formatting prints the apostrophe followed by the identifier. Equality, ordering, and hashing are based on the identifier, not the apostrophe span.

## Control Flow
Parsing is feature-gated under `parsing` and uses `ParseStream::step` with the token cursor's `lifetime()` primitive. If no lifetime token is present, it produces `expected lifetime`. Printing constructs a joint apostrophe punctuation token with the stored apostrophe span and then emits the identifier.

## State And Persistence Behavior
There is no durable persistence. The value preserves token span state for diagnostics and code generation. The equality model intentionally ignores span, making lifetimes with the same textual identifier compare equal even if they came from different source locations.

## Dependencies And Integration Points
This module depends on `proc_macro2::{Ident, Span}`, `crate::ident::xid_ok`, `crate::lookahead` for token marker integration, Syn's `Parse` trait, and `quote::ToTokens` for printing. It is used throughout generics, type references, receivers, and bounds.

## Risks
`Lifetime::new` panics on invalid input rather than returning `Result`, which is appropriate for construction APIs but risky if callers pass untrusted strings. Span joining can fail and falls back to the apostrophe span, so diagnostics may be less precise for synthesized lifetimes. Equality ignoring span is correct for AST semantics but unsuitable for callers trying to distinguish source origins.

## Test Signals
Tests should cover valid Unicode/XID lifetime names, invalid names, empty apostrophe-only input, span update behavior, parse errors, `ToTokens` apostrophe spacing, and equality/hash behavior across different spans.
