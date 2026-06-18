# sources/distributed-fs/ceph-client/rust/proc-macro2/marker.rs

## Purpose

This module defines the marker embedded in facade token types to give them the same auto-trait behavior expected for proc-macro-like objects.

## Important APIs, types, and functions

`ProcMacroAutoTraits` is a zero-sized tuple struct around `PhantomData<Rc<()>>`. `MARKER` is the singleton value used by facade structs. The type manually implements `UnwindSafe` and `RefUnwindSafe`, while the `Rc` phantom prevents unwanted `Send`/`Sync` auto traits. Under semver-exempt fallback/super-unstable configs it can derive equality.

## Control flow

There is no runtime control flow beyond construction of the constant marker.

## State and persistence behavior

No persistent state is stored. The marker influences compile-time auto-trait derivation for token wrapper types.

## Dependencies and integration points

It uses `alloc::rc::Rc`, `core::marker::PhantomData`, and panic-safety marker traits. `lib.rs` imports `MARKER` into `TokenStream`, `LexError`, `Span`, `Ident`, and `Literal`.

## Risks and test signals

Risks are trait-surface regressions: accidentally making public token types `Send` or `Sync`, or losing unwind-safety behavior. Compile-time trait assertion tests are the best signal, alongside downstream crates that rely on `proc_macro2` tokens remaining thread-local-like.
