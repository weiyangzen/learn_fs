# subset-b-006320 grouped research

Work item: `subset-b-006320`

This grouped report covers the requested `sources/distributed-fs/ceph-client/rust/syn` source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/parse.rs -->
# sources/distributed-fs/ceph-client/rust/syn/parse.rs

## Purpose
`parse.rs` is the core Syn parsing API. It defines the `Parse` trait, `ParseStream` alias, `ParseBuffer` cursor wrapper, speculative parsing support, low-level token `Parse` impls, the `Parser` trait entry points, and the `Nothing` sentinel parser. It is the central bridge from `proc_macro2::TokenStream` and, behind `proc-macro`, `proc_macro::TokenStream` into Syn AST nodes.

## Important APIs, types, and functions
Key public APIs are `Parse::parse`, `ParseStream<'a>`, `ParseBuffer`, `StepCursor`, `Parser::{parse2, parse, parse_str}`, `parse_scoped`, and `Nothing`. `ParseBuffer` exposes `parse`, `call`, `peek`, `peek2`, `peek3`, `parse_terminated`, `is_empty`, `lookahead1`, `fork`, `error`, `step`, `span`, and `cursor`. Low-level `Parse` impls exist for `Box<T>`, `Option<T>`, `TokenStream`, `TokenTree`, `Group`, `Punct`, and `Literal`.

## Control flow
Top-level parsing flows through a `Parser` impl for parser functions. `parse2` builds a `TokenBuffer`, wraps its begin cursor in `ParseBuffer`, invokes the parser, checks delayed unexpected-token state, and rejects leftover tokens. `ParseBuffer::step` hands a `StepCursor` to a closure and advances the stored cursor only on success. `fork` copies cursor state for speculative parsing; successful forks can be reconciled by the discouraged speculative extension outside this file.

## State and persistence behavior
State is in memory only. `ParseBuffer` stores cursor position in a `Cell<Cursor<'static>>` with `PhantomData` to preserve variance and uses an `unexpected` `Rc<Cell<Unexpected>>` chain to report tokens left inside dropped parse buffers. There is no disk, network, or durable persistence.

## Dependencies and integration points
The file depends on `crate::buffer`, `crate::error`, `crate::lookahead`, `crate::punctuated`, and `crate::token`, plus `proc_macro2`, `quote` under `printing`, and standard `Cell`, `Rc`, `PhantomData`, and panic-safety traits. Nearly every `parsing` module in Syn consumes `ParseStream` and `Parser`.

## Risks
This file contains intentional `unsafe` lifetime transmute logic in `new_parse_buffer`, `advance_step_cursor`, and cursor storage. Soundness depends on all cursors assigned to `cell` originating from the same token buffer or a proven compatible `StepCursor`. Speculative parsing can be expensive if a fork parses unbounded input. Delayed unexpected-token reporting through `Drop` is subtle and should be tested with delimiter leftovers.

## Test signals
Useful tests include parsing success and leftover-token failure for `parse2`, `parse_str` hygiene expectations, `fork` plus `advance_to` scenarios, `step` rollback on error, nested delimiter unexpected-token diagnostics, low-level token parses, and `Nothing` rejecting non-empty input through the outer parser's leftover-token check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/parse.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/parse_macro_input.rs -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/parse_macro_input.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/parse_quote.rs -->
# sources/distributed-fs/ceph-client/rust/syn/parse_quote.rs

## Purpose
`parse_quote.rs` implements typed quasi-quotation: it lets callers write quoted Rust tokens and parse them immediately into an inferred Syn syntax tree type.

## Important APIs, types, and functions
Important APIs are exported macros `parse_quote!` and `parse_quote_spanned!`, hidden function `parse<T: ParseQuote>`, and hidden trait `ParseQuote`. Blanket `ParseQuote` covers all `T: Parse`. Special impls cover `Attribute`, `Vec<Attribute>`, `Field`, `Pat`, `Box<Pat>`, `Punctuated<T, P>`, `Vec<Stmt>`, and `Vec<Arm>` under relevant features.

