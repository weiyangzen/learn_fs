# sources/distributed-fs/ceph-client/io_uring/openclose.c

Purpose: implements io_uring open, close, fixed-file install, and pipe operations. It translates SQE fields into VFS open/close/pipe actions while respecting fixed-file tables and async-only paths.

Important APIs/types/functions: `struct io_open`, `struct io_close`, `struct io_fixed_install`, and `struct io_pipe` are the per-op command payloads. Entry points include `io_openat_prep()`, `io_openat2_prep()`, `io_openat2()`, `io_close_prep()`, `io_close()`, `io_install_fixed_fd_prep()`, `io_install_fixed_fd()`, `io_pipe_prep()`, and `io_pipe()`. `__io_close_fixed()` is exported to other io_uring resource paths.

Control flow: prep validates unused SQE fields, copies paths or `open_how`, captures rlimits, and marks cleanup or forced async where required. Open uses `build_open_flags()`, optional `LOOKUP_CACHED`/`O_NONBLOCK` for nonblocking issue, VFS `do_file_open()`, then either installs a normal fd or inserts into the fixed file table. Close removes a fixed slot or safely extracts an fd under `files->file_lock`, punting flush-capable files to async. Pipe creates both files, then installs them in normal fd space or adjacent/allocated fixed slots.

State and persistence: state changes are fd table entries, io_uring fixed-file table slots, file references, pipe file objects, and delayed filename storage. No disk state is kept directly, but open/close may trigger filesystem side effects.

Dependencies/integration: integrates with VFS namei/open helpers, file descriptor allocation, pipe creation, fixed-file helpers in `filetable`/`rsrc`, BPF filter population for open, and io_uring completion flags.

Risks/test signals: important risks are cleanup of delayed names on retries, fixed-slot rollback on pipe copy-to-user failure, `O_CLOEXEC` rejection for fixed opens/pipes, and avoiding recursive registration of io_uring fds. Test with normal and fixed open/close, open retry with `RESOLVE_CACHED`, close of flush files, fixed fd install credentials, pipe fixed-slot allocation, and faulted user fd arrays.
