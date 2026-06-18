# Research: subset-b-006319

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/item.rs -->
## sources/distributed-fs/ceph-client/rust/syn/item.rs

### Purpose
`item.rs` defines Syn's full-feature AST for Rust items and item-like declarations: module items, use trees, foreign items, trait items, impl items, signatures, receivers, variadics, and static mutability. It is compiled behind the crate `full` feature and is the main structured representation used when parsing whole Rust files or item streams for procedural macros.

### Important APIs, Types, And Functions
The central enum is `Item`, with variants for `Const`, `Enum`, `ExternCrate`, `Fn`, `ForeignMod`, `Impl`, `Macro`, `Mod`, `Static`, `Struct`, `Trait`, `TraitAlias`, `Type`, `Union`, `Use`, and `Verbatim`. Its structs preserve attributes, visibility, keyword tokens, identifiers, generics, bodies, and punctuation. `UseTree` represents nested `use` syntax through `UsePath`, `UseName`, `UseRename`, `UseGlob`, and `UseGroup`. `ForeignItem`, `TraitItem`, and `ImplItem` mirror Rust's nested item contexts and each includes a `Verbatim(TokenStream)` escape hatch for accepted-but-unmodeled syntax. `Signature`, `FnArg`, `Receiver`, and `Variadic` model callable signatures and expose helpers like `Signature::receiver()` and `Receiver::lifetime()`. Conversion impls bridge `DeriveInput` with `ItemStruct`, `ItemEnum`, and `ItemUnion`.

### Control Flow
Parsing is implemented in `parsing`. `Parse for Item` gathers outer attributes, forks the input, parses visibility on the fork, then dispatches through `parse_rest_of_item`. The dispatch branches distinguish function signatures, extern crate/extern blocks, use/static/const/unsafe/mod/type/struct/enum/union/trait/impl/macro cases and then reattaches outer attributes using `replace_attrs`. Many helpers parse a broad syntax first and then decide whether to return a structured node or `Verbatim`, such as `parse_item_type`, `parse_foreign_item_type`, `parse_impl`, `parse_trait_item_type`, and `parse_impl_item_type`.

Function signatures flow through `peek_signature`, `parse_signature`, `parse_fn_args`, and `parse_fn_arg_or_variadic`. Receiver parsing reconstructs shorthand `self`, `&self`, and `&mut self` into a `Type` when no explicit `self: Type` is present. Nested modules, extern blocks, traits, and impls parse inner attributes before recursively parsing contained items. The printing module emits tokens in Rust source order, including inner attributes inside braces and special handling for receiver shorthand consistency.

### State And Persistence Behavior
The module has no filesystem or durable persistence. Its state is the owned AST: vectors of attributes/items, boxed subtrees, `Punctuated` lists, spans carried by token types, and `TokenStream` verbatim payloads. Parser state is transient and uses `ParseStream` forks for speculative dispatch. The `Verbatim` variants preserve input tokens for syntax that was consumable but not represented structurally, which is important for round-tripping and forward compatibility.

### Dependencies And Integration Points
This file integrates with most of Syn: attributes, derive data, expressions, generics, lifetimes, macros, patterns, paths, punctuation, visibility restrictions, statements, tokens, types, verbatim token capture, and printing. It depends on `proc_macro2::TokenStream` for unstructured fragments and on `quote::ToTokens` when `printing` is enabled. Downstream users encounter these APIs through crate-root re-exports in `lib.rs`.

### Risks
The highest-risk area is parser classification. Some Rust syntax is intentionally parsed to `Verbatim` rather than rejected, including const/type generic edge cases, safe/unsafe extern additions, const impls, impl items with omitted bodies, and unsupported use-tree crate-root patterns. Changes here can silently shift downstream macro behavior from structured AST to verbatim tokens or vice versa. The parser also relies on careful attribute transfer after speculative parsing; mistakes can drop or duplicate attributes. `Receiver` printing can emit explicit `: Type` if the stored type no longer matches shorthand assumptions, so AST mutation code must preserve invariants intentionally.

