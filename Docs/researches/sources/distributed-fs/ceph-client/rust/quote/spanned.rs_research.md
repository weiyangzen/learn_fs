# sources/distributed-fs/ceph-client/rust/quote/spanned.rs

## Purpose

This hidden module provides the sealed `Spanned` trait used by `syn::spanned::Spanned`-style APIs to derive a representative span from spans, delimiter spans, or tokenizable values.

## Important APIs, types, and functions

`Spanned::__span` returns a `Span`. Implementations cover `Span`, `DelimSpan`, and all `T: ToTokens`. `join_spans` takes a token stream, uses the first and last token spans, tries `first.join(last)`, and falls back to the first span. A private sealed trait prevents external implementations.

## Control flow

For tokenizable values, `into_token_stream` materializes tokens, `join_spans` gets the first span, folds to the last span, and tries to join them. Empty token streams return `Span::call_site`.

## State and persistence behavior

No state persists. The representative span is computed from current token output, so it can change if a `ToTokens` implementation changes.

## Dependencies and integration points

It depends on `quote::ToTokens`, `proc_macro2::{Span, TokenStream}`, and `proc_macro2::extra::DelimSpan`. Syn uses this hidden support for span reporting.

## Risks and test signals

Risks include expensive tokenization for large ASTs, inaccurate spans when first/last cannot join, and call-site fallback hiding empty-token errors. Tests should cover empty streams, single tokens, multi-token values with joinable spans, delimiter spans, and non-joinable cross-file spans.
