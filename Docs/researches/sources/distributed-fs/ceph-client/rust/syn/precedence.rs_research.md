# sources/distributed-fs/ceph-client/rust/syn/precedence.rs

## Purpose
`precedence.rs` centralizes Rust expression precedence for Syn's expression printer so emitted token streams preserve semantics with minimal parentheses.

## Important APIs, types, and functions
The main type is `Precedence` with ordered variants from `Jump` through `Unambiguous`. `Precedence::MIN` defines the lowest level. `Precedence::of_binop` maps `BinOp` to precedence. Under `printing`, `Precedence::of(&Expr)` classifies full expression nodes and uses helper `prefix_attrs` for outer-attribute-sensitive cases.

## Control flow
Binary operators map directly to precedence classes. `of(&Expr)` matches expression variants, treating assignment, range, binary, let, cast, reference/raw address/unary, jump expressions, closures, and unambiguous expression forms separately. For many full expression forms, outer attributes downgrade printing precedence to `Prefix`.

## State and persistence behavior
No state or persistence. Values are copyable enum discriminants used during printing.

## Dependencies and integration points
It depends on `crate::op::BinOp`, `crate::expr::Expr`, selected full expression structs, `Attribute`, `AttrStyle`, and `ReturnType`. Expression printing modules use the ordering via `PartialOrd`.

## Risks
Any mismatch with the Rust Reference precedence table can change printed semantics. Feature gating means non-`full` builds mark some variants unreachable. Attribute-sensitive precedence is easy to regress because an outer attribute can require parentheses where the expression kind alone would not.

## Test signals
Tests should compare printed output for nested binary/cast/range/assignment expressions, closures with and without return types, outer attributes on expressions, jump expressions with optional payloads, and non-`full` feature builds.
