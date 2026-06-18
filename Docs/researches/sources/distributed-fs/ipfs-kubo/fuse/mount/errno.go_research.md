<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/errno.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/errno.go

## Purpose

This file normalizes read/write errors into FUSE errno values, with special treatment for cancelled contexts.

## Important APIs, Types, and Functions

`ReadErrno` maps `context.Canceled` and `context.DeadlineExceeded` to `syscall.EINTR`; all other errors go through `fs.ToErrno`.

## Control Flow, State, and Integration

Read handlers in readonly and writable file handles call this after DAG reader operations. It is specifically tied to kernel `FUSE_INTERRUPT` behavior when a userspace process is killed during a blocking syscall.

## Dependencies, Risks, and Test Signals

Dependencies are `context`, `syscall`, and go-fuse. The risk is returning opaque errno values on cancellation, making killed reads appear as unrelated I/O errors or hang symptoms. `TestReadCancellationUnblocks` in readonly tests verifies the EINTR path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/errno.go -->
