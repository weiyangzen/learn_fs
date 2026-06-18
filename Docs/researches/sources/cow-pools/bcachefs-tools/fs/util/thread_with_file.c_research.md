# File Research: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file.c

Purpose: Runs a kernel thread attached to an anonymous file descriptor, with optional stdio-style redirection.

Key APIs and behavior:
- `bch2_run_thread_with_file()` creates a kthread, creates an anon inode file, installs an fd, and starts the task.
- `bch2_thread_with_file_exit()` stops the task and drops the task reference.
- Stdio mode implements read, write, poll, flush, release, and ioctl file operations.
- Input/output buffers are darrays protected by spinlocks and wait queues.
- Provides blocking/nonblocking writes, read, readline with timeout, printf/vprintf output, and stdout-only mode.

Integration:
- Implements `thread_with_file.h`.
- Guarded by `NO_BCACHEFS_FS`.
- Uses anon inodes, kthreads, file descriptors, fault-in/copy nofault helpers, wait queues, and darray.

Risks and invariants:
- Release marks stdio done, stops the kthread, frees buffers, then calls caller exit op.
- Nonblocking output writes are atomic by message.
- Readline can grow the destination darray and tracks `waiting_for_line` to avoid chopping lines.
