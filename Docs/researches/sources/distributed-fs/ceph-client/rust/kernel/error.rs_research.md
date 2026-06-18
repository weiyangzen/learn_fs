# sources/distributed-fs/ceph-client/rust/kernel/error.rs

## Purpose
`error.rs` is the Rust kernel error bridge. It models negative Linux `errno` values as a nonzero, range-checked `Error`, exposes common error constants through `error::code`, defines the crate-wide `Result` alias, and provides helpers for converting C integer returns, error pointers, and Rust `Result` values at FFI boundaries.

## Important APIs, Types, and Functions
The `code` module declares constants such as `EINVAL`, `ENOMEM`, `EIOCBQUEUED`, and NFS-specific errors by validating C binding errno values at compile time. `Error(NonZeroI32)` exposes `from_errno`, `to_errno`, `to_ptr`, `name`, and, under `CONFIG_BLOCK`, `to_blk_status`. `to_result()` maps negative C return codes to `Err(Error)`. `from_err_ptr()` handles `ERR_PTR`-encoded pointers while preserving `NULL` as success. `from_result()` lets `extern "C"` callbacks return integer status from Rust closures. `VTABLE_DEFAULT_ERROR` is a shared diagnostic string for generated default vtable methods.

## Control Flow
Error construction runs through `try_from_errno`; invalid values log a warning and become `EINVAL`. C-call wrappers use `to_result` immediately after an unsafe binding call, so normal `?` propagation works. Error-pointer handling calls `IS_ERR`, then `PTR_ERR`, and relies on kernel invariants that encoded pointer errors are in `MAX_ERRNO` range. `from_result` executes a closure, returns the successful value unchanged, or converts the error's errno into a narrow integer compatible with C callback ABIs.

## State and Persistence
There is no persistent state. `Error` is a copyable value. Error names are retrieved from static C kernel tables in non-test builds; `testlib` disables that dependency and always returns `None`.

## Dependencies and Integration Points
This file integrates with C errno bindings, kernel error-pointer macros, block status conversion, `errname`, allocator/layout/int/UTF-8/formatting errors, and the rest of the Rust kernel crate through the `Result` alias. Almost every higher-level wrapper in this subset depends on `Error`, `Result`, `to_result`, or `from_result`.

## Risks
The range invariant is central: unsafe construction with an out-of-range errno would break `ERR_PTR` and integer conversion assumptions. `from_result` assumes all kernel errno values fit in `i16`, matching `MAX_ERRNO`. `from_err_ptr` intentionally treats `NULL` as non-error; callers of APIs where `NULL` is failure must add their own check.

## Test Signals
Useful tests cover every conversion path: valid and invalid errno construction, debug output with and without names, `to_result` success and failure, `from_err_ptr` for `ERR_PTR`, `NULL`, and normal pointers, and `from_result` on successful and failing closures.
