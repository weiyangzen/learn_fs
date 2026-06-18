# subset-b-006313 Rust proc-macro ecosystem research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/lib.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/lib.rs

## Purpose

This is the public facade for the vendored `proc_macro2` crate. It exposes `TokenStream`, `Span`, `TokenTree`, `Group`, `Delimiter`, `Punct`, `Spacing`, `Ident`, `Literal`, `LexError`, and `token_stream::IntoIter`, while hiding whether tokens are backed by compiler `proc_macro` objects or the crate's fallback implementation. In this source tree it is foundational for `quote` and `syn`, and for any Rust macro-adjacent code that needs token APIs outside a procedural macro context.

## Important APIs, types, and functions

`TokenStream::new`, `is_empty`, `FromStr`, conversions to/from `proc_macro::TokenStream`, `FromIterator`, `Extend`, `Display`, and `Debug` form the stream API. `LexError::span` exposes parse failure location. `Span` provides `call_site`, `mixed_site`, optional `def_site`, hygiene transformers `resolved_at` and `located_at`, optional span-location methods, `join`, semver-exempt `eq`, and `source_text`. `TokenTree` wraps `Group`, `Ident`, `Punct`, and `Literal`, forwarding `span` and `set_span`. `Group` manages delimiters, streams, delimiter spans, and span setting. `Punct` validates Rust punctuation and tracks `Spacing`. `Ident` validates normal and raw identifiers and implements equality, ordering, and hashing by textual representation. `Literal` exposes constructors for integer, float, string, character, byte, byte string, C string, parsing, spans, `subspan`, and an unsafe unchecked constructor used by `quote`.

## Control flow

The facade delegates all real work to `imp`, which is either `fallback` or `wrapper.rs` depending on `wrap_proc_macro`. Public constructors wrap `imp` values and attach the zero-sized marker from `marker.rs`. Parsing calls `imp::TokenStream::from_str_checked` or `imp::Literal::from_str_checked`, converts success into facade types, and wraps backend lex errors. Token conversion and iteration are shallow: groups remain grouped until callers explicitly enter their streams.

## State and persistence behavior

The facade itself stores only backend token objects and marker fields. Persistent state is in backend streams, spans, and literals. Spans carry hygiene and optional source-location information; stream display is intended to round trip modulo spans, `Delimiter::None`, and negative literal caveats.

## Dependencies and integration points

It depends on `marker`, `parse`, `probe`, `rcvec`, `fallback`, `extra`, optional `location`, and optional `wrapper.rs`. Public APIs are consumed by `quote`, `syn`, and procedural macro crates. Feature/config gates (`proc-macro`, `wrap_proc_macro`, `span_locations`, `procmacro2_semver_exempt`, `super_unstable`) control exposed behavior.

## Risks and test signals

Risks include backend mismatch, span hygiene regressions, invalid raw identifier acceptance, punctuation validation drift, literal round-trip edge cases, and unstable API gating. Useful tests are parse/display round trips, identifier and raw identifier validation, span-location tests under both fallback and procedural macro contexts, `quote`/`syn` integration tests, and compile checks across stable/nightly feature combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/location.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/location.rs

## Purpose

This small module defines `LineColumn`, the source position pair returned by `Span::start` and `Span::end` when span locations are enabled.

## Important APIs, types, and functions

`LineColumn` has public `line` and `column` fields. Lines are one-indexed and columns are zero-indexed UTF-8 character columns. It derives copy, clone, debug, equality, and hash, and implements `Ord` and `PartialOrd` by comparing `line` first and `column` second.

## Control flow

The only executable logic is ordering. `cmp` chains `self.line.cmp(&other.line)` with `self.column.cmp(&other.column)`, and `partial_cmp` always returns `Some(self.cmp(other))`.

## State and persistence behavior

`LineColumn` is immutable value state. It does not own file data, source maps, or spans; it is a snapshot representation of a position computed elsewhere.

## Dependencies and integration points

It depends only on `core::cmp::Ordering`. `lib.rs` publicly re-exports it behind `span_locations`, and `wrapper.rs` constructs it from compiler span probes or fallback spans.

## Risks and test signals

The key risk is semantic mismatch between compiler and fallback column numbering, especially because compiler line/column APIs may be one-indexed and wrapper code adjusts columns with `saturating_sub(1)`. Tests should compare ordering, start/end values from parsed token streams, Unicode column handling, and fallback vs compiler behavior when the feature is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/location.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/marker.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/marker.rs

## Purpose

This module defines the marker embedded in facade token types to give them the same auto-trait behavior expected for proc-macro-like objects.

## Important APIs, types, and functions

