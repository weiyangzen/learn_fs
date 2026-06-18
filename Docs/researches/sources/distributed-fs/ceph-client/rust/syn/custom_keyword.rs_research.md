# sources/distributed-fs/ceph-client/rust/syn/custom_keyword.rs

## Purpose

This file implements `custom_keyword!`, allowing downstream parsers to define identifier-like tokens that parse, peek, print, clone, and expose spans like built-in Syn keyword token types.

## Important APIs, types, and functions

`custom_keyword!($ident)` emits a public struct named after the identifier with a `span` field, a constructor function accepting `IntoSpans<Span>`, a `Default` impl, and feature-gated parse, print, clone, and extra trait implementations. `impl_parse_for_custom_keyword!` implements `CustomToken` and `Parse`. `impl_to_tokens_for_custom_keyword!` prints the keyword as an `Ident`. `impl_clone_for_custom_keyword!` makes it `Copy`/`Clone`. `impl_extra_traits_for_custom_keyword!` implements debug, equality, and hash behavior.

## Control flow

Parsing uses `input.step` and checks `cursor.ident()` against `stringify!($ident)`. On match it returns the token with the parsed ident span and advances to `rest`; otherwise it produces an expected-keyword error. Peeking uses the same cursor ident check. Printing constructs a `syn::Ident` with the stored span and appends it to the output stream.

## State and persistence behavior

Each custom keyword token stores only its span. Equality and hash under `extra-traits` ignore span, matching token marker semantics.

## Dependencies and integration points

It depends on Syn private exports (`Span`, `IntoSpans`, `CustomToken`, `Parse`, `ToTokens`, `TokenStreamExt`, trait aliases) and `quote` printing. Downstream Syn parsers use it in `kw` modules for contextual keywords and DSL keys.

## Risks and test signals

Risks include accepting raw identifiers unexpectedly, feature-gated trait differences, constructor name collisions, span loss while printing, and lookahead error message regressions. Tests should cover parse success/failure, `peek`, default construction, printing with span, clone/copy when enabled, extra-trait behavior, and contextual keywords that overlap with ordinary identifiers.
