# sources/distributed-fs/ceph-client/rust/syn/data.rs

## Purpose

This file models the data payloads used by Rust structs and enum variants: variants, named fields, tuple fields, unit fields, and individual field definitions. It provides uniform iteration over field shapes, conversion to field members for code generation, parsing for derive/full syntax, and printing support.

## Important APIs, Types, and Functions

- `Variant`: enum variant with outer attributes, `ident`, `fields`, and optional discriminant `(=, Expr)`.
- `Fields`: syntax enum with `Named(FieldsNamed)`, `Unnamed(FieldsUnnamed)`, and `Unit`.
- `FieldsNamed`: brace-delimited `Punctuated<Field, Comma>`.
- `FieldsUnnamed`: paren-delimited `Punctuated<Field, Comma>`.
- `Field`: field attributes, visibility, `FieldMutability`, optional identifier, optional colon, and `Type`.
- `Fields::iter`, `iter_mut`, `len`, `is_empty`: shape-independent accessors.
- `Fields::members`: returns cloneable `Members` iterator over `Member::Named` or `Member::Unnamed(Index)`.
- `Members`: iterator that maps fields to expression members; unnamed fields receive monotonically increasing indexes and spans derived from the field type when parsing+printing are enabled.
- `parsing::Field::parse_named` and `parse_unnamed`: parse braced and tuple fields.

## Control Flow

Parsing a `Variant` first consumes outer attributes, then intentionally parses and discards a `Visibility`, then reads the variant identifier. It selects `Fields::Named`, `Fields::Unnamed`, or `Fields::Unit` by peeking for braces or parentheses. If `=` follows, it parses a discriminant. Under `full`, the discriminant is a normal `Expr`; without `full`, it speculatively parses or scans an expression and preserves unsupported tokens as `Expr::Verbatim`.

`FieldsNamed` and `FieldsUnnamed` parse their delimiter content with `parse_terminated`, using the appropriate field parser. Named fields parse outer attributes, visibility, identifier, colon, and type. There is a special full-feature branch for unnamed field placeholders written with `_` and nested `struct` or `union` field syntax; it captures those tokens as `Type::Verbatim`.

Printing emits variant attrs, identifier, fields, and optional discriminant. Named and unnamed fields surround the punctuated field list with the original delimiter token. `Field::to_tokens` prints attrs, visibility, optional name plus colon, and type.

## State and Persistence

The AST is immutable unless callers mutate the public fields directly or use `iter_mut`. No persistent storage, global state, or caches are used. Iteration state is limited to `Members { fields, index }`; cloning a `Members` iterator copies the current iterator and index, so repeated quote expansions can traverse from the same point.

## Dependencies and Integration Points

This module depends on `Attribute`, `Expr`, `Member`, `Index`, `Ident`, `Punctuated`, `Visibility`, `FieldMutability`, `Type`, token types, and `verbatim`. It feeds `derive.rs` for `DataStruct`, `DataEnum`, and `DataUnion`, and feeds expression code generation via `Fields::members`. It integrates with `Parse`, `ToTokens`, `Spanned` for unnamed-field index spans, and `scan_expr` in non-full parsing mode.

## Risks and Edge Cases

Variant parsing accepts and discards visibility even though Rust enum variants do not use visibility in stable syntax; this likely exists to recover or maintain grammar compatibility and could hide invalid input until later stages. Non-full discriminant parsing depends on speculative parsing and token scanning, so unsupported expression forms become verbatim rather than structured AST. `Members` uses a `u32` index; pathological field counts above `u32::MAX` are not realistic but align with `Index`. Shorthand/named-field printing depends on `colon_token` consistency.

## Test Signals

No inline unit tests appear in this file. Test coverage should include named, tuple, and unit fields; variant discriminants under full and non-full feature sets; `Fields::members` for named and unnamed fields; field attribute and visibility round-tripping; and the `_` unnamed-field/nested-struct verbatim branch.