`ProcMacroAutoTraits` is a zero-sized tuple struct around `PhantomData<Rc<()>>`. `MARKER` is the singleton value used by facade structs. The type manually implements `UnwindSafe` and `RefUnwindSafe`, while the `Rc` phantom prevents unwanted `Send`/`Sync` auto traits. Under semver-exempt fallback/super-unstable configs it can derive equality.

## Control flow

There is no runtime control flow beyond construction of the constant marker.

## State and persistence behavior

No persistent state is stored. The marker influences compile-time auto-trait derivation for token wrapper types.

## Dependencies and integration points

It uses `alloc::rc::Rc`, `core::marker::PhantomData`, and panic-safety marker traits. `lib.rs` imports `MARKER` into `TokenStream`, `LexError`, `Span`, `Ident`, and `Literal`.

## Risks and test signals

Risks are trait-surface regressions: accidentally making public token types `Send` or `Sync`, or losing unwind-safety behavior. Compile-time trait assertion tests are the best signal, alongside downstream crates that rely on `proc_macro2` tokens remaining thread-local-like.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/marker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/parse.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/parse.rs

## Purpose

This file implements the fallback lexer/parser that turns Rust source text into fallback `TokenStream` values. It recognizes whitespace, comments, doc comments, groups, identifiers, raw identifiers, punctuation, strings, byte strings, C strings, characters, integers, floats, lifetimes, and selected rustc error placeholders.

## Important APIs, types, and functions

`Cursor` is the immutable parsing cursor with `rest` and optional `off` character offset. `Reject` is the local parse-failure sentinel. `token_stream` is the top-level parser that builds streams using `TokenStreamBuilder` and a delimiter stack. `leaf_token` tries literal, punctuation, identifier, and `(/*ERROR*/)` recognition. Literal helpers cover cooked/raw strings, byte strings, C strings, byte and char literals, numeric literals, suffixes, raw-string delimiters, escapes, Unicode escapes, and line continuations. `doc_comment` rewrites doc comments into `#[doc = "..."]` token trees.

## Control flow

`token_stream` loops until input is exhausted. Each iteration skips non-doc whitespace/comments, translates doc comments first, then handles opening delimiters by pushing a frame, closing delimiters by popping and creating a `Group`, or leaf tokens by parsing and assigning spans. Unbalanced or mismatched delimiters return `LexError`. Literal parsing is ordered to avoid misclassifying literal prefixes as identifiers. Punctuation determines `Joint` spacing by looking ahead to the next punctuation, with special handling for apostrophes and lifetimes.

## State and persistence behavior

Parser state is local: the current `Cursor`, output builder, delimiter stack, and optional span offsets. It persists parsed tokens into fallback `TokenStream` objects. With `span_locations`, offsets advance by character count rather than bytes, while spans store `lo`/`hi` positions for later location mapping.

## Dependencies and integration points

It depends on fallback token types and validation helpers (`is_ident_start`, `is_ident_continue`), public facade enums (`Delimiter`, `Spacing`, `TokenTree`), and `proc_macro2::Punct`. It is called by fallback `TokenStream::from_str_checked` and literal parsing.

## Risks and test signals

Risks include Rust lexical grammar drift, nested block comment edge cases, doc-comment span/content bugs, raw string delimiter limits, C string NUL handling, Unicode escape validation, float/int boundary cases such as ranges and suffixes, apostrophe/lifetime ambiguity, and byte-vs-character offset mismatch. Tests should include round-trip parsing, Rust lexer fixture comparisons, doc comment expansion, malformed literal failures, nested delimiter errors, and span-location assertions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/parse.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/probe.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/probe.rs

## Purpose

This module is the conditional hub for build-probed compiler span APIs used by the wrapper backend.

## Important APIs, types, and functions

It conditionally declares `proc_macro_span`, `proc_macro_span_file`, and `proc_macro_span_location` submodules under their matching cfg flags. It also allows dead code because these files are compile probes and conditional adapters.

## Control flow

There is no runtime logic. The build configuration decides which submodules exist, and `wrapper.rs` imports only the available ones.

## State and persistence behavior

No state is stored. The module expresses capability state through cfg-selected module availability.

## Dependencies and integration points

It integrates with the crate build script/probe results and with `wrapper.rs` span methods such as `byte_range`, `start`, `end`, `file`, `local_file`, `join`, and literal `subspan`.

## Risks and test signals

The risk is cfg skew: wrapper code may assume a probed API exists when the compiler lacks it, or docs/tests may enable incompatible flags. Build matrix tests over stable, beta, nightly, and `procmacro2_nightly_testing` are the main signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/probe.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span.rs

## Purpose

This compile-probe module exercises the full unstable `proc_macro::Span` API surface that `proc_macro2` can expose when available.

## Important APIs, types, and functions