## Control flow
The macros call `quote!` or `quote_spanned!`, then pass the `TokenStream` to `__private::parse_quote`. `parse` invokes `T::parse` through the `Parser` trait and panics on parse failure. Special `ParseQuote` impls select context-sensitive parsers, such as inner versus outer attributes and multi-pattern parsing.

## State and persistence behavior
All state is transient token streams and parser cursor state. It performs no persistence.

## Dependencies and integration points
This file depends on `quote`, `proc_macro2::TokenStream`, `parse::{Parse, ParseStream, Parser}`, `Punctuated`, and AST modules for attributes, fields, patterns, blocks, statements, and match arms. It integrates with `parse.rs` as a panic-on-invalid-input convenience layer for code generation.

## Risks
`parse_quote!` panics instead of returning `Result`, so it is appropriate only when quoted tokens are known valid. Special-case parsers must track Syn grammar changes, especially fields, patterns, and match arms. Feature gates affect which target types are available.

## Test signals
Tests should cover normal `Parse` targets, all special targets, span propagation for `parse_quote_spanned!`, trailing punctuation in `Punctuated`, inner and outer attributes, and expected panic messages for invalid quoted syntax.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/parse_quote.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/pat.rs -->
# sources/distributed-fs/ceph-client/rust/syn/pat.rs

## Purpose
`pat.rs` defines Syn's pattern AST and the parser/printer for Rust patterns under the `full` feature. It reuses expression structs for const, literal, macro, path, and range pattern forms.

## Important APIs, types, and functions
The main enum is `Pat` with variants including `Const`, `Ident`, `Lit`, `Macro`, `Or`, `Paren`, `Path`, `Range`, `Reference`, `Rest`, `Slice`, `Struct`, `Tuple`, `TupleStruct`, `Type`, `Verbatim`, and `Wild`. Structs include `PatIdent`, `PatOr`, `PatParen`, `PatReference`, `PatRest`, `PatSlice`, `PatStruct`, `PatTuple`, `PatTupleStruct`, `PatType`, `PatWild`, and `FieldPat`. Parser entry points are `Pat::parse_single`, `parse_multi`, and `parse_multi_with_leading_vert`.

## Control flow
`parse_single` dispatches by lookahead to path/macro/struct/range, wildcard, box verbatim, literal/range, binding, reference, tuple/paren, slice, rest, and const-block forms. `multi_pat_impl` wraps one or more single patterns separated by top-level `|` into `Pat::Or`. Struct and tuple-struct parsers use `Punctuated`; range parsing converts bounds into expression-backed `PatRange`; slice parsing rejects unparenthesized open range patterns.

## State and persistence behavior
Pattern parsing is stateless beyond parse cursor advancement. Unsupported or intentionally preserved syntax, such as `box` patterns and const block tokens, is retained as `TokenStream` in `Pat::Verbatim`.

## Dependencies and integration points
It depends on attributes, members, paths and `QSelf`, `Punctuated`, types, expressions, macro delimiter parsing, `verbatim`, and block parsing for const patterns. Printing integrates with `FilterAttrs`, `path::printing`, and `quote::ToTokens`.

## Risks
Pattern grammar is context-sensitive and edition-sensitive around top-level or-patterns. Range parsing and slice range rejection are high-risk. This vendored file appears to contain duplicated source text in `pat_range` (`end` field assigned twice), which should be treated as a compile/test risk in this checkout.

## Test signals
Tests should cover function-parameter patterns versus match-arm patterns, leading `|`, struct shorthand fields with `ref` and `mut`, tuple singletons, rest patterns, open and closed ranges, slice rejection of unparenthesized ranges, macro patterns, const patterns, and round-trip printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/pat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/path.rs -->
# sources/distributed-fs/ceph-client/rust/syn/path.rs

## Purpose
`path.rs` defines Rust paths, generic path arguments, associated item constraints, qualified self paths, and parsing/printing for those forms.

