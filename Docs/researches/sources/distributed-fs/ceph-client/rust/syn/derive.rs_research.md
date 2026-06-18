# sources/distributed-fs/ceph-client/rust/syn/derive.rs

## Purpose

This file defines the top-level AST for input to `proc_macro_derive`: `DeriveInput` plus `Data` variants for struct, enum, and union declarations. It parses and prints the declaration shell around the field and variant models supplied by `data.rs`.

## Important APIs, Types, and Functions

- `DeriveInput`: outer attributes, visibility, identifier, generics, and `Data`.
- `Data`: enum of `Struct(DataStruct)`, `Enum(DataEnum)`, and `Union(DataUnion)`.
- `DataStruct`: `struct_token`, `fields`, and optional semicolon.
- `DataEnum`: `enum_token`, brace token, and `Punctuated<Variant, Comma>`.
- `DataUnion`: `union_token` and named fields.
- `parsing::data_struct`: parses where-clause placement, named/unnamed/unit fields, and semicolon requirements.
- `parsing::data_enum`: parses optional where clause then braced variants.
- `parsing::data_union`: parses optional where clause then named fields.
- `printing::ToTokens for DeriveInput`: reconstructs declaration tokens with correct where-clause placement.

## Control Flow

`DeriveInput::parse` consumes outer attributes and visibility, then uses a lookahead to choose `struct`, `enum`, or `union`. For all three forms it parses the identifier and generics before delegating to a shape-specific helper. The helper returns any where clause that syntactically appears after generics or fields, and the parser rebuilds `Generics { where_clause, ..generics }`.

`data_struct` handles Rust's different struct layouts. It allows an early where clause before fields, parses tuple fields followed by an optional where clause and required semicolon, parses named fields without a semicolon, or parses unit structs with a semicolon. `data_enum` and `data_union` parse a where clause in the standard position before braces.

Printing emits outer attrs, visibility, the selected kind token, identifier, generics, then fields/variants. The where clause is printed before named struct braces, after tuple fields but before their semicolon, before a unit struct semicolon, and before enum/union bodies.

## State and Persistence

The module only builds AST values from parse streams and tokenizes them back out. It maintains no persistent state. The only transient state is local lookahead and returned helper tuples.

## Dependencies and Integration Points

It depends on `Attribute`, `Fields`, `FieldsNamed`, `Variant`, `Generics`, `WhereClause`, `Ident`, `Punctuated`, `Visibility`, and token definitions. It is the central input type for derive macros and integrates with `parse_macro_input!`, `quote::ToTokens`, and downstream code that matches on `Data`.

## Risks and Edge Cases

Where-clause placement is subtle: tuple structs may place a where clause after tuple fields, while named and unit structs print it elsewhere. A parser or printer change can easily alter round-trip formatting or validity. `Data` is not marked non-exhaustive in this file, so downstream matching depends on the current three shapes. The parser rejects malformed struct layouts via `lookahead.error`, so error quality depends on lookahead setup.

## Test Signals

No inline unit tests appear here. Useful tests include derive input round-trips for named, tuple, and unit structs; tuple structs with where clauses after fields; enums with discriminants and attributes; unions; and invalid declarations that should produce useful lookahead errors.
