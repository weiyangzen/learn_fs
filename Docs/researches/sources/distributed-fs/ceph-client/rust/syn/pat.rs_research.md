# sources/distributed-fs/ceph-client/rust/syn/pat.rs

## Purpose
`pat.rs` defines Syn's pattern AST and the parser/printer for Rust patterns under the `full` feature. It reuses expression structs for const, literal, macro, path, and range pattern forms.

## Important APIs, types, and functions
The main enum is `Pat` with variants including `Const`, `Ident`, `Lit`, `Macro`, `Or`, `Paren`, `Path`, `Range`, `Reference`, `Rest`, `Slice`, `Struct`, `Tuple`, `TupleStruct`, `Type`, `Verbatim`, and `Wild`. Structs include `PatIdent`, `PatOr`, `PatParen`, `PatReference`, `PatRest`, `PatSlice`, `PatStruct`, `PatTuple`, `PatTupleStruct`, `PatType`, `PatWild`, and `FieldPat`. Parser entry points are `Pat::parse_single`, `parse_multi`, and `parse_multi_with_leading_vert`.

## Control flow
`parse_single` dispatches by lookahead to path/macro/struct/range, wildcard, box verbatim, literal/range, binding, reference, tuple/paren, slice, rest, and const-block forms. `multi_pat_impl` wraps one or more single patterns separated by top-level `|` into `Pat::Or`. Struct and tuple-struct parsers use `Punctuated`; range parsing converts bounds into expression-backed `PatRange`; slice parsing rejects unparenthesized open range patterns.

## State and persistence behavior
Pattern parsing is stateless beyond parse cursor advancement. Unsupported or intentionally preserved syntax, such as `box` patterns and const block tokens, is retained as `TokenStream` in `Pat::Verbatim`.

## Dependencies and integration points
It depends on attributes, members, paths and `QSelf`, `Punctuated`, types, expressions, macro delimiter parsing, `verbatim`, and block parsing for const patterns. Printing integrates with `FilterAttrs`, `path::printing`, and `quote::ToTokens`.

## Risks
Pattern grammar is context-sensitive and edition-sensitive around top-level or-patterns. Range parsing and slice range rejection are high-risk. This vendored file appears to contain duplicated source text in `pat_range` (`end` field assigned twice), which should be treated as a compile/test risk in this checkout.

## Test signals
Tests should cover function-parameter patterns versus match-arm patterns, leading `|`, struct shorthand fields with `ref` and `mut`, tuple singletons, rest patterns, open and closed ranges, slice rejection of unparenthesized ranges, macro patterns, const patterns, and round-trip printing.
