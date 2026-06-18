# sources/distributed-fs/ceph-client/rust/macros/fmt.rs

## Purpose
`fmt.rs` implements a formatting helper used by kernel logging macros. It wraps every formatting argument in `::kernel::fmt::Adapter` so kernel-specific formatting behavior is applied while preserving `core::format_args!` syntax.

## Important APIs, Types, And Functions
The public crate-internal entry is `fmt(input: TokenStream) -> TokenStream`. It scans the first literal format string for named placeholders, stores names in a `BTreeSet`, rewrites explicit positional or named arguments through `Adapter(&(expr))`, and appends implicit named arguments that appeared only in the format string.

## Control Flow
If the first token is not a string literal, the macro returns the input unchanged. Otherwise it parses `{name}` patterns while skipping escaped `{{`, ignoring numeric positional placeholders, and stripping format specifiers after `:`. It then walks remaining tokens, splitting on commas, and for each argument separates an optional `lhs =` from the expression so named arguments remain named. At the end it emits `::core::format_args!(...)`.

## State And Persistence
All state is transient: a set of inferred placeholder names plus token-stream accumulators. There is no runtime storage.

## Dependencies And Integration Points
It depends on `proc_macro2`, `quote_spanned`, and the kernel `fmt::Adapter`. `macros/lib.rs` exposes it as `fmt!`, and higher-level logging macros use it to adapt arguments before printing.

## Risks And Edge Cases
The format-string scanner is intentionally lightweight and does not implement the full Rust format grammar. It can miss or misinterpret unusual formatting constructs, although actual `format_args!` still performs final validation. Argument splitting on top-level comma tokens relies on the token stream structure and preserves `a = b = c` by splitting only the first equals sign. Span selection uses the format literal span for generated adapter references.

## Test Signals
Tests should cover positional arguments, explicit named arguments, implicit captured names, escaped braces, format specifiers, assignments inside expressions, non-literal first tokens, and ensuring all generated values are wrapped exactly once in `Adapter`.