### Test Signals
Useful tests are parse/print round trips for each `Item`, nested module/trait/impl/foreign contexts, attribute placement, macro item semicolon behavior, receiver forms, variadics, use groups, negative trait impls, and all `Verbatim` fallback cases. Feature-combination tests should cover `full+parsing`, `full+printing`, and `full` without printing because error paths differ when `ToTokens` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/item.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/lib.rs -->
## sources/distributed-fs/ceph-client/rust/syn/lib.rs

### Purpose
`lib.rs` is the crate root for the vendored Syn parser library. It documents Syn's procedural macro use cases, declares crate-level lints and feature gates, wires internal modules, and defines the top-level parsing entry points `parse`, `parse2`, `parse_str`, and `parse_file`.

### Important APIs, Types, And Functions
Most public API in this file is re-export orchestration. It re-exports AST nodes from `attr`, `data`, `derive`, `expr`, `file`, `generics`, `ident`, `item`, `lifetime`, `lit`, `mac`, `meta`, `op`, `pat`, `path`, `restriction`, `stmt`, and `ty` according to feature flags. It exposes `Error` and `Result` unconditionally, `punctuated` unconditionally, parser modules under `parsing`, and traversal modules `fold`, `visit`, and `visit_mut` from generated code when enabled. `__private` points to `export.rs` for non-public support.

The parsing entry points are thin wrappers: `parse<T>` accepts `proc_macro::TokenStream` when both `parsing` and `proc-macro` are enabled, `parse2<T>` accepts `proc_macro2::TokenStream`, and `parse_str<T>` parses string input. `parse_file` is specialized for full Rust files and preserves file-level affordances not handled by plain `FromStr`.

### Control Flow
Compilation is driven by `cfg` gates. Modules are only declared and re-exported when the corresponding features are enabled, which keeps procedural macro compile times lower for derive-only users. The generated `gen` module contains documentation and conditional declarations for traversal, clone, debug, equality, and hash support.

`parse_file` strips a UTF-8 byte order mark, detects a shebang beginning with `#!` unless it is an inner attribute (`#![...]` after whitespace), removes that shebang from the parsed content, delegates to `parse_str::<File>`, and restores the shebang onto the resulting `File`.

### State And Persistence Behavior
The crate root keeps no mutable runtime state. Its significant state is compile-time module availability determined by Cargo features. `parse_file` temporarily owns a shebang `String` and returns it in the AST. All parsing functions enforce complete consumption through the underlying `Parser` APIs.

### Dependencies And Integration Points
This file integrates Syn with `proc_macro` when enabled, `proc_macro2` for token-stream parsing, and feature-gated traversal/printing/parsing modules. It is the canonical integration surface for downstream macro crates because downstream code normally imports `syn::{parse_macro_input, DeriveInput, Item, Expr, Type, ...}` from these re-exports.

### Risks
Feature gates are the main risk. Moving a module or re-export across feature conditions can break downstream builds or unexpectedly increase compile cost. `parse_file` shebang detection must keep distinguishing real shebangs from inner attributes, otherwise valid crate files can parse incorrectly. Because this file is the public API hub, re-export changes are semver-sensitive even when internal modules remain unchanged.

### Test Signals
Tests should exercise representative feature matrices: default derive/parsing/printing, derive-only, full parsing, full printing, traversal features, extra traits, and proc-macro parsing. `parse_file` needs tests for BOMs, shebang-only files, shebang plus items, and inner attributes at the top of the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/lifetime.rs -->
## sources/distributed-fs/ceph-client/rust/syn/lifetime.rs

### Purpose
`lifetime.rs` defines the AST representation of a Rust lifetime such as `'a`, including construction, span handling, parsing, printing, display, ordering, equality, and hashing behavior.

### Important APIs, Types, And Functions
`Lifetime` stores two pieces of state: `apostrophe: Span` and `ident: proc_macro2::Ident`. `Lifetime::new(symbol, span)` validates that the symbol begins with an apostrophe, is not only an apostrophe, and that the name after the apostrophe satisfies Syn's identifier XID rules. `span()` joins the apostrophe and identifier spans when possible, and `set_span()` updates both components. Formatting prints the apostrophe followed by the identifier. Equality, ordering, and hashing are based on the identifier, not the apostrophe span.

