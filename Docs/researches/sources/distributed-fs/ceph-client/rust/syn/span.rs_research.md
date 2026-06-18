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
