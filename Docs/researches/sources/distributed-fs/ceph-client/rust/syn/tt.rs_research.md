# sources/distributed-fs/ceph-client/rust/syn/tt.rs

## Purpose
`tt.rs` provides equality and hashing helpers for `proc_macro2::TokenTree` and `TokenStream` that compare structural token content rather than source spans.

## Important APIs, types, and functions
The helper wrappers are `TokenTreeHelper<'a>(pub &'a TokenTree)` and `TokenStreamHelper<'a>(pub &'a TokenStream)`, each implementing `PartialEq` and `Hash`.

## Control flow
`TokenTreeHelper::eq` recursively compares groups by delimiter and contained token trees, punctuation by character and spacing, literals by string form, and identifiers by equality. Hashing writes a variant discriminator, delimiter or punctuation details, recursive group contents, a group terminator, literal strings, and identifiers. `TokenStreamHelper` collects cloned streams into vectors, compares length, then compares helper-wrapped elements.

## State and persistence behavior
No persistent state. Token streams are cloned and collected transiently for comparison or hashing.

## Dependencies and integration points
It depends on `proc_macro2::{Delimiter, TokenStream, TokenTree}` and standard `Hash`. It is useful for `extra-traits` style equality/hash behavior where spans should not affect semantic token identity.

## Risks
Literal comparison by `to_string()` can conflate or distinguish forms according to proc-macro formatting rather than original source spelling. Collecting token streams into vectors allocates. Span-insensitive equality may be inappropriate for diagnostics-sensitive comparisons.

## Test signals
Tests should cover nested groups, delimiter differences, punctuation spacing differences, literal string forms, identifier equality, token stream length mismatches, equal streams with different spans, and hash/equality consistency.
