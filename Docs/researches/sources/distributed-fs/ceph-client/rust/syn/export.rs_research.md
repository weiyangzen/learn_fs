# sources/distributed-fs/ceph-client/rust/syn/export.rs

## Purpose

This file provides a hidden internal reexport surface used by Syn's public macros. By routing macro-generated code through `$crate::__private`, Syn can refer to standard-library traits, proc-macro types, quote traits, parser helpers, and token helpers without relying on the caller's imports or prelude.

## Important APIs, Types, and Functions

- Hidden reexports of `Clone`, `Eq`, `PartialEq`, `Default`, `Debug`, `Hash`, `Hasher`, `Copy`, `Option::{None, Some}`, `Result::{Err, Ok}`, `concat`, and `stringify`.
- `Formatter<'a>` and `FmtResult` aliases for debug impls.
- Primitive aliases `bool` and `str`.
- `quote` reexport and `ToTokens`, `TokenStreamExt` when `printing` is enabled.
- `Span`, `TokenStream2`, and `TokenStream` aliases for `proc_macro2` and `proc_macro` token streams.
- Parsing helpers: `parse_braces`, `parse_brackets`, `parse_parens`, `peek_punct`, `parse_punct`, and `CustomToken`.
- Printing helper: `print_punct`.
- `IntoSpans` reexport for token constructors.
- `parse_quote` reexport when both parsing and printing are enabled.
- `private(pub(crate) ())`: hidden marker type.

## Control Flow

There is no runtime control flow. The file is a compile-time namespace that macros reference after expansion. Feature flags decide which names exist, matching the capabilities of the macro expansions that use them.

## State and Persistence

No state or persistence is present. All items are aliases or reexports.

## Dependencies and Integration Points

This module is tightly integrated with `custom_punctuation!`, `custom_keyword!`, token constructors, quote integration, and parse quote macros. It depends on `proc_macro2`, optionally `proc_macro`, `quote`, `group`, `span`, `parse_quote`, and `token` modules.

## Risks and Edge Cases

Because public macros expand to this hidden API, renaming or removing any reexport can be a breaking change even though the items are `doc(hidden)`. Feature gating must stay synchronized with macro helper expansions; for example, printing macros must not reference `ToTokens` unless the `printing` feature exposes it. Lowercase aliases for primitives intentionally avoid caller shadowing but can surprise readers.

## Test Signals

There are no inline tests. Compile-time macro expansion tests are the strongest signal: custom punctuation/keyword use from downstream crates, with and without relevant feature flags, plus no-std-style import isolation where caller scopes do not import any of these traits.
