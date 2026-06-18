# sources/distributed-fs/ceph-client/rust/syn/token.rs

## Purpose
`token.rs` defines Syn's token marker types for Rust keywords, punctuation, delimiters, invisible groups, and the exported `Token!` type macro. These token types are used in AST fields, peeking, parsing, printing, and span construction.

## Important APIs, types, and functions
Key APIs are trait `Token`, private traits `Sealed` and `CustomToken`, `WithSpan`, macros `define_keywords`, `define_punctuation_structs`, `define_punctuation`, `define_delimiters`, `impl_deref_if_len_is_1`, `Token!`, and generated token structs for keywords/punctuation/delimiters. Special types include `Underscore` and none-delimited `Group`. Parsing helpers are `parsing::{keyword, peek_keyword, punct, peek_punct}`; printing helpers are `printing::{punct, keyword, delim}`.

## Control flow
Generated token `Parse` impls use `ParseStream::step` to consume a keyword or punctuator sequence. Punctuation parsing walks joint punctuation characters until the requested token is matched. Printing reconstructs multi-character punctuation with joint spacing except the final character. Delimiter `surround` builds a `Group` with the requested delimiter and span.

## State and persistence behavior
Token structs store spans or span arrays. There is no persistent state. Default constructors use `Span::call_site()`.

## Dependencies and integration points
This file integrates with `parse.rs`, `span::IntoSpans`, `proc_macro2`, `quote`, lifetime parsing, and all AST modules that store `Token![...]` fields.

## Risks
Macro-generated code is broad and feature-gated. Multi-character punctuation depends on joint spacing. `Deref` for single-span punctuation uses an unsafe transparent cast to `WithSpan`. This checkout appears to define `"." pub struct Dot/1` twice in `define_punctuation!`, which is a duplicate-definition compile risk.

## Test signals
Tests should cover every `Token!` mapping, keyword and punctuation parse/peek, joint versus alone punctuation, underscore as ident or punct, delimiter `surround`, span constructors, default spans, low-level token impls, and feature-gated trait impls.
