# sources/distributed-fs/ceph-client/rust/syn/stmt.rs

## Purpose
`stmt.rs` defines block and statement AST nodes plus parsing/printing for Rust statement sequences under the `full` feature.

## Important APIs, types, and functions
Main types are `Block`, `Stmt`, `Local`, `LocalInit`, and `StmtMacro`. Parser entry points include `Block::parse_within`, `Parse for Block`, `Parse for Stmt`, and helpers `parse_stmt`, `stmt_mac`, `stmt_local`, and `stmt_expr`.

## Control flow
`Block::parse_within` consumes empty semicolon statements, repeatedly parses statements, and enforces required semicolons before continuing. `parse_stmt` gathers outer attributes, detects brace-style macros, classifies `let`, item starts, or expression statements. `stmt_local` parses pattern, optional type ascription, initializer, optional `else` block for let-else, and semicolon. `stmt_expr` parses an expression, moves outer attributes onto the leftmost relevant expression target, handles macro statements, and enforces semicolon rules.

## State and persistence behavior
State is local parser state only. Blocks store statements in `Vec<Stmt>`, and statement nodes preserve attributes, token spans, and optional semicolon tokens.

## Dependencies and integration points
It depends on attributes, expression parsing/classification, item parsing, macros, patterns, paths, tokens, types, and `Speculative`. Printing integrates with expression printing and `FixupContext`.

## Risks
Statement classification is highly ambiguous: macro invocations, item starts, `const` blocks versus const items, `async` closures versus async items, and expression statements with trailing braces all require precise lookahead. Attribute reassignment to expression targets is subtle. Semicolon enforcement relies on `classify`.

## Test signals
Tests should cover empty statements, trailing expression blocks, required semicolon failures, let-else, typed locals, macro statements with each delimiter, item macro ambiguity, async/const/unsafe classification, and printing round trips.
