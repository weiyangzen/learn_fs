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
