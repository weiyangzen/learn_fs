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
