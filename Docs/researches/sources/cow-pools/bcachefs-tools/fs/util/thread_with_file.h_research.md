# File Research: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file.h

Purpose: Public API for fd-backed kernel threads and stdio redirection.

Key APIs and behavior:
- Defines low-level `struct thread_with_file` with task, return value, and done flag.
- Defines `thread_with_stdio_ops` for exit, main function, and ioctl hook.
- Defines `struct thread_with_stdio` combining thread state, stdio buffers, and ops.
- Declares run/init/read/readline/write/printf helpers.

Integration:
- Implemented by `thread_with_file.c`.
- Uses `thread_with_file_types.h`.

Risks and invariants:
- Low-level users with custom file operations must call `bch2_thread_with_file_exit()` from release.
- Closing the fd is the shutdown signal.
