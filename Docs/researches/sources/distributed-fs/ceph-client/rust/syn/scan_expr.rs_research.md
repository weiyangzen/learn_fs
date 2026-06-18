# sources/distributed-fs/ceph-client/rust/syn/scan_expr.rs

## Purpose
`scan_expr.rs` implements a table-driven expression scanner that consumes tokens until an expression boundary is found. It is used where Syn needs to recognize an expression-shaped token span without constructing or owning a complete expression node at each step.

## Important APIs, types, and functions
Internal enums are `Input` and `Action`. Static rule tables include `INIT`, `POSTFIX`, `ASYNC`, `BLOCK`, `BREAK_LABEL`, `BREAK_VALUE`, `CLOSURE`, `CLOSURE_ARGS`, `CLOSURE_RET`, `CONST`, `CONTINUE`, `DOT`, `FOR`, `IF_ELSE`, `IF_THEN`, `METHOD`, `PATH`, `PATTERN`, `RANGE`, `RAW`, `REFERENCE`, and `RETURN`. The public crate-level function is `scan_expr(input: ParseStream) -> Result<()>`.

## Control flow
`scan_expr` loops over the current state table and tests each `Input` against the parse stream. Matching rules consume tokens by keyword, punctuator sequence, delimiter, ident, lifetime, literal, binary op, path, turbofish, type, or expression-start predicate. Actions transition state, increment/decrement nested expression depth, or finish when depth is zero.

## State and persistence behavior
State is transient: the active rule table and a `usize` depth counter. There is no persistence.

## Dependencies and integration points
It depends on `proc_macro2` token primitives and Syn parsing of `AngleBracketedGenericArguments`, `BinOp`, `Expr`, `ExprPath`, `Lifetime`, `Lit`, and `Type`. It integrates with expression parsing boundaries.

## Risks
The finite-state scanner must track a large Rust expression grammar surface. Ambiguities around closures, async blocks, `if`/`else`, range operators, `let` patterns, turbofish, and method calls are high risk. `DecDepth` assumes depth is nonzero in matched states.

## Test signals
Tests should cover nested `if`/`else`, loops, closures with typed returns, async/const/unsafe blocks, method turbofish, ranges, `let` patterns, break/continue labels, return/yield payloads, and unsupported-expression diagnostics.
