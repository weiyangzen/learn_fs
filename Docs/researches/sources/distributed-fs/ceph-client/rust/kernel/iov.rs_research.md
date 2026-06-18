# sources/distributed-fs/ceph-client/rust/kernel/iov.rs

## Purpose
`iov.rs` provides Rust wrappers for Linux `struct iov_iter` sources and destinations. It separates readable and writable iterator directions at the type level and exposes safe copying helpers for kernel buffers and vectors.

## Important APIs, Types, and Functions
`IovIterSource<'data>` wraps an iterator with `data_source == ITER_SOURCE`; `IovIterDest<'data>` wraps `ITER_DEST`. Both provide unsafe `from_raw`, `as_raw`, `len`, `is_empty`, `advance`, and unsafe `revert`. Source adds `copy_from_iter`, `copy_from_iter_vec`, and `copy_from_iter_raw`. Destination adds `copy_to_iter` and `simple_read_from_buffer`.

## Control Flow
`from_raw` asserts the C iterator direction matches the wrapper type before casting. Copy-from operations reserve vector capacity when needed, call `_copy_from_iter`, and set initialized length only for bytes C reports as written. Copy-to calls `_copy_to_iter`. `simple_read_from_buffer` validates nonnegative position, handles EOF, copies from the current offset, and advances `ppos` by bytes written.

## State and Persistence
The wrapper mutates the underlying C iterator's count and position as copy/advance/revert operations occur. It does not own the backing user/kernel memory. The types are intentionally not `Send` because data can be thread-locally mapped.

## Dependencies and Integration Points
It depends on C iov iterator helpers, allocation `Vec` and `Allocator`, `MaybeUninit`, `Opaque`, and VFS read/write iterator callbacks. `simple_read_from_buffer` is useful for pseudo-files exposing static content.

## Risks
`from_raw` is unsafe and direction assertions can panic if C passes the wrong iterator kind. `len()` may overestimate available bytes because user memory faults can terminate copying early. `revert` can underflow logical iterator position if caller passes too many bytes. Destination and source wrappers must not be confused.

## Test Signals
Test source and destination direction assertions, partial copies, vector append initialization, EOF and negative offset handling in `simple_read_from_buffer`, advance/revert bounds, and user-memory fault behavior through integration tests.
