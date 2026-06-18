# sources/distributed-fs/ceph-client/include/linux/file.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/file.h` declares VFS file allocation, descriptor acquisition, descriptor installation, and cleanup-helper APIs. The source was read as a complete 255-line file for this report.

## Important APIs, Types, and Functions

Important exports include `fput`, `alloc_file_pseudo`, `alloc_file_pseudo_noaccount`, `alloc_file_clone`, `struct fd`, `FDPUT_FPUT`, `FDPUT_POS_UNLOCK`, `fd_file`, `fd_empty`, `EMPTY_FD`, `BORROWED_FD`, `CLONED_FD`, `fdput`, `fget`, `fget_raw`, `fget_task`, `fget_task_next`, `fdget`, `fdget_raw`, `fdget_pos`, `fdput_pos`, cleanup classes `fd`, `fd_raw`, and `fd_pos`, `f_dupfd`, `replace_fd`, close-on-exec helpers, unused-fd helpers, `take_fd`, `fd_install`, `receive_fd`, `receive_fd_replace`, delayed fput helpers, `struct fd_prepare`, `FD_PREPARE`, `fd_publish`, and `FD_ADD`.

## Control Flow

Callers acquire `struct file` references through fget/fdget helpers, use `fd_file()` to access the pointer, and release via `fdput()` or `fdput_pos()` depending on whether the low-bit flags request `fput()` and/or position unlock. Allocation flows reserve an fd, allocate or receive a file, install with `fd_install()`, and publish/take ownership. `fd_prepare` and cleanup classes make error paths automatically release partially acquired fds/files.

## State and Persistence Behavior

The header does not own storage, but its `struct fd` encodes file pointer plus flags in low pointer bits. Descriptor state lives in `files_struct`; file state lives in `struct file`; delayed fput state is handled by VFS.

## Dependencies and Integration Points

It depends on cleanup helpers, errno, error pointers, and VFS types. It integrates with fdtable internals, open/receive-fd paths, SCM_RIGHTS, pseudo files, mount/dentry/inode file creation, close-on-exec, and positional file locking.

## Risks and Edge Cases

Low-bit pointer tagging requires `struct file` alignment. Forgetting `fdput_pos()` after `fdget_pos()` can leave position locks held. Publishing must transfer ownership exactly once; failure paths must not leak unused fds or double `fput()` files.

## Test Signals

Open/close/dup/SCM_RIGHTS tests, fd leak tests under fault injection, lockdep for `f_pos` locking, cleanup-class build tests, and stress tests around `FD_ADD` and `fd_prepare` failure paths.
