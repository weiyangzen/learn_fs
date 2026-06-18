# sources/distributed-fs/ceph-client/tools/include/nolibc/dirent.h

## Purpose
Implements a tiny directory-iteration interface on top of Linux `getdents64` for nolibc programs.

## APIs, Types, and Functions
Defines `struct dirent`, opaque `DIR` carrying a file descriptor plus one `linux_dirent64`, and functions `fdopendir`, `opendir`, `closedir`, and `readdir_r`.

## Control Flow, State, and Persistence
`opendir()` opens a directory, `fdopendir()` allocates a DIR wrapper, `readdir_r()` issues one `getdents64` call into the embedded buffer and copies inode, offset, reclen, type, and name into the caller's `dirent`, and `closedir()` closes the fd and frees the wrapper. Persistent state is the open file descriptor and DIR allocation.

## Dependencies and Integration
Depends on `fcntl.h`, `stdlib.h`, `string.h`, `sys.h`, and `types.h`, especially `struct linux_dirent64`. It integrates with filesystem-walking nolibc tools that only need simple one-entry-at-a-time iteration.

## Risks and Test Signals
Risks include the intentionally limited single-record buffer, `readdir_r` legacy semantics, long names bounded by the embedded kernel record, and fd ownership surprises with `fdopendir`. Test signals are empty/nonempty directory iteration, long filename handling, fd leak checks, error propagation from `getdents64`, and iteration after close.