## Important APIs, types, and functions
Core types are `Path`, `PathSegment`, `PathArguments`, `GenericArgument`, `AngleBracketedGenericArguments`, `AssocType`, `AssocConst`, `Constraint`, `ParenthesizedGenericArguments`, and `QSelf`. Important methods include `Path::is_ident`, `get_ident`, `require_ident`, `PathArguments::{is_empty,is_none}`, `Path::parse_mod_style`, `parse_helper`, `parse_rest`, `is_mod_style`, `qpath`, `const_argument`, and `AngleBracketedGenericArguments::parse_turbofish`.

## Control flow
Parsing starts with optional leading `::`, one segment, then repeated `::` segments unless followed by parenthesized generic arguments. `GenericArgument::parse` first handles lifetimes and const arguments, then parses a `Type` and reclassifies single-segment path types followed by `=` or `:` into associated const/type/bound arguments. `qpath` parses `<T as Trait>::Item` or `<T>::Item` and records the `QSelf` position.

## State and persistence behavior
No durable state is used. Paths preserve token spans in token fields and preserve unparsed expression details through nested AST nodes.

## Dependencies and integration points
The file depends on expressions, generics, identifiers, lifetimes, literals, `Punctuated`, tokens, and types. Printing integrates with `generics::printing`, `TokensOrDefault`, `Spanned`, and `quote`.

## Risks
Path parsing must disambiguate comparisons, turbofish, qualified paths, associated type bindings, associated consts, and constraints. Printing intentionally reorders lifetimes before other angle-bracketed arguments, matching Rust syntax expectations but requiring care for round trips. This checkout appears to include duplicated source text in `Path::parse_helper` (`segments` repeated), which is a compile/test risk.

## Test signals
Tests should cover module-style paths, expression-style paths, turbofish, `Fn(A) -> B` parenthesized arguments, associated type and const bindings, associated type bounds, const generic blocks, `QSelf` printing, and rejection of trailing `::`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/path.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/precedence.rs -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/precedence.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/print.rs -->
# sources/distributed-fs/ceph-client/rust/syn/print.rs

## Purpose
`print.rs` provides a small printing helper for optional token fields that should emit a default token when absent.

## Important APIs, types, and functions
The only type is `TokensOrDefault<'a, T>(pub &'a Option<T>)`, with a `ToTokens` impl for `T: ToTokens + Default`.

## Control flow
`to_tokens` matches the wrapped option. `Some(t)` prints `t`; `None` constructs `T::default()` and prints that default token.

## State and persistence behavior
No state is retained and nothing is persisted. Defaults are created at print time.

## Dependencies and integration points
It depends on `proc_macro2::TokenStream` and `quote::ToTokens`. It is used by path printing, especially when a syntactically required token such as `as` or `::` should be emitted even if the AST stores it as optional.

## Risks
Default token spans are call-site spans, so diagnostics or formatting that rely on original spans may lose precision when a missing optional token is synthesized. The helper should only be used where synthesis is semantically correct.

## Test signals
Tests should cover both `Some` and `None` paths and verify default token emission in qualified path and turbofish printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/print.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/punctuated.rs -->
# sources/distributed-fs/ceph-client/rust/syn/punctuated.rs

## Purpose
`punctuated.rs` defines `Punctuated<T, P>`, Syn's shared representation for sequences of syntax nodes separated by punctuation, such as path segments, fields, generic bounds, call arguments, and pattern lists.

## Important APIs, types, and functions
Main types are `Punctuated<T, P>`, iterator types `Pairs`, `PairsMut`, `IntoPairs`, `IntoIter`, `Iter`, `IterMut`, private iterator adapters, and `Pair<T, P>`. Core methods include `new`, `is_empty`, `len`, `first`, `last`, `get`, `iter`, `pairs`, `push_value`, `push_punct`, `push`, `insert`, `pop`, `pop_punct`, `trailing_punct`, `empty_or_trailing`, and parsers `parse_terminated(_with)` and `parse_separated_nonempty(_with)`.

