# sources/distributed-fs/ceph-client/samples/bpf/sock_example.h

Purpose: shared helper for socket BPF samples to open a raw packet socket on a named interface.

Important APIs/types/functions: `open_raw_sock(const char *name)` uses `socket(PF_PACKET, SOCK_RAW|SOCK_NONBLOCK|SOCK_CLOEXEC, htons(ETH_P_ALL))`, `if_nametoindex`, `bind`, and `sockaddr_ll`.

Control flow: creates a packet socket, resolves interface index, binds to all Ethernet protocols on that interface, and returns the socket FD or exits on errors.

State and persistence: returns a live socket FD owned by the caller.

Dependencies and integration: included by `sockex*_user.c` and related socket samples; depends on Linux packet sockets and netdevice names.

Risks: helper exits the process on failure. Requires privileges and a valid interface. Nonblocking socket behavior matters for callers.

Test signals: opening on `lo` or another interface succeeds and attached socket filters receive traffic.
