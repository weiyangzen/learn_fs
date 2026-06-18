# Research: subset-b-006314

Grouped research report for Syn source files under `sources/distributed-fs/ceph-client/rust/syn`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/custom_punctuation.rs -->
# sources/distributed-fs/ceph-client/rust/syn/custom_punctuation.rs

## Purpose

This file defines the public `syn::custom_punctuation!` macro and its private helper macros. It lets macro authors declare a Rust type that represents a multi-character punctuation sequence, such as `<=>` or `</>`, while integrating with Syn's standard parse, peek, print, span, clone, debug, equality, and hash conventions.

## Important APIs, Types, and Functions

- `custom_punctuation!($ident, $($tt)+)`: exported macro that generates a public struct with `pub spans`, a constructor-like function named after the type, and feature-gated trait impls.
- `impl_parse_for_custom_punctuation!`: with `parsing`, implements `CustomToken` and `Parse`. `peek` uses `__private::peek_punct`, `display` formats the punctuation for diagnostics, and parsing delegates to `__private::parse_punct`.
- `impl_to_tokens_for_custom_punctuation!`: with `printing`, implements `quote::ToTokens` through `__private::print_punct`.
- `impl_clone_for_custom_punctuation!`: with `clone-impls`, makes the punctuation token `Copy` and `Clone`.
- `impl_extra_traits_for_custom_punctuation!`: with `extra-traits`, implements `Debug`, `Eq`, `PartialEq`, and `Hash`; equality ignores spans, matching built-in token behavior.
- `custom_punctuation_repr!`: computes the span storage type as `[Span; N]`.
- `custom_punctuation_len!`: maps valid punctuation token fragments to span counts and rejects invalid fragments in strict mode.
- `stringify_punct!`: concatenates stringified punctuation pieces for parser/printer helpers.

## Control Flow

The primary macro emits a token struct and a same-named constructor function. The constructor accepts any `IntoSpans<[Span; N]>`, validates all punctuation fragments with `custom_punctuation_len!(strict, ...)`, and converts the caller's span input into the generated `spans` field. Inside a private constant block, feature-gated helper macros expand to trait impls or to empty expansions depending on enabled Syn features.

Parsing flow is: parser calls `input.peek(GeneratedToken)` or `input.parse::<GeneratedToken>()`; the generated `CustomToken` reports the target punctuation string; `parse_punct` consumes the exact punctuation and returns the span array; the generated constructor wraps those spans. Printing flow is the inverse: `ToTokens::to_tokens` passes the punctuation string and span array into `print_punct`.

## State and Persistence

Generated punctuation values are pure syntax nodes. Their only state is the span array. There is no heap persistence, I/O, global mutation, or caching. Trait behavior intentionally treats spans as metadata: `PartialEq` always returns true for two values of the same punctuation type, and `Hash` contributes no span data.

## Dependencies and Integration Points

The macro depends on reexports from `crate::__private` in `export.rs`, including `Span`, `IntoSpans`, `CustomToken`, `ToTokens`, and punctuation parse/print functions. It integrates with `crate::parse::Parse`, `crate::buffer::Cursor`, `quote::ToTokens`, and Syn's feature flags (`parsing`, `printing`, `clone-impls`, `extra-traits`). The generated APIs are intended to behave like built-in token types from `token.rs`, so they can be used in `Punctuated`, parser lookahead, and `quote!` interpolation.

## Risks and Edge Cases

The punctuation grammar is limited to the fragments enumerated in `custom_punctuation_len!`; unsupported fragments fail through the strict branch. The lenient branch returns zero for unknown fragments when computing representation type, but the constructor's strict validation prevents accepting invalid definitions. Multi-character punctuation span arrays must stay aligned with parser/printer assumptions. Feature-gated empty helper expansions mean generated types compile in reduced feature builds but lose parse/print/clone/extra-trait capabilities.

## Test Signals

