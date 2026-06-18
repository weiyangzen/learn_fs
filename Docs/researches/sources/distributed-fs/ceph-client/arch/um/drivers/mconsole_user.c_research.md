<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_user.c

Purpose: implements host/user-side management-console protocol parsing, reply sending, notification sending, and socket unlinking for UML.

Important APIs/types/functions: `commands[]` maps command prefixes to handlers and context. Public functions are `mconsole_get_request()`, `mconsole_reply_len()`, `mconsole_reply()`, `mconsole_unlink_socket()`, and `mconsole_notify()`. Internal helpers are `mconsole_reply_v0()` and `mconsole_parse()`.

Control flow: `mconsole_get_request()` receives a datagram, records sender address, rejects legacy unversioned clients, checks size and version, NUL-terminates payload, and finds a command. Reply helpers split large output into protocol-sized packets with `err` only on the first packet and `more` markers. `mconsole_notify()` lazily opens a Unix datagram socket, builds a notification packet, and sends it to the configured path under notify locking.

State and persistence: global `mconsole_socket_name` holds the bound control socket path, and static `notify_sock` caches the notification socket FD. `mconsole_unlink_socket()` removes the host socket path.

Dependencies and integration points: depends on Unix datagram sockets, `sendto`/`recvfrom`, command handlers in `mconsole_kern.c`, and notify locks provided by kernel-side code.

Risks: command matching is prefix-based, so ambiguous prefixes must be avoided. `strcpy(target.sun_path, sock_name)` assumes the path fits `sockaddr_un`. Legacy version-0 clients are explicitly unsupported.

Test signals: send each command over a Unix datagram socket, oversized request rejection, bad magic/version handling, multi-packet replies, boot/panic/user notifications, and socket unlink on reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_user.c -->
