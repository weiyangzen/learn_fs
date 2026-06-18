# sources/distributed-fs/ceph-client/include/uapi/linux/un.h

Purpose: Defines the AF_UNIX socket address structure and a UNIX-specific ioctl.

Important APIs/types/functions: `UNIX_PATH_MAX` is 108. `struct sockaddr_un` contains `sun_family` and `sun_path`. `SIOCUNIXFILE` is a protocol-private ioctl to open a socket file with `O_PATH`.

Control flow: Userspace passes `sockaddr_un` to bind/connect/sendto or receives it from getsockname/getpeername. The ioctl is issued on AF_UNIX sockets for file access semantics provided by the kernel.

State and persistence behavior: Socket address binding is runtime socket/VFS state; pathname sockets may create filesystem entries outside the header's control.

Dependencies and integration points: Includes `linux/socket.h`; integrates with AF_UNIX sockets, VFS pathname sockets, abstract namespace sockets, and socket ioctls.

Risks: `sun_path` may not be NUL-terminated when length-bound, and abstract names begin with NUL. Callers must calculate sockaddr lengths carefully.

Test signals: Bind/connect pathname and abstract sockets, check length handling at 108 bytes, ioctl behavior, and compat with libc `sockaddr_un`.
