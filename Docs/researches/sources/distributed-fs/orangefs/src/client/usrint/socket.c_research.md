## sources/distributed-fs/orangefs/src/client/usrint/socket.c

Purpose: Interposes socket, pipe, and related syscalls so non-PVFS descriptors participate in OrangeFS usrint's virtual descriptor table and can be routed through the same `fsops` abstraction.

Important APIs, types, and functions: Wraps `socket`, `accept`, `bind`, `connect`, `getpeername`, `getsockname`, `getsockopt`, `setsockopt`, `ioctl`, `listen`, `recv`, `recvfrom`, `recvmsg`, `send`, `sendto`, `sendmsg`, `shutdown`, `socketpair`, and `pipe`. Key helpers are `pvfs_alloc_descriptor`, `pvfs_find_descriptor`, `pvfs_free_descriptor`, `glibc_ops`, and descriptor `mode` bits.

Control flow: Created sockets/pipes are real libc/kernel descriptors wrapped in `pvfs_descriptor`s with `S_IFSOCK` mode. Most operations look up the virtual descriptor, reject missing entries with `EBADF`, reject non-sockets with `ENOTSOCK`, then call the underlying `pd->fsops` function on `pd->true_fd`.

State and persistence: Mutates the process descriptor table maintained by usrint. No durable storage; wrappers track fd identity and mode for the lifetime of the descriptor.

Dependencies and integration points: Depends on `usrint.h`, `posix-ops.h`, `posix-pvfs.h`, and `openfile-util.h`. It integrates libc sockets/pipes with the usrint descriptor layer used by POSIX wrappers and stdio.

Risks and test signals: `socket` calls `syscall(SYS_socketcall, domain, type, protocol)`, which does not match modern direct `socket` syscall conventions and is architecture-sensitive. `accept` returns the real fd instead of `pd->fd`, and `socketpair`/`pipe` assign `sv[]`/`filedes[]` to `true_fd`, risking descriptor-namespace confusion. `ioctl` passes a `va_list` to an `ioctl` function pointer that may expect a raw third argument. Test basic TCP/UDP sockets, accept fd usability through usrint, socketpair/pipe read/write/close, ioctl on sockets, non-socket error paths, and 64-bit/current Linux syscall behavior.
