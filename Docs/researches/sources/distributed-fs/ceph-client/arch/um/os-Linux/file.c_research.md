# sources/distributed-fs/ceph-client/arch/um/os-Linux/file.c

## Purpose
Wraps host Linux file, socket, fd-passing, polling, fallocate, and shared-memory syscalls behind UML's `os_*` API with consistent negative-errno returns.

## Important APIs, Types, and Functions
Provides stat/access/open/close/read/write/pread/pwrite/sync/seek, file type/mode/size/modtime, FD flags and async SIGIO setup, Unix socket connect/create/shutdown/accept, `os_pipe()`, `os_rcv_fd_msg()`, `os_sendmsg_fds()`, device major/minor helpers, fallocate punch/zero, eventfd, `os_poll()`, and shared `mmap`/`mremap` helpers.

## Control Flow, State, and Persistence
No global state except host file descriptors managed by callers. Functions convert host errors to `-errno`; FD-passing uses ancillary `SCM_RIGHTS` data and fixed maximum receive/send counts.

## Dependencies and Integration Points
Heavily used by time-travel external sockets, SKAS FD passing, block/hostfs/console devices, temp memory files, and generic host wrappers. It bridges kernel code to libc/syscall behavior.

## Risks and Test Signals
Risks include partial I/O not retried, fd leaks on error, insufficient `MAX_RCV_FDS`, `os_poll()` fixed two-FD limit, async signal ownership issues, and shared-memory remap failures. Test fd passing, time-travel shared memory, host file-backed block devices, SIGIO setup, and fallocate support.
