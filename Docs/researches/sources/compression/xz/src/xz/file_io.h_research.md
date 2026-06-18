# Research: sources/compression/xz/src/xz/file_io.h
## sources/compression/xz/src/xz/file_io.h

Purpose: Declares the file I/O buffer type, `file_pair` state object, and public I/O routines for the xz front end.

Important APIs and types: `IO_BUFFER_SIZE` is derived from `BUFSIZ` and rounded to a multiple of eight for sparse detection. `io_buf` aliases bytes, 32-bit words, and 64-bit words safely through a union. `file_pair` stores source/destination names and descriptors, optional directory fd, EOF/flush flags, sparse-output state, and source/destination `stat` snapshots. Public functions cover initialization, abort-pipe signaling, sparse disabling, open/close, read/write, seeking, pread-like reads, and source-position rewind.

Control flow and integration: `main.c` calls `io_init()`. `coder.c` uses open/read/write/close for data transformation. `list.c` uses source open, `io_pread()`, and close for metadata listing. `signals.c` calls `io_write_to_user_abort_pipe()` on POSIX.

State and persistence: The struct fields are the authoritative per-file state passed between `file_io.c`, `coder.c`, and `list.c`. File removal decisions depend on the stored `stat` snapshots and success flag.

Risks: Callers must respect `IO_BUFFER_SIZE` bounds, must not keep `file_pair` beyond the next `io_open_src()` because the implementation uses static storage, and must pass the correct success flag to avoid deleting good sources or retaining bad destinations.

Test signals: Compile on POSIX, Windows/MSVC, and DOS-like configurations; validate struct behavior for stdin/stdout, regular files, sparse paths, and list-mode random access.
