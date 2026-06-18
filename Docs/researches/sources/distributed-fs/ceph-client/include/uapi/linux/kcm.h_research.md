# sources/distributed-fs/ceph-client/include/uapi/linux/kcm.h

## Purpose
`kcm.h` defines socket ioctl structures for Kernel Connection Multiplexor attachment, detachment, and cloning.

## Important APIs, Types, and Functions
`struct kcm_attach` carries a target file descriptor and BPF program file descriptor. `struct kcm_unattach` carries a file descriptor to detach. `struct kcm_clone` returns or accepts a file descriptor for clone operations. Ioctls are `SIOCKCMATTACH`, `SIOCKCMUNATTACH`, and `SIOCKCMCLONE`. `KCMPROTO_CONNECTED` and `KCM_RECV_DISABLE` define protocol/flag values.

## Control Flow
Userspace attaches lower sockets and parser programs to KCM sockets, detaches them, or clones KCM endpoints. The kernel multiplexes message-oriented traffic over attached connections.

## State and Persistence
Attached socket associations, BPF parser references, and clone relationships are kernel socket state tied to file descriptors and network namespaces.

## Dependencies and Integration Points
It relies on socket-private ioctl numbering from networking headers. Integration points include KCM protocol sockets, BPF stream parsing, and applications multiplexing logical messages over TCP.

## Risks and Test Signals
Tests should validate fd lifetime/reference handling, BPF program type validation, detach of unknown fds, clone semantics, receive-disable behavior, and namespace/credential checks.
