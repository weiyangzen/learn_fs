# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/diagnostics.rs

## Purpose
This file provides a small diagnostics accumulator for the `pin-init-internal` proc-macro crate. It lets macro expansion collect one or more `syn::Error` compile errors before returning a token stream.

## Important APIs, Types, And Functions
`DiagCtxt(TokenStream)` stores accumulated compile-error tokens. `ErrorGuaranteed` is an unconstructable marker returned after recording an error. `DiagCtxt::error(span, msg)` appends a `syn::Error::into_compile_error()`. `DiagCtxt::with(fun)` runs a macro expansion closure and combines generated output with accumulated diagnostics, or returns only diagnostics on fatal error.

## Control Flow
Macro entry points call `DiagCtxt::with`. Helper code reports recoverable errors into the context and may return `Err(ErrorGuaranteed)` for fatal expansion. On success, accumulated compile errors are appended to the normal stream; on fatal error, only diagnostics are emitted.

## State And Persistence
State is transient per macro invocation. There is no global diagnostic state.

## Dependencies And Integration Points
It depends on `proc_macro2::TokenStream`, `syn::Error`, and `Spanned`. All internal macro modules use it for consistent compile-error emission.

## Risks And Edge Cases
Appending errors to otherwise generated output can produce multiple diagnostics but may also trigger follow-on type errors if the partial expansion is not robust. Fatal errors must be returned when continuing would emit invalid code.

## Test Signals
Trybuild tests should validate multiple diagnostics from one macro invocation, fatal-only diagnostics, span placement, and absence of proc-macro panics for user errors.