### Control Flow
Parsing is feature-gated under `parsing` and uses `ParseStream::step` with the token cursor's `lifetime()` primitive. If no lifetime token is present, it produces `expected lifetime`. Printing constructs a joint apostrophe punctuation token with the stored apostrophe span and then emits the identifier.

### State And Persistence Behavior
There is no durable persistence. The value preserves token span state for diagnostics and code generation. The equality model intentionally ignores span, making lifetimes with the same textual identifier compare equal even if they came from different source locations.

### Dependencies And Integration Points
This module depends on `proc_macro2::{Ident, Span}`, `crate::ident::xid_ok`, `crate::lookahead` for token marker integration, Syn's `Parse` trait, and `quote::ToTokens` for printing. It is used throughout generics, type references, receivers, and bounds.

### Risks
`Lifetime::new` panics on invalid input rather than returning `Result`, which is appropriate for construction APIs but risky if callers pass untrusted strings. Span joining can fail and falls back to the apostrophe span, so diagnostics may be less precise for synthesized lifetimes. Equality ignoring span is correct for AST semantics but unsuitable for callers trying to distinguish source origins.

### Test Signals
Tests should cover valid Unicode/XID lifetime names, invalid names, empty apostrophe-only input, span update behavior, parse errors, `ToTokens` apostrophe spacing, and equality/hash behavior across different spans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/lifetime.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/lit.rs -->
## sources/distributed-fs/ceph-client/rust/syn/lit.rs

### Purpose
`lit.rs` defines Syn's literal AST, literal constructors/accessors, token conversion, parsing, printing, debug/clone/extra traits, and internal literal-value decoding. It covers string, byte string, C string, byte, char, integer, float, boolean, and verbatim literals.

### Important APIs, Types, And Functions
`Lit` is the central enum. Structured wrappers include `LitStr`, `LitByteStr`, `LitCStr`, `LitByte`, `LitChar`, `LitInt`, `LitFloat`, and `LitBool`. String-like and byte-like literals store a `LitRepr` containing the original `proc_macro2::Literal` and suffix. Numeric literals store `LitIntRepr` or `LitFloatRepr`, retaining the original token plus normalized `digits` and suffix. Public constructors such as `LitStr::new`, `LitInt::new`, and `LitBool::new` synthesize tokens with spans. Accessors expose decoded values, suffixes, spans, mutable span updates, and cloned tokens. `LitStr::parse` and `parse_with` parse the literal contents as Rust tokens after respanning every token to the literal's span.

### Control Flow
`Parse for Lit` first accepts cursor literals, then boolean identifiers, then a `-` punctuation followed by numeric literal via `parse_negative_lit`. Specific literal parsers parse `Lit` and downcast to the requested variant. Internal `value::Lit::new` classifies a `proc_macro2::Literal` by its textual representation. String and byte parsers decode cooked/raw syntax, escape sequences, line continuations, suffixes, Unicode escapes, and C string nul restrictions. `parse_lit_int` converts binary/octal/hex/decimal literals into normalized base-10 digits using `BigInt`; `parse_lit_float` removes underscores and normalizes exponent syntax while preserving a valid suffix.

### State And Persistence Behavior
No filesystem persistence exists. The module deliberately stores both source token identity and decoded/normalized data. This dual state lets `ToTokens` preserve the original literal spelling while APIs like `base10_digits()` and `value()` provide semantic content. Parsing via `LitStr::parse_with` creates transient respanned token streams so diagnostics point at the original string literal.

### Dependencies And Integration Points
The module depends on `proc_macro2::{Literal, Ident, Span, TokenStream, TokenTree, Punct}`, Syn's parser and error APIs, `crate::bigint::BigInt`, `crate::ident::xid_ok`, token lookahead integration, `quote::ToTokens`, and standard `CStr/CString`. It is used by expressions, attributes/meta parsing, token peeking, and procedural macro helper APIs.

### Risks
Several internal decoders use `assert!`, `assert_eq!`, `unwrap`, and `panic!` under the assumption that `proc_macro2` only provides syntactically valid literals. If callers construct invalid strings for `LitInt::new` or `LitFloat::new`, these APIs panic. Escape decoding is subtle, especially C string nul rejection, raw string pound counting, negative numeric spans, and suffix validation through `xid_ok`. Classification based on `Literal::to_string()` is tied to proc-macro2 formatting.

