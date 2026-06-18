# sources/distributed-fs/ceph-client/rust/quote/runtime.rs

## Purpose

This hidden module is the runtime support library for `quote!`, `quote_spanned!`, and `format_ident!`. It provides token push helpers, repetition iterator adapters, span extraction, and identifier fragment formatting adapters.

## Important APIs, types, and functions

It re-exports hidden `format`, `Option`, and aliases for `Delimiter`, `Span`, and `TokenStream`. `HasIterator` and `ThereIsNoIteratorInRepetition` are type markers combined with `BitOr`. `ext` defines `RepIteratorExt`, `RepToTokensExt`, and `RepAsIteratorExt` for iterators, non-iterable `ToTokens` values, slices, arrays, `Vec`, `BTreeSet`, references, and `RepInterp`. `RepInterp` prevents duplicate binding from advancing the same iterator twice. `get_span` extracts spans from `Span` or `DelimSpan`. Push helpers create groups, parse fallback tokens, respan token trees, push identifiers, lifetimes, underscores, and all punctuation combinations. `mk_ident` and `ident_maybe_raw` handle raw identifiers.

## Control flow

Quote macros call push helpers in token order. Spanned helpers create tokens and then recursively replace spans through `respan_token_tree`. Repetition setup calls `quote_into_iter` on each pounded variable; the type-level marker enforces that at least one iterator is present. `RepInterp::next` returns the already-bound value when a name appears multiple times in a repetition body.

## State and persistence behavior

State is local to token construction: mutable output streams, iterator cursors, temporary span values, and formatted identifier strings. There is no global persistence.

## Dependencies and integration points

It depends on `proc_macro2` token types, `TokenStreamExt`, `ToTokens`, `IdentFragment`, `BTreeSet`, slices, formatting traits, and `DelimSpan`. `quote/lib.rs` macro rules rely on the exact helper names and hidden types.

## Risks and test signals

Risks include ambiguous `quote_into_iter` trait resolution, duplicate repetition variables advancing incorrectly, recursive respanning missing nested groups, raw identifier construction panics, parse helper failures for unusual tokens, and punctuation spacing regressions. Tests should cover repetition over all supported collection shapes, duplicated metavariables, spanned nested groups, format-ident raw names, lifetime generation, punctuation string output, and compile-fail cases for repetition with no iterator.
