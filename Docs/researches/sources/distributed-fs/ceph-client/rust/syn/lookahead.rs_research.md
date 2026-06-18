# Research: sources/distributed-fs/ceph-client/rust/syn/lookahead.rs

## Purpose
`lookahead.rs` implements `Lookahead1`, Syn's helper for parser dispatch based on the next token with accumulated, human-readable error messages. It also defines the sealed `Peek` trait and the pseudo-token `End`.

## Important APIs, Types, And Functions
`Lookahead1<'a>` stores a diagnostic scope `Span`, a `Cursor<'a>`, and a `RefCell<Vec<&'static str>>` of failed token expectations. `new(scope, cursor)` constructs it. `Lookahead1::peek(T)` checks a token type implementing `Peek`; failed comparisons are recorded for later diagnostics. `Lookahead1::error()` formats `unexpected end of input`, `unexpected token`, `expected X`, `expected X or Y`, or `expected one of: ...`. `End` is a custom token whose `peek` succeeds at EOF and whose display placeholder is rewritten to the current closing delimiter.

## Control Flow
Every `peek` delegates to `peek_impl`. If the token matches, it returns true immediately and does not record anything. If not, it appends the token display string. `error()` consumes the lookahead, rewrites the special `)` display based on the cursor's scope delimiter, removes it for delimiter-less scope, and emits an error at the cursor using `error::new_at` unless no comparisons were recorded.

## State And Persistence Behavior
State is transient and diagnostic-only. `RefCell` allows `peek` to take `&self` while appending expectations. Consuming tokens from the original parse stream after constructing `Lookahead1` does not advance this stored cursor, so callers must create a fresh lookahead after changing parse position.

## Dependencies And Integration Points
The module depends on parser cursors, Syn error construction, sealed traits, span conversion, and token traits. `Peek` is sealed so only Syn-controlled token marker functions and `End` can implement it. It is used throughout parser modules, including `item.rs`, `op.rs`, and `meta.rs`, to produce consistent errors for alternative syntax branches.

## Risks
Because failed peek order becomes the error message order, parser branches affect diagnostics. Reusing a lookahead after consuming input can produce stale errors. The `End` display rewrite is delimiter-sensitive; incorrect cursor scope would report the wrong closing delimiter. The `RefCell` design is simple but means repeated failed peeks against the same token can duplicate expected entries.

## Test Signals
Tests should cover zero, one, two, and many expected alternatives; EOF diagnostics; delimiter-specific `End` messages for parentheses, braces, and brackets; stale lookahead behavior expectations; and parser examples that use `peek2(End)` for trailing comma handling.
