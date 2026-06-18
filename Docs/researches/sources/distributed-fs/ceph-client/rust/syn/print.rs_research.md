# sources/distributed-fs/ceph-client/rust/syn/print.rs

## Purpose
`print.rs` provides a small printing helper for optional token fields that should emit a default token when absent.

## Important APIs, types, and functions
The only type is `TokensOrDefault<'a, T>(pub &'a Option<T>)`, with a `ToTokens` impl for `T: ToTokens + Default`.

## Control flow
`to_tokens` matches the wrapped option. `Some(t)` prints `t`; `None` constructs `T::default()` and prints that default token.

## State and persistence behavior
No state is retained and nothing is persisted. Defaults are created at print time.

## Dependencies and integration points
It depends on `proc_macro2::TokenStream` and `quote::ToTokens`. It is used by path printing, especially when a syntactically required token such as `as` or `::` should be emitted even if the AST stores it as optional.

## Risks
Default token spans are call-site spans, so diagnostics or formatting that rely on original spans may lose precision when a missing optional token is synthesized. The helper should only be used where synthesis is semantically correct.

## Test signals
Tests should cover both `Some` and `None` paths and verify default token emission in qualified path and turbofish printing.
