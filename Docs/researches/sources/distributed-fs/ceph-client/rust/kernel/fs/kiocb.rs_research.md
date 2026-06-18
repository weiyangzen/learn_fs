# sources/distributed-fs/ceph-client/rust/kernel/fs/kiocb.rs

## Purpose
`fs/kiocb.rs` wraps `struct kiocb` for Rust file operation callbacks. It currently exposes file-private data and the file position carried by the kernel I/O callback.

## Important APIs, Types, and Functions
`Kiocb<'a, T>` stores a non-null raw `kiocb` pointer and a lifetime marker for private data type `T`. `T` must implement `ForeignOwnable`. `from_raw` constructs the wrapper, `as_raw` returns the C pointer, `file()` borrows `ki_filp->private_data` as `T::Borrowed`, `ki_pos()` reads the current offset, and `ki_pos_mut()` exposes mutable access to the position.

## Control Flow
Callback glue calls unsafe `from_raw` once the kernel passes a valid `kiocb`. Methods then directly read the embedded `ki_filp` and `ki_pos` fields. Private data borrowing is delegated to the `ForeignOwnable` contract so wrappers can recover Rust driver/filesystem state stored in C.

## State and Persistence
The wrapper owns no state. It borrows the callback-local `kiocb`, whose position and file pointer are owned by VFS. Mutating `ki_pos` updates the live callback object.

## Dependencies and Integration Points
It integrates with VFS async/sync file operation callbacks and Rust-owned private data stored as C `void *`. It depends on `kernel::types::ForeignOwnable`.

## Risks
`from_raw` is unsafe because a null or wrong-type `kiocb` would make later field access invalid. `file()` assumes private data has type `T`; a mismatch can violate aliasing or lifetime invariants. `ki_pos_mut()` requires exclusive wrapper access to avoid concurrent offset mutation.

## Test Signals
File operation tests should verify correct private-data recovery, read/write callback position updates, invalid private-data assumptions caught by review, and offset behavior across repeated operations.