### Test Signals
Tests should cover all literal kinds, cooked/raw string and byte string escapes, C string nul errors, Unicode escapes with underscores and length limits, byte/char escape limits, numeric bases and underscore normalization, float exponent forms, suffix acceptance/rejection, negative int/float parsing, respanned `LitStr::parse_with` errors, and print round trips preserving token spelling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/lit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/lookahead.rs -->
## sources/distributed-fs/ceph-client/rust/syn/lookahead.rs

### Purpose
`lookahead.rs` implements `Lookahead1`, Syn's helper for parser dispatch based on the next token with accumulated, human-readable error messages. It also defines the sealed `Peek` trait and the pseudo-token `End`.

### Important APIs, Types, And Functions
`Lookahead1<'a>` stores a diagnostic scope `Span`, a `Cursor<'a>`, and a `RefCell<Vec<&'static str>>` of failed token expectations. `new(scope, cursor)` constructs it. `Lookahead1::peek(T)` checks a token type implementing `Peek`; failed comparisons are recorded for later diagnostics. `Lookahead1::error()` formats `unexpected end of input`, `unexpected token`, `expected X`, `expected X or Y`, or `expected one of: ...`. `End` is a custom token whose `peek` succeeds at EOF and whose display placeholder is rewritten to the current closing delimiter.

### Control Flow
Every `peek` delegates to `peek_impl`. If the token matches, it returns true immediately and does not record anything. If not, it appends the token display string. `error()` consumes the lookahead, rewrites the special `)` display based on the cursor's scope delimiter, removes it for delimiter-less scope, and emits an error at the cursor using `error::new_at` unless no comparisons were recorded.

### State And Persistence Behavior
State is transient and diagnostic-only. `RefCell` allows `peek` to take `&self` while appending expectations. Consuming tokens from the original parse stream after constructing `Lookahead1` does not advance this stored cursor, so callers must create a fresh lookahead after changing parse position.

### Dependencies And Integration Points
The module depends on parser cursors, Syn error construction, sealed traits, span conversion, and token traits. `Peek` is sealed so only Syn-controlled token marker functions and `End` can implement it. It is used throughout parser modules, including `item.rs`, `op.rs`, and `meta.rs`, to produce consistent errors for alternative syntax branches.

### Risks
Because failed peek order becomes the error message order, parser branches affect diagnostics. Reusing a lookahead after consuming input can produce stale errors. The `End` display rewrite is delimiter-sensitive; incorrect cursor scope would report the wrong closing delimiter. The `RefCell` design is simple but means repeated failed peeks against the same token can duplicate expected entries.

### Test Signals
Tests should cover zero, one, two, and many expected alternatives; EOF diagnostics; delimiter-specific `End` messages for parentheses, braces, and brackets; stale lookahead behavior expectations; and parser examples that use `peek2(End)` for trailing comma handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/lookahead.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/mac.rs -->
## sources/distributed-fs/ceph-client/rust/syn/mac.rs

### Purpose
`mac.rs` defines the AST for a Rust macro invocation and the delimiter abstraction around macro bodies. It also provides helpers for parsing macro body tokens into typed syntax and printing macro invocations.

### Important APIs, Types, And Functions
`Macro` contains a module-style `Path`, a bang token, a `MacroDelimiter`, and the body `TokenStream`. `MacroDelimiter` distinguishes `Paren`, `Brace`, and `Bracket` delimiters and exposes `span()` plus the internal `is_brace()` helper used by item parsers to decide whether a trailing semicolon is required. `Macro::parse_body` and `parse_body_with` parse the stored body tokens with a caller-provided parser, scoping errors to the closing delimiter span for better diagnostics. `parse_delimiter` extracts a grouped token tree and returns the delimiter plus its stream.

### Control Flow
`Parse for Macro` parses a module-style path, `!`, then delegates to `parse_delimiter`. `parse_delimiter` uses a cursor step to require a `TokenTree::Group`; parenthesis, brace, and bracket groups are converted into Syn token structs using `DelimSpan`, while `Delimiter::None` is rejected. Printing emits the macro path in module style, the bang, and surrounds cloned body tokens with the original delimiter span.

