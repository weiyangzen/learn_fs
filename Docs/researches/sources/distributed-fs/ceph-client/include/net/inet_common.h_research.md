# sources/distributed-fs/ceph-client/include/net/inet_common.h

Purpose: declares common IPv4/INET socket operations shared by stream and datagram protocols, plus GRO/GSO hooks and control-socket lifecycle.

Important APIs/types: exported `inet_stream_ops` and `inet_dgram_ops` are protocol operation tables. Socket operation declarations cover release, connect, accept, send/recv, shutdown, listen, bind, getname, ioctl, control-socket create/destroy, receive error, and socket destruct. Bind flags control address-no-port, locking, BPF-originated bind, and capability checks. GRO/GSO functions include `inet_gro_receive()`, `inet_gro_complete()`, and `inet_gso_segment()`. Indirect-call macros optimize GRO callback dispatch.

Control flow and state: socket syscalls enter these common helpers, which then delegate to protocol-specific `struct proto` hooks. Control sockets are created for kernel internal protocols and destroyed by `inet_ctl_sock_destroy()`. Persistent state lives in `struct sock` and derived `inet_sock`.

Dependencies and integration: depends on socket, netdev features, indirect-call wrappers, and `net/sock.h`. It integrates with TCP, UDP, RAW, ping sockets, GRO/GSO, and BPF bind paths.

Risks: bind flag combinations alter security and port allocation semantics. Common helpers affect all INET protocols, so regressions are broad. Tests should cover stream/datagram connect, bind variants, listener accept, shutdown, error queue receive, GRO/GSO paths, control-socket lifecycle, and BPF bind behavior.