## Control flow
Internally, all punctuated elements except a possible final unpunctuated value are stored in `inner: Vec<(T, P)>`; the final value is `last: Option<Box<T>>`. `push_value` requires an empty or trailing state, while `push_punct` moves `last` into `inner`. Parsers alternate value parsing and punctuation parsing until stream end or missing separator.

## State and persistence behavior
State is entirely in-memory collection shape. The invariant is that `last == None` means empty or trailing punctuation, while `Some` means a final value without trailing punctuation.

## Dependencies and integration points
It depends on `Parse`, `Token`, `NoDrop`, `TrivialDrop`, standard iterators, and `quote::ToTokens` for printing. It is pervasive across Syn AST modules.

## Risks
Invariant violations panic in `push_value`, `push_punct`, `insert`, and `do_extend`. Iterator implementation uses boxed trait objects and `NoDrop`, so drop-safety assumptions matter. This vendored file appears to include duplicated/imbalanced source text around `PartialEq` and `PrivateIter` implementations, which is a serious compile/test signal for this checkout.

## Test signals
Tests should cover empty, singleton, trailing-punctuation, and non-trailing states; forward/backward iteration; mutable iteration; `Pair` conversion; parsing with and without trailing punctuation; `Extend<Pair>` panic after `Pair::End`; indexing; and feature-gated trait impl builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/punctuated.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/restriction.rs -->
# sources/distributed-fs/ceph-client/rust/syn/restriction.rs

## Purpose
`restriction.rs` defines visibility-related AST nodes and parsing/printing for `pub`, restricted `pub(...)`, and inherited visibility. It also reserves `FieldMutability` for future field mutability restrictions.

## Important APIs, types, and functions
Important types are `Visibility`, `VisRestricted`, and `FieldMutability`. `Visibility::parse` handles normal visibility parsing and empty none-delimited groups from `$:vis`. `Visibility::parse_pub` recognizes `pub`, `pub(crate)`, `pub(self)`, `pub(super)`, and `pub(in path)`. `Visibility::is_some` is available under `full`.

## Control flow
Parsing first detects an empty invisible group and returns `Inherited`. For `pub`, it speculatively parses parenthesized content. If the content is `crate`, `self`, or `super` and fully consumed, it records a restricted visibility without `in`. If it starts with `in`, it parses a module-style path. Otherwise, it returns plain public visibility.

## State and persistence behavior
No persistent state. Speculative parser state is reconciled with `advance_to` only after a restricted form is confirmed.

## Dependencies and integration points
It depends on paths, tokens, identifiers, `Speculative`, and parse APIs. Printing integrates with `path::printing::print_path` using `PathStyle::Mod`.

## Risks
The parser intentionally avoids misreading tuple fields like `pub (crate::A, crate::B)` as restricted visibility; this is a regression-prone ambiguity. The TODO for RFC 3323 marks future expansion risk. Printing does not automatically insert `in` for arbitrary paths when `in_token` is absent.

## Test signals
Tests should cover inherited, empty `$:vis` group, all restricted forms, `pub(in a::b)`, tuple-field ambiguity, and printing of restricted paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/restriction.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/scan_expr.rs -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/scan_expr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/sealed.rs -->
# sources/distributed-fs/ceph-client/rust/syn/sealed.rs

## Purpose
`sealed.rs` provides a tiny internal sealing trait for lookahead-related parsing APIs.

## Important APIs, types, and functions
Under `parsing`, module `lookahead` defines `pub trait Sealed: Copy {}`. There are no functions.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state and no persistence.

## Dependencies and integration points
The trait is used as a sealing bound by lookahead token machinery so only crate-approved types can participate while still allowing copyable lookahead markers.

## Risks
The only risk is API-boundary drift: if lookahead types need to be extensible outside the crate, this sealed trait prevents it by design.

## Test signals
Compile-time tests should verify intended lookahead types satisfy the bound and downstream crates cannot implement sealed internals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/sealed.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/span.rs -->
# sources/distributed-fs/ceph-client/rust/syn/span.rs

