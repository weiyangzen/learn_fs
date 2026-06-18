# Research: sources/distributed-fs/ceph-client/rust/syn/mac.rs

## Purpose
`mac.rs` defines the AST for a Rust macro invocation and the delimiter abstraction around macro bodies. It also provides helpers for parsing macro body tokens into typed syntax and printing macro invocations.

## Important APIs, Types, And Functions
`Macro` contains a module-style `Path`, a bang token, a `MacroDelimiter`, and the body `TokenStream`. `MacroDelimiter` distinguishes `Paren`, `Brace`, and `Bracket` delimiters and exposes `span()` plus the internal `is_brace()` helper used by item parsers to decide whether a trailing semicolon is required. `Macro::parse_body` and `parse_body_with` parse the stored body tokens with a caller-provided parser, scoping errors to the closing delimiter span for better diagnostics. `parse_delimiter` extracts a grouped token tree and returns the delimiter plus its stream.

## Control Flow
`Parse for Macro` parses a module-style path, `!`, then delegates to `parse_delimiter`. `parse_delimiter` uses a cursor step to require a `TokenTree::Group`; parenthesis, brace, and bracket groups are converted into Syn token structs using `DelimSpan`, while `Delimiter::None` is rejected. Printing emits the macro path in module style, the bang, and surrounds cloned body tokens with the original delimiter span.

## State And Persistence Behavior
There is no durable persistence. The macro body remains an opaque `TokenStream` until a caller invokes `parse_body*`. Delimiter spans are retained separately from body tokens for printing and diagnostics.

## Dependencies And Integration Points
This module integrates with `path`, `token`, Syn parsing, `proc_macro2::{TokenStream, TokenTree, Delimiter}`, `proc_macro2::extra::DelimSpan`, and `quote::ToTokens`. It is referenced by item, expression, pattern, type, trait item, impl item, and foreign item AST nodes.

## Risks
Macro contents are intentionally not parsed eagerly, so downstream code must choose an appropriate parser and handle arbitrary tokens. `Delimiter::None` groups are rejected, which is correct for Rust macro invocations but relevant if callers feed synthetic token streams. Semicolon behavior for macro items depends on `is_brace`, so delimiter changes affect parse/print compatibility.

## Test Signals
Tests should cover all three delimiters, rejection of delimiter-less groups, body parsing success and empty-body errors, span placement for body parse failures, path style printing, and item/trait/impl/foreign macro semicolon rules.