It wraps compiler APIs for `byte_range`, `start`, `end`, `line`, `column`, `file`, `local_file`, `join`, and `Literal::subspan`. Under `procmacro2_build_probe` it enables `feature(proc_macro_span)` and includes `RUSTC_BOOTSTRAP` in the cache key.

## Control flow

Each function directly forwards to the matching `proc_macro` method. Failure is compile-time: if a method is unavailable, the probe does not compile and the cfg should not be enabled.

## State and persistence behavior

No runtime state is stored. The module returns spans, ranges, strings, and paths from compiler-owned span state.

## Dependencies and integration points

It depends on `proc_macro::{Literal, Span}`, `core::ops::{Range, RangeBounds}`, and `PathBuf`. `wrapper.rs` uses it for span locations, joining, and literal subspans when `proc_macro_span` is set.

## Risks and test signals

Risks include nightly API signature changes, incorrect cache invalidation, and calling wrappers outside procedural macro contexts. Signals include build-probe success/failure, span-location tests under nightly, and wrapper fallback behavior when the probe is disabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span_file.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span_file.rs

## Purpose

This probe covers the subset of `proc_macro::Span` file APIs stabilized in Rust 1.88.

## Important APIs, types, and functions

It exports `file(&Span) -> String` and `local_file(&Span) -> Option<PathBuf>`, each forwarding to the compiler span method.

## Control flow

There is no branching. The module exists only if the probed compiler supports these methods.

## State and persistence behavior

It has no state and returns compiler-derived path/display data. The distinction between display file and local file is important because `local_file` can reveal real disk paths.

## Dependencies and integration points

It depends on `proc_macro::Span` and `PathBuf`. `wrapper.rs` uses it when both `span_locations` and `proc_macro_span_file` are configured; otherwise compiler-backed spans fall back to placeholder file data or `None`.

## Risks and test signals

Risks include accidentally exposing remapped paths where display paths are expected, or relying on local file data in generated macro output. Tests should assert file/local_file behavior under stable compilers that support the APIs and fallback defaults when disabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span_file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span_location.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span_location.rs

## Purpose

This probe covers the span start/end and line/column subset stabilized in Rust 1.88.

## Important APIs, types, and functions

It exports `start`, `end`, `line`, and `column`, forwarding to `proc_macro::Span` methods. `start` and `end` return compiler `Span` values; `line` and `column` extract numeric positions from a span.

## Control flow

Each function is a direct wrapper. Capability is determined entirely by cfg/build probing.

## State and persistence behavior

There is no local state. Returned values are snapshots of compiler span location data.

## Dependencies and integration points

It depends on `proc_macro::Span`. `wrapper.rs` combines these calls to build `LineColumn`, subtracting one from compiler columns to maintain proc-macro2's zero-indexed column contract.

## Risks and test signals

The main risks are off-by-one column conversion, changed compiler semantics for artificial spans, and location APIs being present without meaningful data in some macro contexts. Tests should cover call-site spans, parsed fallback spans, joined spans, and generated tokens with known source positions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span_location.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/rcvec.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/rcvec.rs

## Purpose

This file provides a small copy-on-write vector abstraction used by the fallback token stream implementation to share token storage cheaply while allowing mutation when necessary.

## Important APIs, types, and functions

`RcVec<T>` wraps `Rc<Vec<T>>`. `RcVecBuilder<T>` owns a mutable `Vec<T>` during construction. `RcVecMut<'a, T>` wraps a mutable vector borrow. `RcVecIntoIter<T>` owns a `vec::IntoIter<T>`. `RcVec` exposes `is_empty`, `len`, `iter`, `make_mut`, `get_mut`, and `make_owned`. Builders expose `new`, `with_capacity`, `push`, `extend`, `len`, `is_empty`, and `build`. Mutable views expose `push`, `extend`, and `truncate`.

## Control flow

Mutation either uses `Rc::make_mut` to clone-on-write, `Rc::get_mut` to mutate only unique storage, or `make_owned` to take the vector if uniquely held and clone otherwise. Iteration is delegated to the inner vector iterator.

## State and persistence behavior

The persistent state is reference-counted token storage. Clones share the same vector until mutation. `make_owned` can drain unique storage with `mem::take`, which avoids unnecessary allocation when extending or rebuilding token streams.

## Dependencies and integration points

It depends on `alloc::rc::Rc`, `alloc::vec`, `core::mem`, and slices. Fallback `TokenStream` and `TokenStreamBuilder` use it to support cheap token stream cloning and mutable building.

## Risks and test signals

Risks are clone-on-write aliasing bugs, accidental mutation of shared vectors, capacity/length mistakes during builder conversion, and unwind-safety trait drift. Tests should clone streams, mutate one clone, verify the other is unchanged, iterate builder-owned vectors, and run `quote` workloads that repeatedly extend fallback streams.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/rcvec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/wrapper.rs -->
# sources/distributed-fs/ceph-client/rust/proc-macro2/wrapper.rs