### State And Persistence Behavior
There is no durable persistence. The macro body remains an opaque `TokenStream` until a caller invokes `parse_body*`. Delimiter spans are retained separately from body tokens for printing and diagnostics.

### Dependencies And Integration Points
This module integrates with `path`, `token`, Syn parsing, `proc_macro2::{TokenStream, TokenTree, Delimiter}`, `proc_macro2::extra::DelimSpan`, and `quote::ToTokens`. It is referenced by item, expression, pattern, type, trait item, impl item, and foreign item AST nodes.

### Risks
Macro contents are intentionally not parsed eagerly, so downstream code must choose an appropriate parser and handle arbitrary tokens. `Delimiter::None` groups are rejected, which is correct for Rust macro invocations but relevant if callers feed synthetic token streams. Semicolon behavior for macro items depends on `is_brace`, so delimiter changes affect parse/print compatibility.

### Test Signals
Tests should cover all three delimiters, rejection of delimiter-less groups, body parsing success and empty-body errors, span placement for body parse failures, path style printing, and item/trait/impl/foreign macro semicolon rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/mac.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/macros.rs -->
## sources/distributed-fs/ceph-client/rust/syn/macros.rs

### Purpose
`macros.rs` contains local macro definitions that generate much of Syn's AST boilerplate. It centralizes struct/enum declarations, enum-to-struct `From` impls, `ToTokens` forwarding for enum wrappers, doc-only visibility tweaks, keyword validation, and docsrs-specific return type selection.

### Important APIs, Types, And Functions
`ast_struct!` declares AST structs and can create placeholder non-`full` versions for `#full` structs. `ast_enum!` declares AST enums under the appropriate feature gates. `ast_enum_of_structs!` declares an enum, generates `From<Member>` conversions through `ast_enum_of_structs_impl!`, and generates `ToTokens` forwarding when `printing` is enabled. `pub_if_not_doc!` exposes hidden parser marker functions publicly outside docs while keeping them crate-private during documentation builds. `return_impl_trait!` switches between a concrete return type for normal builds and an `impl Trait` signature for docsrs.

### Control Flow
These macros expand at compile time only. `generate_to_tokens!` recursively accumulates match arms for enum variants, ignoring fieldless variants and forwarding single-member variants to the contained node's `ToTokens`. `check_keyword_matches!` forces macro invocations to use the expected literal keywords (`pub`, `struct`, `enum`) and prevents accidental syntactic drift.

### State And Persistence Behavior
The file has no runtime state. Its "state" is compile-time generated code conditioned on crate features. Placeholder structs for non-`full` builds use `PhantomData<proc_macro2::Span>` to prevent construction while keeping type names available for selected feature combinations.

### Dependencies And Integration Points
Every AST module in this subset relies on these macros. They integrate with `quote::ToTokens`, `proc_macro2::TokenStream`, docsrs cfgs, and Syn's feature gating policy. The generated `From` impls and printing impls are part of the ergonomic public surface even though the macros are internal.

### Risks
Macro changes have wide blast radius. A small change can alter public type layout, generated trait impls, docs visibility, or feature-gated availability across the crate. The recursive token-generation macro assumes enum variants are either fieldless or single-member wrappers; adding a differently shaped enum through this macro would require macro changes. Placeholder non-`full` structs intentionally panic on printing, so they must remain unreachable under valid feature combinations.

### Test Signals
Tests should compile representative AST modules under feature combinations, verify `From` conversions for enum wrapper variants, verify generated `ToTokens` forwarding, run docs builds, and include trybuild-style checks for public visibility under docs and non-docs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/macros.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/meta.rs -->
## sources/distributed-fs/ceph-client/rust/syn/meta.rs

### Purpose
`meta.rs` provides parsing utilities for structured attribute contents such as `#[tea(kind = "EarlGrey", hot, with(sugar))]`. It is focused on conventional nested meta syntax and is available when parsing plus `full` or `derive` support is enabled.

