# sources/distributed-fs/ceph-client/rust/helpers/err.c

## Purpose
Exposes Linux encoded error-pointer helpers to Rust.

## APIs, Types, and Functions
Exports wrappers for `ERR_PTR()`, `IS_ERR()`, and `PTR_ERR()`.

## Control Flow, State, and Persistence
No local state; helpers encode/decode errors in pointer values according to kernel conventions.

## Dependencies and Integration
Depends on `linux/err.h` and Rust wrappers converting C pointer-return APIs into `Result`.

## Risks and Test Signals
Risks include treating valid low-address pointers as errors, losing `__force` semantics, and accepting null separately from error pointers. Test signals are conversion tests for common errno values and raw pointer API wrappers.
