# sources/distributed-fs/ceph-client/drivers/xen/pvcalls-front.h

## Purpose
`pvcalls-front.h` declares the socket-operation entry points exported by the PV Calls frontend.

## Important APIs, types, and functions
It declares helpers for socket creation, connect, bind, listen, accept, sendmsg, recvmsg, poll, and release. The signatures use `struct socket`, `struct sockaddr`, `struct msghdr`, `struct proto_accept_arg`, `struct file`, and `poll_table`, matching Linux socket operation hooks.

## Control flow
The header has no runtime control flow. Consumers call these functions from socket operation tables when PV Calls is selected for a socket.

## State and persistence
No state is stored here. The implementation in `pvcalls-front.c` owns all per-device and per-socket state.

## Dependencies and integration points
It includes `<linux/net.h>` and is the local contract between PV Calls frontend implementation and code that wires the frontend into networking/socket operations.

## Risks and test signals
Risks are ABI drift between declarations and implementation or kernel socket API signature changes. Test signals are compile coverage and exercising every declared operation through PV Calls sockets.