### Important APIs, Types, And Functions
`parser(logic)` adapts a `FnMut(ParseNestedMeta) -> Result<()>` callback into a `Parser<Output = ()>` usable with `parse_macro_input!` for attribute macro arguments. `ParseNestedMeta<'a>` exposes the parsed `path` and remaining `input` for one property. `value()` consumes `=` and returns the same parse stream for parsing the value. `parse_nested_meta()` parses parenthesized nested content using the same convention. `error(msg)` creates a span covering the property path through the latest consumed token. The internal `parse_nested_meta` loop handles comma-separated properties and trailing commas. `parse_meta_path` parses paths that accept keywords as identifiers and emits tailored errors for literals or other unexpected tokens.

### Control Flow
The top-level parser returns `Ok(())` on empty input; otherwise it loops through `parse_nested_meta`. Each iteration parses a meta path, calls user logic with the current parse stream, then requires a comma unless the input is empty. Nested lists are parsed by `parenthesized!` and recursively applying the same loop. User logic is responsible for interpreting `path`, deciding whether to call `value`, parse a list, or reject the property.

### State And Persistence Behavior
There is no persistent state. Mutable state is normally held by the user's closure, as shown in the examples that fill option and vector fields. `ParseNestedMeta` borrows the active parse stream, so it is a transient view into the parser cursor.

### Dependencies And Integration Points
This module integrates with `Attribute::parse_nested_meta`, `parse_macro_input!`, Syn's `Parser` trait, paths, literals, punctuation, and error construction. It uses `IdentExt::parse_any` so keywords can appear in meta paths, matching Rust attribute conventions.

### Risks
`parser` is explicitly less precise for non-attribute-macro contexts because rustc conceals surrounding delimiter spans for proc-macro attribute arguments. Callers should prefer `Attribute::parse_nested_meta` when they have a full `Attribute`. The utility only fits conventional structured attributes; arbitrary token grammars inside parentheses should parse the exposed `ParseStream` directly. Error span construction depends on `prev_span`, so callbacks that parse far ahead before calling `error` intentionally produce wider diagnostics.

### Test Signals
Tests should cover empty args, simple flags, name-value pairs, nested lists, trailing commas, keyword path segments, leading colons and path separators, unsupported literals in path position, custom errors after value parsing, and comparison between `parser` and `Attribute::parse_nested_meta` span quality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/meta.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/op.rs -->
## sources/distributed-fs/ceph-client/rust/syn/op.rs

### Purpose
`op.rs` defines AST enums for Rust binary and unary operators and supplies parser and printer implementations. These enums are used by expression nodes and traversal/printing code.

### Important APIs, Types, And Functions
`BinOp` is a non-exhaustive enum covering arithmetic, logical, bitwise, comparison, shift, and assignment operators: `+`, `-`, `*`, `/`, `%`, `&&`, `||`, `^`, `&`, `|`, `<<`, `>>`, `==`, `<`, `<=`, `!=`, `>=`, `>`, and the compound assignment forms. `UnOp` covers dereference `*`, logical not `!`, and negation `-`. Each variant stores the exact token type, preserving span and spelling for diagnostics and printing.

### Control Flow
`Parse for BinOp` checks longest and most specific tokens first, especially assignment and multi-character operators, before falling back to single-character operators. This avoids consuming `+=` as `+` or `<<=` as `<<`. `Parse for UnOp` uses `lookahead1` to collect useful errors across `*`, `!`, and `-`. Printing is a direct match that delegates to each stored token's `ToTokens` implementation.

### State And Persistence Behavior
No persistent state exists. Operator values hold only token spans through their token fields. The enums are non-exhaustive, so downstream matching must retain a fallback for future Rust operators.

### Dependencies And Integration Points
The module depends on Syn token definitions, parser traits, lookahead diagnostics, and `quote::ToTokens`. It is consumed by expression parsing/printing, precedence handling, visitors/folders, and extra trait generation.

### Risks
Ordering in `BinOp::parse` is critical. Reordering multi-character operators after prefixes would create incorrect token consumption. Because assignment operators are represented in `BinOp`, downstream consumers must distinguish arithmetic/logical binary operations from assignment-like operations when semantics matter. Non-exhaustiveness requires careful downstream matches.

### Test Signals
Tests should parse and print every operator, verify longest-match behavior for `>>=`, `<<=`, `>=`, `<=`, `==`, `!=`, `&&`, `||`, and assignment operators, confirm invalid input diagnostics, and run expression parser tests that validate precedence integration outside this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/op.rs -->
