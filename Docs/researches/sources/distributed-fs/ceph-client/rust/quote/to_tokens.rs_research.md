# sources/distributed-fs/ceph-client/rust/quote/to_tokens.rs

## Purpose

This file defines `ToTokens`, the core interpolation trait for values that can be written into `quote!` output streams.

## Important APIs, types, and functions

`ToTokens::to_tokens` is required. `to_token_stream` and `into_token_stream` are convenience methods. Blanket implementations forward for references, mutable references, `Cow`, `Box`, `Rc`, and `Option`. Primitive implementations convert strings to string literals, integers/floats to suffixed literals, chars to character literals, booleans to `true`/`false` identifiers, C strings to C string literals, and proc-macro2 token types by clone/extend.

## Control flow

Most implementations append one token. `Option` appends only when `Some`. `TokenStream` extends by one cloned stream and overrides `into_token_stream` to avoid rebuilding.

## State and persistence behavior

The only mutation is appending to the provided `TokenStream`. Primitive numeric output persists type suffixes, which matters for generated syntax.

## Dependencies and integration points

It depends on `TokenStreamExt`, `alloc` wrappers, `proc_macro2` token types, `Span`, and `std::ffi::{CStr, CString}`. `quote!` calls it for every interpolation, and `syn` implements it for AST nodes under printing features.

## Risks and test signals

Risks include unwanted numeric suffixes in contexts like tuple indexing, boolean span choices, string escaping, C string support across compiler versions, and clone costs for large token streams. Tests should cover primitive interpolation output, `Option` omission, wrapper forwarding, token type preservation, and generated code that requires unsuffixed literals via domain-specific types such as `syn::Index`.
