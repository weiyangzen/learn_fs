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
