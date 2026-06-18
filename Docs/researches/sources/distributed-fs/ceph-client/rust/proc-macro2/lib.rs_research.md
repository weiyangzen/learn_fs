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
