# sources/distributed-fs/ceph-client/drivers/android/binder/error.rs

## Purpose

This Rust file defines the Rust Binder error type used for failures that are returned through the Binder protocol in `BINDER_WRITE_READ`, rather than directly as ioctl `errno`. It distinguishes protocol-level reply commands such as dead, frozen, pending-frozen, and failed replies, while optionally retaining the underlying kernel `Error` for extended-error reporting and debugging.

## Important APIs, types, and functions

The main alias is `BinderResult<T = ()> = Result<T, BinderError>`. `BinderError` stores `reply: u32` and `source: Option<Error>`. Constructors are `new_dead()`, `new_frozen()`, and `new_frozen_oneway()`. `is_dead()` recognizes `BR_DEAD_REPLY`. Conversion impls map `kernel::Error`, `BadFdError`, and `AllocError` into `BR_FAILED_REPLY` with an appropriate source (`ENOMEM` for allocation failure). A custom `Debug` impl formats known Binder reply values by name and includes the source error for failed replies.

## Control flow

Code that detects a Binder-level failure constructs or converts into `BinderError`. Callers can return it through `BinderResult`, then higher layers translate `reply` into a `BR_*` item for userspace and can store `source` in extended-error state. Direct dead/frozen constructors have no source errno because the protocol reply is the meaningful result. Generic kernel errors become `BR_FAILED_REPLY`.

## State and persistence behavior

`BinderError` is an owned value with no global state. Its `source` field preserves errno context across Rust call layers until the Binder protocol response and extended error can be produced. No long-term persistence exists.

## Dependencies and integration points

The file depends on `defs.rs` for Binder `BR_*` constants, Rust-for-Linux `Error`, `BadFdError`, allocation errors, and kernel formatting. It integrates with context-manager lookup, transaction delivery, fd handling, allocation failures, and debug logging in the Rust Binder implementation.

## Risks

The main risk is returning the wrong channel of failure. Some failures must be delivered as Binder replies (`BR_DEAD_REPLY`, `BR_FROZEN_REPLY`, `BR_TRANSACTION_PENDING_FROZEN`) rather than ioctl errno; converting them to plain `Error` would break userspace protocol expectations. Conversely, low-level copy or ioctl validation errors may still need direct errno in callers outside this type. Missing source errors reduce extended-error diagnostics.

## Test signals

Tests should cover dead context manager mapping to `BR_DEAD_REPLY`, frozen sync and one-way paths, allocation failure mapping to `BR_FAILED_REPLY` plus `ENOMEM`, bad fd conversion, `is_dead()`, and debug formatting for known and unknown reply values.
