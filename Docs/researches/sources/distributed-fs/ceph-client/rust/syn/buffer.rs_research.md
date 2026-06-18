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
