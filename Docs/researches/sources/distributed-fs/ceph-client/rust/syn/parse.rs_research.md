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
