# File Research: sources/cow-pools/bcachefs-tools/fs/util/thread_with_file_types.h

Purpose: Shared buffer types for thread-with-stdio plumbing.

Key APIs and behavior:
- `struct stdio_buf` contains a spinlock, wait queue, char darray, and `waiting_for_line`.
- `struct stdio_redirect` contains input and output buffers plus a done flag.

Integration:
- Included by `thread_with_file.h` and used by `thread_with_file.c`.
- Depends on `darray.h`.

Risks and invariants:
- Buffer locking/wakeup behavior is implemented externally.
- `done` terminates blocking reads/writes.
