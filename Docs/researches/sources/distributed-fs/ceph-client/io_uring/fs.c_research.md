# sources/distributed-fs/ceph-client/io_uring/fs.c

## Purpose
`fs.c` implements io_uring filesystem namespace operations: rename, unlink/rmdir, mkdir, symlink, and hardlink.

## Important APIs, Types, And Functions
- Per-op command structs store dirfds, delayed filenames, flags, mode, and a placeholder file pointer.
- Prep handlers: `io_renameat_prep`, `io_unlinkat_prep`, `io_mkdirat_prep`, `io_symlinkat_prep`, and `io_linkat_prep`.
- Issue handlers call `filename_renameat2`, `filename_unlinkat`/`filename_rmdir`, `filename_mkdirat`, `filename_symlinkat`, and `filename_linkat`.
- Cleanup handlers dismiss delayed filenames for operations that allocated them.

## Control Flow
Prep rejects unsupported SQE fields and fixed-file mode, reads dirfds/path pointers/flags, resolves paths through delayed filename helpers, marks the request for cleanup, and forces async execution. Issue handlers complete delayed filenames with scope helpers, call the corresponding VFS operation, clear cleanup state, set result, and complete.

## State And Persistence
Request-local state stores delayed filename objects until issue or cleanup. Persistent effects are filesystem namespace changes.

## Dependencies And Integration Points
The file depends on VFS internal filename helpers from `../fs/internal.h`, io_uring command storage, request cleanup flags, and async worker execution. `fs.h` exposes the handlers to the opcode table.

## Risks And Edge Cases
Delayed filename ownership is the main lifetime risk: every successful first allocation must be dismissed on second allocation failure or cleanup. These operations force async because namespace modifications can block. Fixed-file mode is rejected because path operations use dirfds and userspace paths.

## Test Signals
Tests should cover success and failure paths for rename/unlink/rmdir/mkdir/symlink/link, invalid flags, bad user pointers, cleanup after prep failure, cancellation before issue, and parity with syscalls.
