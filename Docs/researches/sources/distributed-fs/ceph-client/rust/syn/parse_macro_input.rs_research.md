# sources/distributed-fs/ceph-client/rust/syn/parse_macro_input.rs

## Purpose
`parse_macro_input.rs` defines the exported `parse_macro_input!` procedural macro helper. It converts a proc-macro input token stream into a typed Syn AST value and turns parse errors into compiler diagnostics.

## Important APIs, types, and functions
The only API is `parse_macro_input!` with three forms: `($tokenstream as $ty)`, `($tokenstream with $parser)`, and `($tokenstream)`. The first uses `$crate::parse::<$ty>`, the second uses `Parser::parse`, and the third infers the target type through `as _`.

## Control flow
The macro expands to a `match` on the parse result. `Ok(data)` yields the parsed syntax tree. `Err(err)` immediately returns `proc_macro::TokenStream::from(err.to_compile_error())` from the caller, which is why the macro is intended for proc-macro entry points returning `proc_macro::TokenStream`.

## State and persistence behavior
There is no persistent state. The macro consumes the caller's token stream expression and either yields a parsed value or returns generated error tokens.

## Dependencies and integration points
It integrates with the `parse` module, `Parser`, `Error::to_compile_error`, and `$crate::__private` reexports for stable macro expansion hygiene. It is a public ergonomic entry point used by procedural macro authors.

## Risks
The macro shape requires an identifier token stream variable, not an arbitrary expression. Error handling performs an early `return`, so use outside the expected return type context fails. It is gated for `parsing` plus `proc-macro`.

## Test signals
Tests should cover `as` and `with` forms, inferred type use, parse failures producing compile-error token streams, and expansion inside functions returning `proc_macro::TokenStream`.