## Purpose

This is the backend used when `proc_macro2` can wrap compiler `proc_macro` types. It dynamically chooses compiler-backed tokens inside procedural macro execution and fallback tokens outside it, while maintaining a single facade API.

## Important APIs, types, and functions

`TokenStream` is either `Compiler(DeferredTokenStream)` or `Fallback(fallback::TokenStream)`. `DeferredTokenStream` batches appended compiler token trees to avoid expensive bridge calls. `LexError` distinguishes compiler, fallback, and compiler-panic cases. `Span`, `Group`, `Ident`, and `Literal` are similar compiler/fallback enums. `mismatch` panics when mixed backends are combined. `into_compiler_token`, `unwrap_nightly`, and `unwrap_stable` perform backend conversion and validation. Span methods forward to compiler APIs when probed and otherwise return fallback/default values. Literal constructors select native compiler APIs or fallback-string construction for older compilers.

## Control flow

Most constructors branch on `inside_proc_macro()`. Compiler streams defer `Extend<TokenTree>` appends into `extra` and flush via `evaluate_now` before display, conversion, collection, or `Extend<TokenStream>`. Iteration converts compiler `proc_macro::TokenTree` values into facade token trees. Cross-backend operations panic through `mismatch` rather than silently converting spans or token storage.

## State and persistence behavior

State persists in either compiler token handles or fallback values. `DeferredTokenStream` maintains a committed compiler stream plus an uncommitted extra vector. Span source/location state remains compiler-owned for `Compiler` spans and fallback-owned for `Fallback` spans.

## Dependencies and integration points

It depends on `detection::inside_proc_macro`, fallback APIs, optional probe modules, `proc_macro`, public facade token types, `CStr`, ranges, and optional `PathBuf`. `lib.rs` uses this as `imp` under `wrap_proc_macro`, and `quote` benefits from deferred stream batching.

## Risks and test signals

Risks include backend mixing panics in unexpected paths, deferred extras not being flushed before conversion/display, stale compiler API cfgs, span-location placeholder behavior, unsafe unchecked literal parsing, and performance regressions in quote-heavy macros. Tests should cover in-proc-macro and non-proc-macro execution, stream extension batching, conversions to/from `proc_macro`, span probing fallbacks, literal constructors, and cross-backend mismatch assertions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/proc-macro2/wrapper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/ext.rs -->
# sources/distributed-fs/ceph-client/rust/quote/ext.rs

## Purpose

This file defines `TokenStreamExt`, the sealed extension trait that makes implementing `ToTokens` ergonomic by appending token trees, sequences, separated lists, and terminated lists.

## Important APIs, types, and functions

`append` extends a stream by one `Into<TokenTree>` value. `append_all` calls `ToTokens` for every item. `append_separated` writes items with an operator between them. `append_terminated` writes each item followed by a terminator. The private `Sealed` trait prevents external implementations.

## Control flow

All methods are linear iteration over provided inputs. `append_separated` uses `enumerate` to suppress the separator before the first item; `append_terminated` always appends the terminator after every item.

## State and persistence behavior

The only state mutation is appending into the caller-provided `proc_macro2::TokenStream`.

## Dependencies and integration points

It depends on `quote::ToTokens`, `proc_macro2::{TokenStream, TokenTree}`, and `core::iter`. It is re-exported from `quote/lib.rs` and used by downstream `ToTokens` implementations and quote runtime helpers.

## Risks and test signals

Risks are separator placement regressions, unintended external trait impls, and accidental extra clones for large streams. Tests should verify empty, single, and multi-item sequences for all helper methods and downstream syntax printing that relies on punctuation placement.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/ext.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/format.rs -->
# sources/distributed-fs/ceph-client/rust/quote/format.rs

## Purpose

This file implements `format_ident!`, a formatting macro for constructing `proc_macro2::Ident` values while preserving useful span hygiene from identifier fragments.

## Important APIs, types, and functions

`format_ident!` forwards to `format_ident_impl!` with an initially absent span. `format_ident_impl!` parses positional args, named args, and a special `span = ...` override, wraps arguments in `IdentFragmentAdapter`, accumulates the first fragment span with `Option::or`, runs `format!`, and calls `__private::mk_ident`.

## Control flow

Macro expansion is a recursive state machine. Final state formats the string and constructs the identifier. Span arguments override the accumulated span. Non-span arguments are adapted so their `IdentFragment` implementation controls text and optional span inheritance.

## State and persistence behavior

Macro state is compile-time token state containing the pending span expression and accumulated format invocation. Runtime persistence is just the constructed `Ident`.

## Dependencies and integration points

