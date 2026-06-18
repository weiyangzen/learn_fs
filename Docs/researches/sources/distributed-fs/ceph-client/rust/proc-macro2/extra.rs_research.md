# sources/distributed-fs/ceph-client/rust/proc-macro2/extra.rs

## Purpose
`extra.rs` provides proc-macro2 APIs that do not directly correspond to stable `proc_macro` APIs. In this subset it exposes span invalidation for large parsing workloads and a compact delimiter-span wrapper.

## Important APIs, Types, And Functions
Under `span_locations`, `invalidate_current_thread_spans()` clears current-thread fallback span source maps. `DelimSpan` stores either compiler spans (`join`, `open`, `close`) or a fallback span. Methods `new`, `join`, `open`, and `close` return public `Span` wrappers. `Debug` formats the joined span.

## Control Flow
`DelimSpan::new` inspects an internal `imp::Group` and captures compiler open/close spans when wrapping real proc_macro groups; otherwise it stores a fallback group span. Accessors convert stored internal spans back into public `Span`, using first/last byte for fallback open/close spans.

## State And Persistence
`DelimSpan` is a small copyable value. Span invalidation mutates thread-local fallback state in `fallback.rs`; it does not affect other threads.

## Dependencies And Integration Points
It depends on internal `fallback`, `imp`, marker auto-trait machinery, and `Span`. The public API is useful to callers needing delimiter-level spans and to workloads parsing more than 4 GiB of source per thread.

## Risks And Edge Cases
Invalidating spans makes older spans on that thread invalid or incorrect, so callers must not keep using them. `invalidate_current_thread_spans()` panics or is unavailable in proc-macro contexts. Fallback open/close spans approximate delimiters with first/last bytes of the group span.

## Test Signals
Tests should cover compiler-backed and fallback `DelimSpan`, open/close/join values, debug formatting, span invalidation after large parse simulations, and panic behavior when invalidation is called from an unsupported context.
