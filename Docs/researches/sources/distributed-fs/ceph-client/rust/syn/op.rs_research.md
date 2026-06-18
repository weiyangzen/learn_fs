# Research: sources/distributed-fs/ceph-client/rust/syn/op.rs

## Purpose
`op.rs` defines AST enums for Rust binary and unary operators and supplies parser and printer implementations. These enums are used by expression nodes and traversal/printing code.

## Important APIs, Types, And Functions
`BinOp` is a non-exhaustive enum covering arithmetic, logical, bitwise, comparison, shift, and assignment operators: `+`, `-`, `*`, `/`, `%`, `&&`, `||`, `^`, `&`, `|`, `<<`, `>>`, `==`, `<`, `<=`, `!=`, `>=`, `>`, and the compound assignment forms. `UnOp` covers dereference `*`, logical not `!`, and negation `-`. Each variant stores the exact token type, preserving span and spelling for diagnostics and printing.

## Control Flow
`Parse for BinOp` checks longest and most specific tokens first, especially assignment and multi-character operators, before falling back to single-character operators. This avoids consuming `+=` as `+` or `<<=` as `<<`. `Parse for UnOp` uses `lookahead1` to collect useful errors across `*`, `!`, and `-`. Printing is a direct match that delegates to each stored token's `ToTokens` implementation.

## State And Persistence Behavior
No persistent state exists. Operator values hold only token spans through their token fields. The enums are non-exhaustive, so downstream matching must retain a fallback for future Rust operators.

## Dependencies And Integration Points
The module depends on Syn token definitions, parser traits, lookahead diagnostics, and `quote::ToTokens`. It is consumed by expression parsing/printing, precedence handling, visitors/folders, and extra trait generation.

## Risks
Ordering in `BinOp::parse` is critical. Reordering multi-character operators after prefixes would create incorrect token consumption. Because assignment operators are represented in `BinOp`, downstream consumers must distinguish arithmetic/logical binary operations from assignment-like operations when semantics matter. Non-exhaustiveness requires careful downstream matches.

## Test Signals
Tests should parse and print every operator, verify longest-match behavior for `>>=`, `<<=`, `>=`, `<=`, `==`, `!=`, `&&`, `||`, and assignment operators, confirm invalid input diagnostics, and run expression parser tests that validate precedence integration outside this file.