There are no inline unit tests in this file. The documentation example exercises custom punctuation inside a `Punctuated<Expr, PathSeparator>` parser. Strong test signals would include compile-pass tests for valid punctuation definitions, compile-fail tests for invalid fragments, round-trip parse/quote tests preserving span counts, and feature-matrix tests for the empty helper expansions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/custom_punctuation.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/data.rs -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/data.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/derive.rs -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/derive.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/discouraged.rs -->
# sources/distributed-fs/ceph-client/rust/syn/discouraged.rs

## Purpose

This file exposes niche parsing extensions that are intentionally separated from the main parsing API: speculative parsing commit support and delimiter-agnostic group parsing. The module documentation and trait names signal that these tools are powerful but can degrade diagnostics when overused.

## Important APIs, Types, and Functions

- `Speculative`: extension trait with `advance_to(&self, fork: &Self)` for committing a forked `ParseStream` back into the original stream.
- `impl Speculative for ParseBuffer`: validates fork ancestry/scope, propagates unexpected-token diagnostic state, and updates the main cursor.
- `AnyDelimiter`: extension trait with `parse_any_delimiter` returning `(Delimiter, DelimSpan, ParseBuffer)`.
- `impl AnyDelimiter for ParseBuffer`: uses `Cursor::any_group` to parse parentheses, brackets, braces, or invisible delimiters uniformly.

## Control Flow

`advance_to` first checks that `self.cursor()` and `fork.cursor()` are in the same scope. If not, it panics because the fork did not originate from the advancing stream. It then compares the shared unexpected-token cells of the two streams. If the fork has an unexpected token and the original does not, it copies that unexpected value to the original. If both are unset, it chains the fork's unexpected cell to the original and replaces the fork's root unexpected pointer to avoid leaking top-level fork errors. Finally, it writes the fork cursor into the original parse buffer cell using a transmute to the buffer's internal static cursor representation.

`parse_any_delimiter` runs a parser step. If the cursor points at any token group, it computes the group close span, advances a nested cursor into the content, shares the current unexpected state, creates a nested `ParseBuffer`, and returns the delimiter metadata plus rest cursor. If no group is present, it returns a cursor error.

## State and Persistence

The key state is parse-buffer cursor position and shared diagnostic state held in `Rc<Cell<Unexpected>>`. `advance_to` mutates the original parse buffer cursor and may relink unexpected-token state. There is no persistent storage. The unsafe transmute is local but relies on ParseBuffer's invariant that the cursor cell owns a lifetime-erased cursor.

## Dependencies and Integration Points

The module depends on `buffer::Cursor`, `ParseBuffer`, `inner_unexpected`, `Unexpected`, `proc_macro2::Delimiter`, `proc_macro2::extra::DelimSpan`, `Rc`, `Cell`, and low-level parse constructors (`advance_step_cursor`, `get_unexpected`, `new_parse_buffer`). It is used by parsers that need fork/try/commit behavior, including expression and data parsing branches elsewhere in Syn.

## Risks and Edge Cases

The main risk is diagnostic quality: a failed speculative branch may cause the parser to report fallback errors rather than the branch that consumed more meaningful input. `advance_to` panics if the fork is unrelated or from a different scope. The unsafe cursor lifetime erasure must remain aligned with `ParseBuffer` internals. Incorrect unexpected-state propagation could produce confusing or stale errors.

## Test Signals

No inline unit tests appear here. The doc example demonstrates speculative turbofish parsing. Useful tests should cover successful fork commits, invalid fork panic behavior, preservation of unexpected-token diagnostics through nested groups, and `parse_any_delimiter` for all delimiter kinds including invisible groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/discouraged.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/drops.rs -->
# sources/distributed-fs/ceph-client/rust/syn/drops.rs

## Purpose

This file defines a small internal utility for wrapping values whose destructor can safely be skipped. It is used to avoid running drop glue for iterator types known to have trivial drop behavior, while documenting the invariant through a marker trait.

## Important APIs, Types, and Functions