It depends on `IdentFragment`, `runtime::IdentFragmentAdapter`, `runtime::mk_ident`, `alloc::format`, and `proc_macro2::Span`. `quote/lib.rs` exports the macro and `ident_fragment.rs` defines the fragment trait.

## Risks and test signals

Risks include accepting invalid identifier text only to panic at construction, wrong span precedence, raw identifier prefix handling, and unsupported format traits. Tests should cover positional/named arguments, `span` override, first-identifier span inheritance, raw identifiers, numeric formatting modes, and invalid formatted identifiers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/format.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/ident_fragment.rs -->
# sources/distributed-fs/ceph-client/rust/quote/ident_fragment.rs

## Purpose

This file defines `IdentFragment`, the restricted formatting trait used by `format_ident!` to build identifier fragments safely and to inherit spans from identifier arguments.

## Important APIs, types, and functions

`IdentFragment::fmt` writes a fragment and `span` optionally returns a `Span`. Blanket impls cover references and mutable references. `Ident` strips a leading `r#` while returning its span. `Cow` forwards to the borrowed type. The `ident_fragment_display!` macro implements the trait for `bool`, `str`, `String`, `char`, and unsigned integer types.

## Control flow

Implementations are straightforward forwarding. The `Ident` implementation converts to string, strips raw prefixes if present, and writes the remaining identifier text.

## State and persistence behavior

No mutable state is held. Span information is read from `Ident` fragments and otherwise defaults to `None`.

## Dependencies and integration points

It depends on `alloc::borrow::Cow`, `core::fmt`, and `proc_macro2::{Ident, Span}`. `format.rs` and `runtime.rs` use it through `IdentFragmentAdapter`.

## Risks and test signals

Risks include allowing fragment types whose display output is not identifier-safe, losing raw identifier semantics, and missing span inheritance through wrapper types. Tests should cover references, `Cow`, raw `Ident`s, unsigned integer formatting, character fragments, invalid final identifiers, and span inheritance.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/ident_fragment.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/lib.rs -->
# sources/distributed-fs/ceph-client/rust/quote/lib.rs

## Purpose

This is the main `quote` crate facade. It documents and exports quasi-quoting macros that turn Rust-like syntax plus interpolations into `proc_macro2::TokenStream` values.

## Important APIs, types, and functions

It exports `quote!`, `quote_spanned!`, `format_ident!` from `format.rs`, `TokenStreamExt`, `IdentFragment`, `ToTokens`, hidden `__private`, and hidden `spanned`. Internal macro machinery includes `pounded_var_names!`, `quote_bind_into_iter!`, `quote_bind_next_or_break!`, `quote_each_token!`, `quote_tokens_with_context!`, `quote_token_with_context!`, and spanned equivalents. `quote_token!` and `quote_token_spanned!` map Rust tokens to runtime push helpers.

## Control flow

`quote!` handles empty, one-token, two-token, and general cases for performance. General input is transformed into seven shifted token streams so each token is processed with three-token context on either side, avoiding recursive tt-muncher behavior. Interpolations `#var` call `ToTokens`; repetitions bind interpolated variables to iterators, repeatedly pull next values, insert separators when needed, and quote the body. `quote_spanned!` follows the same flow but respans tokens originating inside the invocation.

## State and persistence behavior

Macro expansion creates a fresh `proc_macro2::TokenStream` and mutates it through runtime helpers. Repetition state includes temporary iterator bindings, a `has_iter` type-level marker, and separator index counters. Interpolated tokens keep their own spans; literal quote tokens use call-site or provided spans.

## Dependencies and integration points

It depends on `proc_macro2`, `alloc`, `runtime.rs`, `ToTokens`, and extension traits. `syn` and procedural macro crates consume these macros heavily for code generation. `quote_spanned!` integrates with `proc_macro2::Span` and `DelimSpan` via runtime span extraction.

## Risks and test signals

Risks include macro rule precedence errors, repetition without iterators, repeated variable binding advancing iterators too often, separator placement bugs, span loss in spanned quoting, unsupported token parsing fallbacks, and compile-time performance regressions for long inputs. Tests should cover all interpolation forms, nested groups, repetitions with/without separators, repeated metavariables, spanned errors, lifetimes, all multi-character punctuations, and large quote inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/runtime.rs -->
# sources/distributed-fs/ceph-client/rust/quote/runtime.rs

## Purpose

This hidden module is the runtime support library for `quote!`, `quote_spanned!`, and `format_ident!`. It provides token push helpers, repetition iterator adapters, span extraction, and identifier fragment formatting adapters.

## Important APIs, types, and functions

