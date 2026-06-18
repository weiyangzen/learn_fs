# sources/distributed-fs/ceph-client/rust/syn/custom_punctuation.rs

## Purpose

This file defines the public `syn::custom_punctuation!` macro and its private helper macros. It lets macro authors declare a Rust type that represents a multi-character punctuation sequence, such as `<=>` or `</>`, while integrating with Syn's standard parse, peek, print, span, clone, debug, equality, and hash conventions.

## Important APIs, Types, and Functions

- `custom_punctuation!($ident, $($tt)+)`: exported macro that generates a public struct with `pub spans`, a constructor-like function named after the type, and feature-gated trait impls.
- `impl_parse_for_custom_punctuation!`: with `parsing`, implements `CustomToken` and `Parse`. `peek` uses `__private::peek_punct`, `display` formats the punctuation for diagnostics, and parsing delegates to `__private::parse_punct`.
- `impl_to_tokens_for_custom_punctuation!`: with `printing`, implements `quote::ToTokens` through `__private::print_punct`.
- `impl_clone_for_custom_punctuation!`: with `clone-impls`, makes the punctuation token `Copy` and `Clone`.
- `impl_extra_traits_for_custom_punctuation!`: with `extra-traits`, implements `Debug`, `Eq`, `PartialEq`, and `Hash`; equality ignores spans, matching built-in token behavior.
- `custom_punctuation_repr!`: computes the span storage type as `[Span; N]`.
- `custom_punctuation_len!`: maps valid punctuation token fragments to span counts and rejects invalid fragments in strict mode.
- `stringify_punct!`: concatenates stringified punctuation pieces for parser/printer helpers.

## Control Flow

The primary macro emits a token struct and a same-named constructor function. The constructor accepts any `IntoSpans<[Span; N]>`, validates all punctuation fragments with `custom_punctuation_len!(strict, ...)`, and converts the caller's span input into the generated `spans` field. Inside a private constant block, feature-gated helper macros expand to trait impls or to empty expansions depending on enabled Syn features.

Parsing flow is: parser calls `input.peek(GeneratedToken)` or `input.parse::<GeneratedToken>()`; the generated `CustomToken` reports the target punctuation string; `parse_punct` consumes the exact punctuation and returns the span array; the generated constructor wraps those spans. Printing flow is the inverse: `ToTokens::to_tokens` passes the punctuation string and span array into `print_punct`.

## State and Persistence

Generated punctuation values are pure syntax nodes. Their only state is the span array. There is no heap persistence, I/O, global mutation, or caching. Trait behavior intentionally treats spans as metadata: `PartialEq` always returns true for two values of the same punctuation type, and `Hash` contributes no span data.

## Dependencies and Integration Points

The macro depends on reexports from `crate::__private` in `export.rs`, including `Span`, `IntoSpans`, `CustomToken`, `ToTokens`, and punctuation parse/print functions. It integrates with `crate::parse::Parse`, `crate::buffer::Cursor`, `quote::ToTokens`, and Syn's feature flags (`parsing`, `printing`, `clone-impls`, `extra-traits`). The generated APIs are intended to behave like built-in token types from `token.rs`, so they can be used in `Punctuated`, parser lookahead, and `quote!` interpolation.

## Risks and Edge Cases

The punctuation grammar is limited to the fragments enumerated in `custom_punctuation_len!`; unsupported fragments fail through the strict branch. The lenient branch returns zero for unknown fragments when computing representation type, but the constructor's strict validation prevents accepting invalid definitions. Multi-character punctuation span arrays must stay aligned with parser/printer assumptions. Feature-gated empty helper expansions mean generated types compile in reduced feature builds but lose parse/print/clone/extra-trait capabilities.

## Test Signals

There are no inline unit tests in this file. The documentation example exercises custom punctuation inside a `Punctuated<Expr, PathSeparator>` parser. Strong test signals would include compile-pass tests for valid punctuation definitions, compile-fail tests for invalid fragments, round-trip parse/quote tests preserving span counts, and feature-matrix tests for the empty helper expansions.