- `NoDrop<T: ?Sized>`: transparent wrapper around `ManuallyDrop<T>`.
- `NoDrop::new(value)`: constructs a wrapper only when `T: TrivialDrop`.
- `Deref` and `DerefMut` impls: expose references to the wrapped value.
- `TrivialDrop`: internal marker trait for types that do not need destructor execution.
- Handwritten `TrivialDrop` impls for `iter::Empty<T>`, slice iterators, and option iterators over references.
- `test_needs_drop`: unit test verifying the marker impls correspond to `std::mem::needs_drop == false` even when the item type has a destructor.

## Control Flow

Construction wraps the value in `ManuallyDrop`. Because `NoDrop` has no custom destructor and `ManuallyDrop` suppresses dropping the inner value, dropping `NoDrop<T>` does not drop `T`. The type bound on `new` is the guardrail: only types with explicit `TrivialDrop` impls can be wrapped through the safe constructor.

## State and Persistence

State is limited to the wrapped value. No heap storage, global state, or persistence is present. The behavior directly affects destructor execution, so its state semantics are about what does not happen when the wrapper is dropped.

## Dependencies and Integration Points

The module uses `std::mem::ManuallyDrop`, iterator types from `std::iter`, `std::slice`, `std::option`, and deref traits. It is likely consumed by AST iteration utilities that need erased or empty iterators without unnecessary drop bounds or overhead.

## Risks and Edge Cases

The safety model depends on `TrivialDrop` impls being correct. Adding a `TrivialDrop` impl for a type that owns resources would leak or skip required cleanup. The current impls are for iterator/reference wrappers that should remain destructor-free. The wrapper is safe Rust, but misuse through expanding marker impls would create semantic leaks.

## Test Signals

This file has an inline unit test, `test_needs_drop`, that defines a `NeedsDrop` type and asserts all marked iterator types do not need drop even when parameterized with it. Future marker impls should add corresponding assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/drops.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/error.rs -->
# sources/distributed-fs/ceph-client/rust/syn/error.rs

## Purpose

This file implements Syn's parser error type. It supports single or combined diagnostic messages, span-aware conversion to `compile_error!` token streams for procedural macros, `Display`/`Debug`/`std::error::Error`, cloning, iteration over combined errors, and conversion from `proc_macro2::LexError`.

## Important APIs, Types, and Functions

- `pub type Result<T> = std::result::Result<T, Error>`: common parser result alias.
- `Error`: owns `Vec<ErrorMessage>`.
- `ErrorMessage`: thread-bound span range plus message string.
- `SpanRange`: start/end spans used to compute joined diagnostic span.
- `Error::new(span, message)`: constructs a one-message error at one span.
- `Error::new_spanned(tokens, message)`: with `printing`, spans from first to last token of a syntax node.
- `Error::span`: returns joined span, or `Span::call_site()` if accessed from another thread.
- `Error::to_compile_error` and `into_compile_error`: render one or more `::core::compile_error! { "message" }` invocations.
- `Error::combine` and `Extend<Error>`: aggregate diagnostics.
- `new_at` and `new2`: crate-internal helpers for parse cursor errors and start/end span ranges.
- `IntoIterator for Error` and `&Error`: split or clone combined messages into one-message `Error` values.

## Control Flow

`Error::new` and `new2` wrap a `SpanRange` in `ThreadBound` and store the message. `new_spanned` converts a tokenizable node into a token stream, uses the first token as start and last token as end, and falls back to call-site for empty streams. `span` retrieves the thread-local span range and joins start/end if possible.

Compile-error rendering maps each message through `ErrorMessage::to_compile_error`. That function manually constructs a token stream equivalent to `::core::compile_error! { "message" }`, setting spans on punctuation, identifiers, the bang, group, and string literal to point at the stored start/end range. Combined errors render as multiple compile-error invocations collected into one stream.

## State and Persistence

Error state is an in-memory vector of messages. Span data is wrapped in `ThreadBound` so the `Error` type can be `Send + Sync`; if an error is examined from a different thread, span access degrades to call-site. There is no persistence, I/O, or global mutation.

## Dependencies and Integration Points