## Purpose
`span.rs` defines `IntoSpans`, a conversion trait used by generated token constructors to accept either a single `Span`, arrays of spans, or delimiter spans.

## Important APIs, types, and functions
The main API is hidden trait `IntoSpans<S> { fn into_spans(self) -> S; }`. Implementations convert `Span` into `Span`, `[Span; 1]`, `[Span; 2]`, `[Span; 3]`, and `DelimSpan`, and pass arrays or `DelimSpan` through unchanged.

## Control flow
Conversions are direct. The `Span -> DelimSpan` conversion constructs an empty none-delimited `Group`, sets its span, and returns its `delim_span`.

## State and persistence behavior
No persistent state. Temporary groups are used only to derive delimiter span data.

## Dependencies and integration points
It depends on `proc_macro2::extra::DelimSpan` and `proc_macro2::{Delimiter, Group, Span, TokenStream}`. Token constructors in `token.rs` use this trait to accept ergonomic span inputs for keywords, punctuation, and delimiters.

## Risks
Duplicating a single `Span` across multi-character punctuation loses per-character span precision. The synthetic `DelimSpan` path relies on `proc_macro2` group span behavior.

## Test signals
Tests should verify token constructors accept single spans, arrays, and delimiter spans, and that delimiter surround methods preserve expected open/close span behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/span.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/spanned.rs -->
# sources/distributed-fs/ceph-client/rust/syn/spanned.rs

## Purpose
`spanned.rs` defines Syn's `Spanned` trait, which returns a span covering a syntax tree node for diagnostics and quote-spanned code generation.

## Important APIs, types, and functions
The public trait is `Spanned: private::Sealed` with `fn span(&self) -> Span`. A blanket impl covers all `T: quote::spanned::Spanned` and delegates to `__span()`. Private sealing covers all such tokenizable types and, under `full` or `derive`, `QSelf`.

## Control flow
Calling `span()` delegates to quote's span computation. The module itself has no parser or printer control flow.

## State and persistence behavior
No state and no persistence. Span computation is derived from tokenization.

## Dependencies and integration points
It depends on `proc_macro2::Span` and `quote::spanned::Spanned`. It is used by diagnostics and by path printing for `QSelf` delimiter spans.

## Risks
Joined spans depend on compiler/proc-macro capabilities. On stable contexts where full span joining is unavailable, span may degrade to the first token. For broad diagnostics, `Error::new_spanned` may be more precise.

## Test signals
Tests should cover span results for empty token streams, simple nodes, multi-token nodes, and `QSelf`, plus diagnostic behavior using `quote_spanned!`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/spanned.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/stmt.rs -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/stmt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/thread.rs -->
# sources/distributed-fs/ceph-client/rust/syn/thread.rs

## Purpose
`thread.rs` defines `ThreadBound<T>`, a wrapper that marks values `Sync` and conditionally `Send` while only exposing references on the thread where the wrapper was created.

## Important APIs, types, and functions
The main type is `ThreadBound<T> { value, thread_id }`. APIs are `ThreadBound::new`, `ThreadBound::get`, `Debug`, and `Copy`/`Clone` for `T: Copy`. Unsafe impls provide `Sync` for all `T` and `Send` for `T: Copy`.

## Control flow
`new` records `thread::current().id()`. `get` compares the current thread id to the stored id and returns `Some(&T)` only on the original thread. `Debug` prints the value on the original thread and `"unknown"` elsewhere.

## State and persistence behavior
State is in-memory value plus original `ThreadId`. Nothing persists across process boundaries.

## Dependencies and integration points
It uses standard thread IDs and formatting traits. It is an internal helper for cases where Syn needs to carry non-thread-safe data through APIs requiring thread-safe wrappers.

## Risks
The unsafe impls rely on Rust assumptions: `T: Copy` implies no `Drop`, and all interior mutability goes through non-`Copy` `UnsafeCell`. If those assumptions change, `Send`/`Copy` reasoning must be revisited. Cross-thread `get` silently returns `None`, so callers must handle absence.

