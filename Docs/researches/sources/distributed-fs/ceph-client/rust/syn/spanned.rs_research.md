# sources/distributed-fs/ceph-client/rust/syn/spanned.rs

## Purpose
`spanned.rs` defines Syn's `Spanned` trait, which returns a span covering a syntax tree node for diagnostics and quote-spanned code generation.

## Important APIs, types, and functions
The public trait is `Spanned: private::Sealed` with `fn span(&self) -> Span`. A blanket impl covers all `T: quote::spanned::Spanned` and delegates to `__span()`. Private sealing covers all such tokenizable types and, under `full` or `derive`, `QSelf`.

## Control flow
Calling `span()` delegates to quote's span computation. The module itself has no parser or printer control flow.

## State and persistence behavior
No state and no persistence. Span computation is derived from tokenization.

## Dependencies and integration points
It depends on `proc_macro2::Span` and `quote::spanned::Spanned`. It is used by diagnostics and by path printing for `QSelf` delimiter spans.

## Risks
Joined spans depend on compiler/proc-macro capabilities. On stable contexts where full span joining is unavailable, span may degrade to the first token. For broad diagnostics, `Error::new_spanned` may be more precise.

## Test signals
Tests should cover span results for empty token streams, simple nodes, multi-token nodes, and `QSelf`, plus diagnostic behavior using `quote_spanned!`.