The module depends on `proc_macro2` token primitives, `quote::ToTokens` for `new_spanned`, Syn's `buffer::Cursor` for parsing helpers, and `thread::ThreadBound` for thread-safe span handling. It is central to `Parse`, `parse_macro_input!`, lookahead errors, and downstream macro expansion error reporting.

## Risks and Edge Cases

Cross-thread span fallback can reduce diagnostic precision but preserves `Send + Sync`. `Display` and `span` report only the first message even when errors are combined, while `to_compile_error` preserves all messages. `new_spanned` quality depends on `ToTokens` preserving meaningful first/last spans. Manual token construction for `compile_error!` must stay compatible with `core` path resolution and proc-macro diagnostics.

## Test Signals

The file contains a compile-time `_Test` assertion that `Error: Send + Sync`. There are no runtime unit tests here. Useful tests include combined-error iteration, `to_compile_error` output shape, `new_spanned` on empty and multi-token nodes, `LexError` conversion, and cross-thread span fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/export.rs -->
# sources/distributed-fs/ceph-client/rust/syn/export.rs

## Purpose

This file provides a hidden internal reexport surface used by Syn's public macros. By routing macro-generated code through `$crate::__private`, Syn can refer to standard-library traits, proc-macro types, quote traits, parser helpers, and token helpers without relying on the caller's imports or prelude.

## Important APIs, Types, and Functions

- Hidden reexports of `Clone`, `Eq`, `PartialEq`, `Default`, `Debug`, `Hash`, `Hasher`, `Copy`, `Option::{None, Some}`, `Result::{Err, Ok}`, `concat`, and `stringify`.
- `Formatter<'a>` and `FmtResult` aliases for debug impls.
- Primitive aliases `bool` and `str`.
- `quote` reexport and `ToTokens`, `TokenStreamExt` when `printing` is enabled.
- `Span`, `TokenStream2`, and `TokenStream` aliases for `proc_macro2` and `proc_macro` token streams.
- Parsing helpers: `parse_braces`, `parse_brackets`, `parse_parens`, `peek_punct`, `parse_punct`, and `CustomToken`.
- Printing helper: `print_punct`.
- `IntoSpans` reexport for token constructors.
- `parse_quote` reexport when both parsing and printing are enabled.
- `private(pub(crate) ())`: hidden marker type.

## Control Flow

There is no runtime control flow. The file is a compile-time namespace that macros reference after expansion. Feature flags decide which names exist, matching the capabilities of the macro expansions that use them.

## State and Persistence

No state or persistence is present. All items are aliases or reexports.

## Dependencies and Integration Points

This module is tightly integrated with `custom_punctuation!`, `custom_keyword!`, token constructors, quote integration, and parse quote macros. It depends on `proc_macro2`, optionally `proc_macro`, `quote`, `group`, `span`, `parse_quote`, and `token` modules.

## Risks and Edge Cases

Because public macros expand to this hidden API, renaming or removing any reexport can be a breaking change even though the items are `doc(hidden)`. Feature gating must stay synchronized with macro helper expansions; for example, printing macros must not reference `ToTokens` unless the `printing` feature exposes it. Lowercase aliases for primitives intentionally avoid caller shadowing but can surprise readers.

## Test Signals

There are no inline tests. Compile-time macro expansion tests are the strongest signal: custom punctuation/keyword use from downstream crates, with and without relevant feature flags, plus no-std-style import isolation where caller scopes do not import any of these traits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/export.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/expr.rs -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/expr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/ext.rs -->
# sources/distributed-fs/ceph-client/rust/syn/ext.rs

## Purpose

This file defines extension methods for foreign types, currently `proc_macro2::Ident`. It adds Syn-specific identifier parsing and normalization needed by macro DSLs and Rust grammar code.

## Important APIs, Types, and Functions

