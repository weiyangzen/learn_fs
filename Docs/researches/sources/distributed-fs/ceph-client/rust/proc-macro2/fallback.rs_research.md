# sources/distributed-fs/ceph-client/rust/proc-macro2/fallback.rs

## Purpose
`fallback.rs` implements proc-macro2's compiler-independent token model. It provides fallback `TokenStream`, `Group`, `Ident`, `Literal`, `Span`, parsing/printing, source-location support, and conversions used when real `proc_macro` is unavailable or forced off.

## Important APIs, Types, And Functions
Top-level controls are `force()` and `unforce()`. Core types are `TokenStream`, `LexError`, `TokenStreamBuilder`, `Span`, `Group`, `Ident`, and `Literal`. Source-location support includes thread-local `SOURCE_MAP`, `FileInfo`, `SourceMap`, `lines_offsets`, and `invalidate_current_thread_spans`. Utility functions include `get_cursor`, `push_token_from_proc_macro`, identifier validators, `escape_utf8`, and feature-gated `FromStr2` for panic-safe compiler parsing.

## Control Flow
`TokenStream::from_str_checked` creates a parser cursor, strips a byte-order mark, and delegates token parsing. Token streams use reference-counted vectors and builders; extending a stream normalizes negative literals into `-` plus a positive literal token. `Display` prints tokens with spacing controlled by punct jointness. `Drop` walks nested fallback groups iteratively to avoid recursive stack overflow. Span-location parsing registers each source string in a thread-local source map and assigns monotonically increasing 32-bit character offsets; span methods map offsets to line/column, byte ranges, file labels, source text, joins, and delimiter endpoints.

## State And Persistence
Fallback token streams persist token vectors and spans. Under `span_locations`, each thread keeps a source map of parsed strings until invalidated, with lazy char-index-to-byte-offset caches per file. `force()` and `unforce()` affect global proc-macro2 detection state through `detection.rs`.

## Dependencies And Integration Points
It depends on internal parser cursors, `RcVec`, public token enums, `Delimiter`, `Spacing`, optional `LineColumn`, `alloc::BTreeMap`, and optional real `proc_macro` parsing. It is the core fallback for all proc-macro2 users outside compiler proc-macro contexts.

## Risks And Edge Cases
Span offsets are 32-bit and can wrap for very large same-thread parse workloads; `extra::invalidate_current_thread_spans` is the mitigation. Source-map lookups assert that spans are valid and within one file. Identifier validation is ASCII-only here, so behavior differs from full Rust Unicode identifiers. `Literal::from_str_checked` handles negative literals specially and escapes NULs carefully to avoid octal ambiguity. Compiler conversion uses fallback validation first because rustc can panic on invalid token streams.

## Test Signals
High-value tests include parsing and displaying nested token streams, nonrecursive drop of deeply nested groups, negative literal normalization, span line/column/source-text lookup, source-map invalidation, identifier and raw identifier validation, literal constructors for strings/bytes/C strings/numbers, BOM stripping, invalid token errors, and compiler conversion panic handling.