It re-exports hidden `format`, `Option`, and aliases for `Delimiter`, `Span`, and `TokenStream`. `HasIterator` and `ThereIsNoIteratorInRepetition` are type markers combined with `BitOr`. `ext` defines `RepIteratorExt`, `RepToTokensExt`, and `RepAsIteratorExt` for iterators, non-iterable `ToTokens` values, slices, arrays, `Vec`, `BTreeSet`, references, and `RepInterp`. `RepInterp` prevents duplicate binding from advancing the same iterator twice. `get_span` extracts spans from `Span` or `DelimSpan`. Push helpers create groups, parse fallback tokens, respan token trees, push identifiers, lifetimes, underscores, and all punctuation combinations. `mk_ident` and `ident_maybe_raw` handle raw identifiers.

## Control flow

Quote macros call push helpers in token order. Spanned helpers create tokens and then recursively replace spans through `respan_token_tree`. Repetition setup calls `quote_into_iter` on each pounded variable; the type-level marker enforces that at least one iterator is present. `RepInterp::next` returns the already-bound value when a name appears multiple times in a repetition body.

## State and persistence behavior

State is local to token construction: mutable output streams, iterator cursors, temporary span values, and formatted identifier strings. There is no global persistence.

## Dependencies and integration points

It depends on `proc_macro2` token types, `TokenStreamExt`, `ToTokens`, `IdentFragment`, `BTreeSet`, slices, formatting traits, and `DelimSpan`. `quote/lib.rs` macro rules rely on the exact helper names and hidden types.

## Risks and test signals

Risks include ambiguous `quote_into_iter` trait resolution, duplicate repetition variables advancing incorrectly, recursive respanning missing nested groups, raw identifier construction panics, parse helper failures for unusual tokens, and punctuation spacing regressions. Tests should cover repetition over all supported collection shapes, duplicated metavariables, spanned nested groups, format-ident raw names, lifetime generation, punctuation string output, and compile-fail cases for repetition with no iterator.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/runtime.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/spanned.rs -->
# sources/distributed-fs/ceph-client/rust/quote/spanned.rs

## Purpose

This hidden module provides the sealed `Spanned` trait used by `syn::spanned::Spanned`-style APIs to derive a representative span from spans, delimiter spans, or tokenizable values.

## Important APIs, types, and functions

`Spanned::__span` returns a `Span`. Implementations cover `Span`, `DelimSpan`, and all `T: ToTokens`. `join_spans` takes a token stream, uses the first and last token spans, tries `first.join(last)`, and falls back to the first span. A private sealed trait prevents external implementations.

## Control flow

For tokenizable values, `into_token_stream` materializes tokens, `join_spans` gets the first span, folds to the last span, and tries to join them. Empty token streams return `Span::call_site`.

## State and persistence behavior

No state persists. The representative span is computed from current token output, so it can change if a `ToTokens` implementation changes.

## Dependencies and integration points

It depends on `quote::ToTokens`, `proc_macro2::{Span, TokenStream}`, and `proc_macro2::extra::DelimSpan`. Syn uses this hidden support for span reporting.

## Risks and test signals

Risks include expensive tokenization for large ASTs, inaccurate spans when first/last cannot join, and call-site fallback hiding empty-token errors. Tests should cover empty streams, single tokens, multi-token values with joinable spans, delimiter spans, and non-joinable cross-file spans.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/spanned.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/to_tokens.rs -->
# sources/distributed-fs/ceph-client/rust/quote/to_tokens.rs

## Purpose

This file defines `ToTokens`, the core interpolation trait for values that can be written into `quote!` output streams.

## Important APIs, types, and functions

`ToTokens::to_tokens` is required. `to_token_stream` and `into_token_stream` are convenience methods. Blanket implementations forward for references, mutable references, `Cow`, `Box`, `Rc`, and `Option`. Primitive implementations convert strings to string literals, integers/floats to suffixed literals, chars to character literals, booleans to `true`/`false` identifiers, C strings to C string literals, and proc-macro2 token types by clone/extend.

## Control flow

Most implementations append one token. `Option` appends only when `Some`. `TokenStream` extends by one cloned stream and overrides `into_token_stream` to avoid rebuilding.

## State and persistence behavior

The only mutation is appending to the provided `TokenStream`. Primitive numeric output persists type suffixes, which matters for generated syntax.

## Dependencies and integration points

It depends on `TokenStreamExt`, `alloc` wrappers, `proc_macro2` token types, `Span`, and `std::ffi::{CStr, CString}`. `quote!` calls it for every interpolation, and `syn` implements it for AST nodes under printing features.

## Risks and test signals

Risks include unwanted numeric suffixes in contexts like tuple indexing, boolean span choices, string escaping, C string support across compiler versions, and clone costs for large token streams. Tests should cover primitive interpolation output, `Option` omission, wrapper forwarding, token type preservation, and generated code that requires unsuffixed literals via domain-specific types such as `syn::Index`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/quote/to_tokens.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/attr.rs -->
# sources/distributed-fs/ceph-client/rust/syn/attr.rs

