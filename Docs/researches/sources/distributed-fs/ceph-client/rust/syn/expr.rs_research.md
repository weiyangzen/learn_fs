# sources/distributed-fs/ceph-client/rust/syn/expr.rs

## Purpose

This file defines Syn's expression AST, expression-related helper types, expression parsing, and expression printing. It is one of the central Rust grammar modules: it models all expression variants available under `full` plus a smaller derive-compatible subset, handles context-sensitive parsing such as struct-literal ambiguity, and prints expressions with precedence and boundary fixups.

## Important APIs, Types, and Functions

- `Expr`: non-exhaustive syntax enum for Rust expressions. Variants include arrays, assignment, async/await, binary, block, break/continue/return/yield, calls, casts, closures, field/index access, loops, groups, if/let/match/ranges, references/raw addresses, repeat arrays, structs, try, tuples, unary, unsafe, while, and `Verbatim`.
- Per-variant structs: `ExprArray`, `ExprAssign`, `ExprAsync`, `ExprAwait`, `ExprBinary`, `ExprBlock`, `ExprBreak`, `ExprCall`, `ExprCast`, `ExprClosure`, `ExprConst`, `ExprContinue`, `ExprField`, `ExprForLoop`, `ExprGroup`, `ExprIf`, `ExprIndex`, `ExprInfer`, `ExprLet`, `ExprLit`, `ExprLoop`, `ExprMacro`, `ExprMatch`, `ExprMethodCall`, `ExprParen`, `ExprPath`, `ExprRange`, `ExprRawAddr`, `ExprReference`, `ExprRepeat`, `ExprReturn`, `ExprStruct`, `ExprTry`, `ExprTryBlock`, `ExprTuple`, `ExprUnary`, `ExprUnsafe`, `ExprWhile`, `ExprYield`.
- `Expr::PLACEHOLDER`: invalid empty path expression used as a temporary value for AST surgery.
- `Expr::parse_without_eager_brace`: context parser for conditions and match scrutinees where trailing braces must not become struct literals.
- `Expr::parse_with_earlier_boundary_rule`: context parser for statement heads and match arm bodies where expression boundaries are placed earlier than normal.
- `Expr::peek`: classifies whether the next token can begin an expression.
- `Expr::replace_attrs`: swaps expression attributes across all structured variants.
- `Member`, `Index`, `FieldValue`, `Label`, `Arm`, `RangeLimits`, `PointerMutability`: supporting expression types.
- Parsing core: `ambiguous_expr`, `parse_expr`, `parse_binop_rhs`, `peek_precedence`, `unary_expr`, `trailer_expr`, `trailer_helper`, `atom_expr`.
- Printing core: `print_expr`, `print_subexpression`, and per-variant `ToTokens` implementations that use `FixupContext`.

## Control Flow

The general parser is Pratt-style. `ambiguous_expr` parses a unary/trailer/atom expression as the left-hand side, then `parse_expr` loops over binary operators, assignment, ranges, and casts according to `Precedence`. `parse_binop_rhs` recursively consumes tighter or right-associative operators. Comparisons are explicitly rejected when chained.

Atom parsing chooses from literals, async/try blocks, closures, built-in verbatim syntax, paths/macros/struct literals, parentheses/tuples, jump expressions, arrays/repeats, let expressions, control-flow expressions, ranges, inference, and labeled loops/blocks. Trailer parsing repeatedly adds calls, field access, method calls with optional turbofish, indexing, await, and try `?`. The `multi_index` helper handles tokens like `.0.1` that may initially arrive as float literals and splits them into chained tuple-field indexes with subspans.

Context-sensitive parsing is explicit. `AllowStruct(false)` prevents eager struct literals in conditions and similar positions. `parse_with_earlier_boundary_rule` stops after expressions that terminate statements or match arms, except for trailers that should still bind. Non-full builds keep a subset parser for derive-compatible expressions and can preserve some unsupported block expressions as `Expr::Verbatim`.

Control-flow-specific parsers handle nested `else if` by temporarily storing `Expr::PLACEHOLDER`, then rebuilding the chain from the inside out. Loop, while, for, match, const, unsafe, and block parsers collect inner attributes and parse `Block::parse_within`. Closure parsing supports lifetimes, `const`, `static`, `async`, `move`, typed or untyped pattern arguments, optional return type, and either block or expression bodies.

Printing dispatches through `print_expr` and per-variant helpers. Expressions that can change parse meaning receive `FixupContext` from `fixup.rs`; helpers request leftmost/rightmost subexpression precedence and insert parentheses when needed. Statement and match-arm bodies use specialized fixup contexts. Printers also maintain syntactic necessities such as tuple trailing commas, match-arm commas for non-block arms, `else` wrapping for invalid else expressions, and shorthand struct fields with absent colon tokens.

## State and Persistence

All AST state is in public struct fields: attributes, tokens, boxed subexpressions, punctuated lists, blocks, paths, labels, and spans. Parsing uses transient forks, lookahead, and local vectors, but no persistent store. `Expr::replace_attrs` mutates an expression's attribute vector and returns the old one. `Expr::PLACEHOLDER` is a sentinel for temporary replacement and should not be treated as meaningful user syntax.

## Dependencies and Integration Points

This module integrates nearly every core Syn subsystem: attributes, errors, identifier extensions, generics, lifetimes, literals, macros, operators, parser streams, patterns, paths and qualified self types, punctuated lists, statements/blocks, tokens, types, precedence classification, verbatim capture, and quote printing. It depends on `FixupContext` for printing correctness and on `classify` for statement/match-arm boundary decisions. Downstream users rely on `Expr` as the main expression tree for parsing, analysis, rewriting, and code generation.

## Risks and Edge Cases

Expression grammar is highly context-sensitive. Risks include accidentally allowing struct literals in condition positions, misplacing expression boundaries in match arms or statement heads, changing operator associativity, or producing token streams that parse back differently. `Expr::PLACEHOLDER` must not escape temporary rewrite paths. `Index::from` asserts `usize < u32::MAX`, and `Index::parse` rejects suffixed integers. `multi_index` depends on proc-macro2 subspan support and falls back to the float span when unavailable. Casts reject immediate trailers because Rust requires parentheses before calls, fields, indexing, `?`, or await after a cast. Feature-gated parsing and printing paths must stay consistent across `full`, `derive`, `parsing`, and `printing`.

## Test Signals

Inline executable tests are limited to documentation examples such as `Expr::PLACEHOLDER`; this file itself has no `#[test]` module. Strong coverage should include round-trip parse/print suites across every `Expr` variant, precedence and associativity cases, chained comparison rejection, condition vs expression struct-literal ambiguity, earlier-boundary statement and match-arm cases, closure forms, `else if` reconstruction, tuple field multi-index spans, cast trailer errors, feature-reduced parsing, and match-arm comma insertion.
