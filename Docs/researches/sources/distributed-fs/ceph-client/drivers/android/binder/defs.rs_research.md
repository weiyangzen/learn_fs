# sources/distributed-fs/ceph-client/drivers/android/binder/defs.rs

## Purpose

This Rust file centralizes Rust Binder access to Binder UAPI constants and C-layout UAPI structs. It strips long generated UAPI prefixes into local `pub(crate)` constants, re-exports Binder object type constants, and wraps UAPI structs in transparent `MaybeUninit` newtypes that preserve padding bytes while implementing `FromBytes` and `AsBytes` for safe byte copying.

## Important APIs, types, and functions

The `pub_no_prefix!` macro creates local constants for Binder return protocol values (`BR_TRANSACTION`, `BR_REPLY`, `BR_DEAD_REPLY`, `BR_FROZEN_REPLY`, `BR_TRANSACTION_PENDING_FROZEN`, and others), command protocol values (`BC_TRANSACTION`, `BC_REPLY`, refcount commands, looper commands, death/freeze commands), flat binder flags, and transaction flags.

The `decl_wrapper!` macro defines transparent wrappers for UAPI structs including `BinderNodeDebugInfo`, `BinderNodeInfoForRef`, `FlatBinderObject`, `BinderFdObject`, `BinderFdArrayObject`, `BinderObjectHeader`, `BinderBufferObject`, `BinderTransactionData`, `BinderTransactionDataSecctx`, `BinderTransactionDataSg`, `BinderWriteRead`, `BinderVersion`, freezer structs, `BinderHandleCookie`, and `ExtendedError`.

Helper methods are `BinderVersion::current()`, `BinderTransactionData::with_buffers_size()`, `BinderTransactionDataSecctx::tr_data()`, and `ExtendedError::new()`.

## Control flow

Runtime control flow is minimal. Wrapper defaults zero all bytes including padding. `Deref` and `DerefMut` expose the initialized inner UAPI struct while retaining `MaybeUninit` storage to avoid accidentally fabricating or dropping padding during byte-level copies. `BinderTransactionData::with_buffers_size()` constructs the scatter-gather variant around an existing transaction payload. `BinderTransactionDataSecctx::tr_data()` transmutes the embedded UAPI transaction field into the Rust wrapper view.

## State and persistence behavior

There is no mutable global state. Constants are compile-time aliases and wrappers are per-value byte containers. The key persistence behavior is preserving UAPI padding bytes during read/write of structures crossing the userspace ABI, which matters for exact ABI compatibility and avoiding uninitialized-byte exposure.

## Dependencies and integration points

The file depends on `kernel::uapi`, Binder UAPI generated bindings, `MaybeUninit`, `Deref`, `DerefMut`, and Rust-for-Linux `AsBytes`/`FromBytes`. Other Rust Binder modules import this file for protocol constants, object types, transaction wrappers, version reporting, and extended-error construction.

## Risks

The risks are ABI drift and invalid wrapper assumptions. `decl_wrapper!` marks each wrapper as `FromBytes` and `AsBytes`; this is only sound for C UAPI structs whose initialized byte patterns are acceptable and whose padding is intentionally preserved. If a UAPI struct gains stricter validity constraints, the unsafe impl assumptions need review. Prefix-stripped constants must stay in sync with generated `uapi` names. `tr_data()` relies on transparent layout compatibility between the UAPI field and wrapper.

## Test signals

Build failures against changed UAPI names are an immediate signal. Runtime tests should verify `BINDER_VERSION`, `BINDER_WRITE_READ`, SG transaction wrapping, security-context transaction wrapping, extended-error reporting, and byte-for-byte ABI size/alignment checks against the C Binder structs.
