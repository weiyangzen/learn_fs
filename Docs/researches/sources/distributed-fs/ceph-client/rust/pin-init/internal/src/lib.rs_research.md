# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/lib.rs

## Purpose
This is the proc-macro crate entry point for `pin-init-internal`. It exposes macros used by the public `pin-init` crate: field pinning metadata, pinned drop transformation, zeroable derives, and initializer construction.

## Important APIs, Types, And Functions
Proc-macro exports are `#[pin_data]`, `#[pinned_drop]`, `#[derive(Zeroable)]`, `#[derive(MaybeZeroable)]`, `init!`, and `pin_init!`. The file wires each entry point to `pin_data`, `pinned_drop`, `zeroable`, or `init` helper modules through `DiagCtxt::with`.

## Control Flow
Each macro parses input with `syn::parse_macro_input!`, creates a diagnostic context, delegates to the corresponding expansion function, and converts the result back to `proc_macro::TokenStream`. `init!` and `pin_init!` both default the error type to `core::convert::Infallible` and differ by the `pinned` flag passed to `init::expand`.

## State And Persistence
No runtime state is held by this crate entry point. Generated output can define helper types, impls, and initializer closures in the caller crate.

## Dependencies And Integration Points
It depends on Rust proc-macro APIs, `syn`, and local modules. The public `pin-init/src/lib.rs` re-exports these proc macros under the user-facing crate.

## Risks And Edge Cases
The entry point must keep public macro names and defaults synchronized with `pin-init` documentation. Parse failures from `parse_macro_input!` short-circuit before custom diagnostics. Feature gates and fixdep version-string comments are part of the kernel build integration.

## Test Signals
Signals include expansion tests for all exported macros, parse-error diagnostics, default error type behavior, and public re-export compatibility from the main `pin-init` crate.
