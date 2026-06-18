# sources/distributed-fs/ceph-client/rust/macros/paste.rs

## Purpose
`paste.rs` implements a small identifier-pasting macro similar to the `paste` crate, limited to identifiers and literals inside `[< ... >]` groups. It supports case modifiers and span selection for generated identifiers.

## Important APIs, Types, And Functions
`expand(tokens: &mut Vec<TokenTree>)` is the recursive entry. `concat()` creates one identifier from a bracket group. `concat_helper()` walks paste segments and returns string/span pairs. Supported modifiers are `:span`, `:lower`, and `:upper`.

## Control Flow
Expansion recursively descends into groups. A bracket group whose first token is `<` and last token is `>` is replaced by a concatenated `Ident`; all other groups are recursively expanded and rebuilt with the original delimiter/span. After recursion, a reverse pass removes invisible delimiter groups adjacent to `::` path separators because path segments cannot contain such groups.

## State And Persistence
No state persists outside the token vector being rewritten. Span state is local to a paste group; the `span` modifier may select one segment span as the generated identifier span.

## Dependencies And Integration Points
It depends only on `proc_macro2` token types. `macros/lib.rs` exposes it as `paste!` for kernel macro authors who need generated identifiers without depending on the full external `paste` crate behavior.

## Risks And Edge Cases
Malformed paste syntax causes panics rather than structured `syn::Error` diagnostics. The implementation strips quotes from string literals and `r#` from raw identifiers before concatenation. It does not support lifetimes or doc-string concatenation. Only ASCII-ish identifier validation is left to `Ident::new`, so invalid pasted names fail there.

## Test Signals
Useful tests include nested group expansion, literals plus identifiers, raw identifiers, lower/upper/span modifiers, duplicate `span` modifier rejection, invisible group removal around paths, and malformed token negative tests.