## Purpose

This file defines Syn's attribute AST and parsing/printing support for Rust attributes and doc comments.

## Important APIs, types, and functions

`Attribute` stores `#`, `AttrStyle`, bracket tokens, and `Meta`. `Attribute::path`, `parse_args`, `parse_args_with`, `parse_nested_meta`, `parse_outer`, and `parse_inner` are the main APIs. `AttrStyle` distinguishes outer and inner attributes. `Meta` has `Path`, `List`, and `NameValue` variants with `path`, `require_path_only`, `require_list`, and `require_name_value`. `MetaList` stores path, delimiter, and tokens and can parse arguments or nested meta. `FilterAttrs` filters outer/inner attrs for printing.

## Control flow

Outer and inner parsers loop while `#` or `#!` tokens are present, parse bracket contents, and parse `Meta`. `parse_meta_after_path` selects list, name-value, or bare path based on following delimiters or `=`. Name-value parsing preserves old literal-only behavior by first forking and accepting a lone literal as `Expr::Lit`; nested attributes inside attributes are rejected. Printing reconstructs `#`, optional `!`, brackets, paths, delimiters, and values.

## State and persistence behavior

Attributes persist parsed syntax tree state: punctuation tokens and spans, style, path, raw list token streams, delimiters, and expression values. `MetaList::parse_args_with` reparses stored tokens under the close-delimiter span for better errors.

## Dependencies and integration points

It depends on Syn expression, macro delimiter, meta parsing, parse streams, paths, punctuation tokens, `proc_macro2::TokenStream`, and `quote::ToTokens` under printing. It integrates with every Syn item/field/variant parser that stores attributes and with macro crates that parse structured attribute arguments.

## Risks and test signals

Risks include accepting invalid outermost keyword paths, poor error spans for empty or wrong-form attributes, incorrect doc-comment equivalence, nested attribute rejection regressions, arbitrary token preservation in lists, and print/parse round-trip drift. Tests should cover outer/inner attrs, doc comments, `Meta::Path/List/NameValue`, literal and expression name-values, `parse_nested_meta`, delimiter variants, malformed attributes, and printing filters.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/attr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/bigint.rs -->
# sources/distributed-fs/ceph-client/rust/syn/bigint.rs

## Purpose

This helper implements a minimal decimal big integer used by `LitInt` support to expose base-10 digits without depending on a general big integer crate.

## Important APIs, types, and functions

`BigInt` stores decimal digits little-endian in `Vec<u8>`. `new` creates an empty zero value. `to_string` renders digits in normal order while suppressing leading zeroes. `reserve_two_digits` ensures enough capacity for add/multiply by small bases. `AddAssign<u8>` adds an increment less than 16. `MulAssign<u8>` multiplies by a base no greater than 16.

## Control flow

Parsing code elsewhere repeatedly multiplies by the literal base and adds the next digit. Carry propagation walks the digit vector in little-endian order. Rendering reverses digits and starts output at the first nonzero digit, defaulting to `"0"`.

## State and persistence behavior

State is an in-memory vector of decimal digits. It is not persisted beyond the literal conversion operation.

## Dependencies and integration points

It depends only on `std::ops::{AddAssign, MulAssign}`. Syn literal parsing uses it to normalize binary, octal, decimal, or hexadecimal integer literal text into base-10 digit strings.

## Risks and test signals

Risks include carry propagation bugs, incorrect zero rendering, assumptions about increment/base bounds being violated, and inefficient growth for very large literals. Tests should cover huge decimal/hex/binary/octal literals, zero and leading-zero forms, underscore-separated literals via caller logic, and maximum carry chains.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/bigint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/buffer.rs -->
# sources/distributed-fs/ceph-client/rust/syn/buffer.rs

## Purpose

This module implements Syn's stably addressed `TokenBuffer` and cheaply copyable `Cursor`, enabling efficient repeated traversal of token streams during parsing.

## Important APIs, types, and functions

`Entry` encodes groups, idents, punctuation, literals, and end markers. `TokenBuffer::new` and `new2` build buffers from `proc_macro` or `proc_macro2` streams; `begin` returns a cursor. `Cursor` exposes `empty`, `eof`, `ident`, `punct`, `literal`, `lifetime`, `group`, `any_group`, `token_stream`, `token_tree`, `span`, `prev_span`, `skip`, and `scope_delimiter`. Helpers include `same_scope`, `same_buffer`, `cmp_assuming_same_buffer`, and `open_span_of_group`.

## Control flow

`recursive_new` flattens token trees into an entry array. Group entries contain an offset to their matching end marker; end entries contain offsets back to the buffer start and matching group. `Cursor::create` skips end markers for transparent `Delimiter::None` groups unless at scope end. Cursor methods optionally ignore `None` groups, inspect the current entry, clone token values when returning them, and compute rest cursors by pointer arithmetic.

