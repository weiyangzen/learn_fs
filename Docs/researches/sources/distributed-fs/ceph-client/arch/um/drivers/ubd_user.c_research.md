<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/ubd_user.c

Purpose: starts and supports the host-side UBD I/O helper thread used by `ubd_kern.c`.

Important APIs/types/functions: static `kernel_pollfd` tracks the helper pipe. Public functions are `start_io_thread()`, `ubd_read_poll()`, and `ubd_write_poll()`. External `kernel_fd` is set to the helper side of the pipe.

Control flow: `start_io_thread()` creates a nonblocking pipe, assigns one end to `kernel_fd` and the other to the kernel side, configures poll state, starts `io_thread()` with `os_run_helper_thread()`, and returns the kernel-side FD. Poll helpers switch events between `POLLIN` and `POLLOUT` and call `poll()`.

State and persistence: runtime state is the pipe FD and pollfd. Persistent disk data is written by `io_thread()` in `ubd_kern.c`, not here.

Dependencies and integration points: depends on UML `os_pipe`, `os_set_fd_block`, `os_run_helper_thread`, host `poll`, and `io_thread()` symbol from `ubd_kern.c`.

Risks: failure paths must close both pipe ends and reset `kernel_fd`. The helper and kernel communicate raw pointers, so the thread must run in the same address space model UML expects.

Test signals: successful helper startup, nonblocking flags, read/write poll wakeups, helper thread start failure, and UBD fallback logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd_user.c -->
