<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec/errors.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec/errors.rs

## Purpose
This file defines small error types used by the kernel `Vec` implementation for operations that intentionally do not allocate or that validate indices.

## Important APIs, Types, and Functions
`PushError<T>(pub T)` is returned by `Vec::push_within_capacity` when a value cannot be appended without reallocating. `RemoveError` is returned by `Vec::remove` on an out-of-bounds index. `InsertError<T>` distinguishes `IndexOutOfBounds(T)` from `OutOfCapacity(T)` for `Vec::insert_within_capacity`, preserving ownership of the rejected element in both cases.

## Control Flow and State
Each error implements `fmt::Debug` without formatting the contained value, avoiding additional trait bounds on `T`. All three convert into kernel `Error` as `EINVAL`. The choice is explicit for capacity errors: a full vector is a caller contract failure for no-allocation insertion, not system-wide `ENOMEM`.

## State and Persistence Behavior
The generic error variants carry rejected elements by value, so failed insertions and pushes do not drop caller-owned data unexpectedly. The error values have no persistent external state.

## Dependencies and Integration Points
The file depends on `kernel::fmt`, `kernel::prelude::*`, and the kernel `Error`/`EINVAL` error model. It is re-exported from `kvec.rs`.

## Risks
The main semantic risk is callers assuming `OutOfCapacity` means memory pressure; conversion to `EINVAL` intentionally communicates that no allocation was attempted. Generic payload ownership must be preserved across all error handling.

## Test Signals
No direct tests live in this file. Usage is exercised through `kvec.rs` examples and tests for `push_within_capacity`, `insert_within_capacity`, and `remove`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/alloc/kvec/errors.rs -->
