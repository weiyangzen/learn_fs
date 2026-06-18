# sources/distributed-fs/ceph-client/rust/syn/fixup.rs

## Purpose

This file implements the context model used while printing expressions so that the emitted tokens parse back to the same expression tree. It handles precedence, statement and match-arm early termination, condition struct-literal ambiguity, jump-expression operands, range behavior, and generic-angle ambiguity after casts.

## Important APIs, Types, and Functions

- `FixupContext`: copyable context passed through expression printing.
- `FixupContext::NONE`: default minimal-fixup context.
- `new_stmt`, `new_match_arm`, `new_condition`: initial contexts for statement, match-arm, and condition/scrutinee positions.
- `leftmost_subexpression_with_operator`: derives context and effective precedence for a left operand followed by an operator.
- `leftmost_subexpression_with_dot`: derives context for receivers followed by `.` or `?`.
- `rightmost_subexpression` and `rightmost_subexpression_fixup`: derive context for right operands.
- `parenthesize`: decides whether an expression needs parentheses due to statement, match-arm, or condition boundary hazards.
- `precedence`: computes context-adjusted precedence, not just intrinsic `Precedence::of`.
- `scan_left` and `scan_right`: recursive scanning helpers used to determine whether a subexpression would be consumed, fail, or require bailout in the surrounding context.
- `Scan`: internal enum with `Fail`, `Bailout`, and `Consume`.

## Control Flow

Printing code calls a `FixupContext` method before printing each subexpression. For left operands, the context records the next operator and whether that operator can begin an expression or generic arguments, then computes effective precedence. For right operands, it records the previous operator, condition reset behavior, optional operand status, and rightmost context before computing precedence.

`parenthesize` handles grammar hazards that are not expressible as simple operator precedence: braced expressions at statement heads, `let` expressions in statement-like positions, braced macro calls in match arms, struct literals in conditions, value-less return/yield/break in condition rightmost positions, and optional operands beginning with plain blocks.

`scan_right` recursively walks expression shapes that can absorb following operators or operands: assignment, binary, unary/reference/raw address, ranges, break/return/yield, closures, and let expressions. It returns whether the expression consumes the next context, bails out into needing normal precedence handling, or fails and needs parentheses. `scan_left` checks whether the left side can accept the previous operator.

## State and Persistence

`FixupContext` is immutable-by-convention and `Copy`; each transformation returns a new context. There is no persistence or global state. Most fields are compiled only under `full`; `next_operator_can_begin_generics` remains relevant outside the full-only block.

## Dependencies and Integration Points

The module depends on `classify`, `Expr` and specific expression structs, `Precedence`, and `ReturnType`. It is consumed by `expr.rs` printing functions for assignments, binary operations, calls, casts, closures, conditions, match arms, ranges, references, jumps, and other nested expressions.

## Risks and Edge Cases

This is a correctness-sensitive printer component. Missing a context flag can emit code that parses differently, especially around `match {}` or `if {}` at statement heads, braced macros, `let` expressions, value-less jumps, range endpoints, closure bodies, and casts before generic-looking operators. The recursive scan logic is complex and depends on `Precedence` ordering; changes in Rust grammar or Syn's precedence table require coordinated updates here and in `expr.rs`.

## Test Signals

No inline tests appear here. High-value tests are expression round-trips that compare AST shape after printing and reparsing, especially for statement heads, match arms, conditions, ranges, jumps, closures, casts followed by `<`, and nested binary/unary combinations. Snapshot tests of printed tokens for ambiguous expressions would catch regressions.