- `IdentExt`: sealed trait implemented only for `proc_macro2::Ident`.
- `IdentExt::parse_any`: parses any identifier, including Rust keywords.
- `IdentExt::peek_any`: associated `PeekFn` value used as `input.peek(Ident::peek_any)`.
- `IdentExt::unraw`: strips a leading `r#` from raw identifiers while preserving span.
- `impl Peek for private::PeekFn`: connects the peek function to a custom token marker.
- `impl CustomToken for private::IdentAny`: peeks `cursor.ident()` and displays as `identifier`.
- Private sealed module: `Sealed`, `PeekFn`, and `IdentAny`.

## Control Flow

`parse_any` uses `ParseStream::step` and directly asks the cursor for an identifier. Since `cursor.ident()` returns identifiers regardless of keyword status, this bypasses normal keyword exclusion. `peek_any` works through Syn's `Peek`/`CustomToken` infrastructure: lookahead invokes `IdentAny::peek`, which checks whether the cursor has any identifier. `unraw` converts the identifier to a string, strips `r#` if present, and creates a new `Ident` with the same span; otherwise it clones the original.

## State and Persistence

No persistent state exists. `unraw` creates a new identifier only when necessary. `PeekFn` is zero-sized and `Copy`.

## Dependencies and Integration Points

The module depends on `buffer::Cursor`, `error::Result`, `ParseStream`, `Peek`, `lookahead::Sealed`, `CustomToken`, and `proc_macro2::Ident`. It is used by parsers that accept keywords as identifiers, including field parsing and expression/path grammar. It also supports macro authors building DSLs with keyword-like names.

## Risks and Edge Cases

`parse_any` intentionally accepts Rust keywords, so parsers must only use it in positions where keywords are valid as names. `unraw` preserves span but changes textual identity; generated identifiers can become Rust keywords if reused without raw escaping, which is intended for foreign-language interop but must be used knowingly. The trait is sealed, so downstream crates cannot extend this pattern to other identifier-like types.

## Test Signals

No inline tests appear here. Useful tests include parsing ordinary identifiers, Rust keywords, and raw identifiers through `parse_any`; peeking without consuming; and verifying `unraw` output and span preservation for `x`, `move`, and `r#move`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/ext.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/file.rs -->
# sources/distributed-fs/ceph-client/rust/syn/file.rs

## Purpose

This file defines Syn's AST node for a complete Rust source file. It captures an optional shebang string, inner file attributes, and the sequence of top-level items.

## Important APIs, Types, and Functions

- `File`: complete Rust file with `shebang: Option<String>`, `attrs: Vec<Attribute>`, and `items: Vec<Item>`.
- `parsing::impl Parse for File`: parses inner attributes and then parses items until the stream is empty.
- `printing::impl ToTokens for File`: prints inner attributes and items.

## Control Flow

`File::parse` constructs a `File` with `shebang: None`, reads inner attributes with `Attribute::parse_inner`, then loops while the input is not empty and pushes each parsed `Item` into a vector. Shebang handling is not performed here; it is expected to be handled by the higher-level `parse_file` entry point before token parsing. Printing appends inner attributes and then all items.

## State and Persistence

`File` stores only parsed syntax in memory. There is no file I/O despite the type name; callers are responsible for reading source text and invoking `parse_file` or parser APIs. `shebang` is a string field populated outside this `Parse` impl.

## Dependencies and Integration Points

The module depends on `Attribute` and `Item`. It is the root AST for full-file parsing and integrates with `crate::parse_file`, `Parse`, `quote::ToTokens`, and the item parser. Downstream tools use it for source-to-source analysis and transformations.

## Risks and Edge Cases

The parse impl sets `shebang` to `None`, so using `input.parse::<File>()` directly on token streams cannot recover a shebang. The item loop depends on each `Item` parser consuming input; if an item parser ever accepted empty input it would risk an infinite loop, but Syn item parsers should not. Printing omits shebang, consistent with token-stream printing but relevant for exact source regeneration.

## Test Signals

No inline tests appear here. Useful tests should cover parse_file shebang preservation, direct `Parse` shebang absence, inner attributes before items, empty files, item sequences, and token printing of attributes/items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/fixup.rs -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/fixup.rs -->
