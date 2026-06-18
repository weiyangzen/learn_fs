# Research: sources/distributed-fs/ceph-client/rust/syn/lit.rs

## Purpose
`lit.rs` defines Syn's literal AST, literal constructors/accessors, token conversion, parsing, printing, debug/clone/extra traits, and internal literal-value decoding. It covers string, byte string, C string, byte, char, integer, float, boolean, and verbatim literals.

## Important APIs, Types, And Functions
`Lit` is the central enum. Structured wrappers include `LitStr`, `LitByteStr`, `LitCStr`, `LitByte`, `LitChar`, `LitInt`, `LitFloat`, and `LitBool`. String-like and byte-like literals store a `LitRepr` containing the original `proc_macro2::Literal` and suffix. Numeric literals store `LitIntRepr` or `LitFloatRepr`, retaining the original token plus normalized `digits` and suffix. Public constructors such as `LitStr::new`, `LitInt::new`, and `LitBool::new` synthesize tokens with spans. Accessors expose decoded values, suffixes, spans, mutable span updates, and cloned tokens. `LitStr::parse` and `parse_with` parse the literal contents as Rust tokens after respanning every token to the literal's span.

## Control Flow
`Parse for Lit` first accepts cursor literals, then boolean identifiers, then a `-` punctuation followed by numeric literal via `parse_negative_lit`. Specific literal parsers parse `Lit` and downcast to the requested variant. Internal `value::Lit::new` classifies a `proc_macro2::Literal` by its textual representation. String and byte parsers decode cooked/raw syntax, escape sequences, line continuations, suffixes, Unicode escapes, and C string nul restrictions. `parse_lit_int` converts binary/octal/hex/decimal literals into normalized base-10 digits using `BigInt`; `parse_lit_float` removes underscores and normalizes exponent syntax while preserving a valid suffix.

## State And Persistence Behavior
No filesystem persistence exists. The module deliberately stores both source token identity and decoded/normalized data. This dual state lets `ToTokens` preserve the original literal spelling while APIs like `base10_digits()` and `value()` provide semantic content. Parsing via `LitStr::parse_with` creates transient respanned token streams so diagnostics point at the original string literal.

## Dependencies And Integration Points
The module depends on `proc_macro2::{Literal, Ident, Span, TokenStream, TokenTree, Punct}`, Syn's parser and error APIs, `crate::bigint::BigInt`, `crate::ident::xid_ok`, token lookahead integration, `quote::ToTokens`, and standard `CStr/CString`. It is used by expressions, attributes/meta parsing, token peeking, and procedural macro helper APIs.

## Risks
Several internal decoders use `assert!`, `assert_eq!`, `unwrap`, and `panic!` under the assumption that `proc_macro2` only provides syntactically valid literals. If callers construct invalid strings for `LitInt::new` or `LitFloat::new`, these APIs panic. Escape decoding is subtle, especially C string nul rejection, raw string pound counting, negative numeric spans, and suffix validation through `xid_ok`. Classification based on `Literal::to_string()` is tied to proc-macro2 formatting.

## Test Signals
Tests should cover all literal kinds, cooked/raw string and byte string escapes, C string nul errors, Unicode escapes with underscores and length limits, byte/char escape limits, numeric bases and underscore normalization, float exponent forms, suffix acceptance/rejection, negative int/float parsing, respanned `LitStr::parse_with` errors, and print round trips preserving token spelling.
