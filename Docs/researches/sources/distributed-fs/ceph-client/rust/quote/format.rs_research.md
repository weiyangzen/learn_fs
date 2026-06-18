# sources/distributed-fs/ceph-client/rust/quote/format.rs

## Purpose

This file implements `format_ident!`, a formatting macro for constructing `proc_macro2::Ident` values while preserving useful span hygiene from identifier fragments.

## Important APIs, types, and functions

`format_ident!` forwards to `format_ident_impl!` with an initially absent span. `format_ident_impl!` parses positional args, named args, and a special `span = ...` override, wraps arguments in `IdentFragmentAdapter`, accumulates the first fragment span with `Option::or`, runs `format!`, and calls `__private::mk_ident`.

## Control flow

Macro expansion is a recursive state machine. Final state formats the string and constructs the identifier. Span arguments override the accumulated span. Non-span arguments are adapted so their `IdentFragment` implementation controls text and optional span inheritance.

## State and persistence behavior

Macro state is compile-time token state containing the pending span expression and accumulated format invocation. Runtime persistence is just the constructed `Ident`.

## Dependencies and integration points

It depends on `IdentFragment`, `runtime::IdentFragmentAdapter`, `runtime::mk_ident`, `alloc::format`, and `proc_macro2::Span`. `quote/lib.rs` exports the macro and `ident_fragment.rs` defines the fragment trait.

## Risks and test signals

Risks include accepting invalid identifier text only to panic at construction, wrong span precedence, raw identifier prefix handling, and unsupported format traits. Tests should cover positional/named arguments, `span` override, first-identifier span inheritance, raw identifiers, numeric formatting modes, and invalid formatted identifiers.