## State and persistence behavior

`TokenBuffer` owns a boxed immutable entry slice. Cursors store raw pointers into that slice plus a scope end pointer and lifetime marker. No parser mutation changes the buffer; parser state is represented by copied cursors.

## Dependencies and integration points

It depends on `proc_macro2` tokens, `DelimSpan`, `Lifetime`, pointer operations, `Ordering`, and `PhantomData`. Syn parse streams and speculative parsing use these cursors for lookahead, stepping, span reporting, and token reconstruction.

## Risks and test signals

This is unsafe and pointer-sensitive. Risks include dangling cursors if lifetimes are bypassed, wrong group offsets, mishandled `Delimiter::None`, lifetime token splitting, ordering across buffers, and incorrect EOF span. Tests should cover nested groups, empty groups, none-delimited groups, lifetimes, span/prev_span at boundaries, cursor comparison, token reconstruction, and fuzzed token streams under Miri if feasible.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/buffer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/classify.rs -->
# sources/distributed-fs/ceph-client/rust/syn/classify.rs

## Purpose

This file classifies Syn expression and type shapes for correct parsing/printing decisions around semicolons, match-arm commas, trailing braces, labels, and ambiguous type paths.

## Important APIs, types, and functions

`requires_semi_to_be_stmt` and `requires_comma_to_be_match_arm` classify expression statement and match arm punctuation. `trailing_unparameterized_path` walks types to determine whether a printed type ends in an unparameterized path. `expr_leading_label` detects whether an expression's first token is a loop/block label. `expr_trailing_brace` determines whether an expression's last token is `}`, recursing into nested expressions and relevant type positions.

## Control flow

The functions are pattern-match walkers over Syn AST enums. They either return immediately for known terminal variants or follow left/right/base/body/type fields until a terminal shape is reached. Helper functions inspect last path segments, parenthesized return types, trait bounds, and verbatim token streams.

## State and persistence behavior

No state is mutated. The module computes boolean classification from immutable AST references.

## Dependencies and integration points

It depends on `Expr` and, under printing/full features, `Type`, `Path`, `PathArguments`, `ReturnType`, `TypeParamBound`, `Punctuated`, `ControlFlow`, and token-stream group inspection. Syn printers use these classifications to decide punctuation and disambiguation.

## Risks and test signals

Risks include missing new `Expr` or `Type` variants, wrong punctuation around macros and brace-delimited expressions, incorrect handling of labels through nested receiver/left expressions, and generic path ambiguity. Tests should cover every expression variant, macro delimiters, chained field/call/index/cast forms, function/trait-object return types, verbatim brace tokens, and compiler parse/pretty-print round trips.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/classify.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/custom_keyword.rs -->
# sources/distributed-fs/ceph-client/rust/syn/custom_keyword.rs

## Purpose

This file implements `custom_keyword!`, allowing downstream parsers to define identifier-like tokens that parse, peek, print, clone, and expose spans like built-in Syn keyword token types.

## Important APIs, types, and functions

`custom_keyword!($ident)` emits a public struct named after the identifier with a `span` field, a constructor function accepting `IntoSpans<Span>`, a `Default` impl, and feature-gated parse, print, clone, and extra trait implementations. `impl_parse_for_custom_keyword!` implements `CustomToken` and `Parse`. `impl_to_tokens_for_custom_keyword!` prints the keyword as an `Ident`. `impl_clone_for_custom_keyword!` makes it `Copy`/`Clone`. `impl_extra_traits_for_custom_keyword!` implements debug, equality, and hash behavior.

## Control flow

Parsing uses `input.step` and checks `cursor.ident()` against `stringify!($ident)`. On match it returns the token with the parsed ident span and advances to `rest`; otherwise it produces an expected-keyword error. Peeking uses the same cursor ident check. Printing constructs a `syn::Ident` with the stored span and appends it to the output stream.

## State and persistence behavior

Each custom keyword token stores only its span. Equality and hash under `extra-traits` ignore span, matching token marker semantics.

## Dependencies and integration points

It depends on Syn private exports (`Span`, `IntoSpans`, `CustomToken`, `Parse`, `ToTokens`, `TokenStreamExt`, trait aliases) and `quote` printing. Downstream Syn parsers use it in `kw` modules for contextual keywords and DSL keys.

## Risks and test signals

Risks include accepting raw identifiers unexpectedly, feature-gated trait differences, constructor name collisions, span loss while printing, and lookahead error message regressions. Tests should cover parse success/failure, `peek`, default construction, printing with span, clone/copy when enabled, extra-trait behavior, and contextual keywords that overlap with ordinary identifiers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/custom_keyword.rs -->