## Test signals
Tests should verify same-thread access, cross-thread denial, debug output on both threads, `Copy`/`Clone` behavior for copyable values, and compile-time trait behavior for `Send`/`Sync`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/thread.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/token.rs -->
# sources/distributed-fs/ceph-client/rust/syn/token.rs

## Purpose
`token.rs` defines Syn's token marker types for Rust keywords, punctuation, delimiters, invisible groups, and the exported `Token!` type macro. These token types are used in AST fields, peeking, parsing, printing, and span construction.

## Important APIs, types, and functions
Key APIs are trait `Token`, private traits `Sealed` and `CustomToken`, `WithSpan`, macros `define_keywords`, `define_punctuation_structs`, `define_punctuation`, `define_delimiters`, `impl_deref_if_len_is_1`, `Token!`, and generated token structs for keywords/punctuation/delimiters. Special types include `Underscore` and none-delimited `Group`. Parsing helpers are `parsing::{keyword, peek_keyword, punct, peek_punct}`; printing helpers are `printing::{punct, keyword, delim}`.

## Control flow
Generated token `Parse` impls use `ParseStream::step` to consume a keyword or punctuator sequence. Punctuation parsing walks joint punctuation characters until the requested token is matched. Printing reconstructs multi-character punctuation with joint spacing except the final character. Delimiter `surround` builds a `Group` with the requested delimiter and span.

## State and persistence behavior
Token structs store spans or span arrays. There is no persistent state. Default constructors use `Span::call_site()`.

## Dependencies and integration points
This file integrates with `parse.rs`, `span::IntoSpans`, `proc_macro2`, `quote`, lifetime parsing, and all AST modules that store `Token![...]` fields.

## Risks
Macro-generated code is broad and feature-gated. Multi-character punctuation depends on joint spacing. `Deref` for single-span punctuation uses an unsafe transparent cast to `WithSpan`. This checkout appears to define `"." pub struct Dot/1` twice in `define_punctuation!`, which is a duplicate-definition compile risk.

## Test signals
Tests should cover every `Token!` mapping, keyword and punctuation parse/peek, joint versus alone punctuation, underscore as ident or punct, delimiter `surround`, span constructors, default spans, low-level token impls, and feature-gated trait impls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/token.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/tt.rs -->
# sources/distributed-fs/ceph-client/rust/syn/tt.rs

## Purpose
`tt.rs` provides equality and hashing helpers for `proc_macro2::TokenTree` and `TokenStream` that compare structural token content rather than source spans.

## Important APIs, types, and functions
The helper wrappers are `TokenTreeHelper<'a>(pub &'a TokenTree)` and `TokenStreamHelper<'a>(pub &'a TokenStream)`, each implementing `PartialEq` and `Hash`.

## Control flow
`TokenTreeHelper::eq` recursively compares groups by delimiter and contained token trees, punctuation by character and spacing, literals by string form, and identifiers by equality. Hashing writes a variant discriminator, delimiter or punctuation details, recursive group contents, a group terminator, literal strings, and identifiers. `TokenStreamHelper` collects cloned streams into vectors, compares length, then compares helper-wrapped elements.

## State and persistence behavior
No persistent state. Token streams are cloned and collected transiently for comparison or hashing.

## Dependencies and integration points
It depends on `proc_macro2::{Delimiter, TokenStream, TokenTree}` and standard `Hash`. It is useful for `extra-traits` style equality/hash behavior where spans should not affect semantic token identity.

## Risks
Literal comparison by `to_string()` can conflate or distinguish forms according to proc-macro formatting rather than original source spelling. Collecting token streams into vectors allocates. Span-insensitive equality may be inappropriate for diagnostics-sensitive comparisons.

## Test signals
Tests should cover nested groups, delimiter differences, punctuation spacing differences, literal string forms, identifier equality, token stream length mismatches, equal streams with different spans, and hash/equality consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/tt.rs -->
