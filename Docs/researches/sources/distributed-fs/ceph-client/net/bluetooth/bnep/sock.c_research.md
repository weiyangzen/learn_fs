# sources/distributed-fs/ceph-client/net/bluetooth/bnep/sock.c

## Purpose
This file exposes the BNEP control socket protocol under PF_BLUETOOTH, handling raw socket creation, ioctls for PAN session management, procfs listing, and protocol registration.

## Important APIs, Types, And Functions
Key functions are `bnep_sock_create()`, `bnep_sock_release()`, `bnep_sock_ioctl()`, `bnep_sock_compat_ioctl()`, `do_bnep_sock_ioctl()`, `bnep_sock_init()`, and `bnep_sock_cleanup()`. The socket operations table supports release and ioctl only; normal bind/connect/send/recv/listen operations use `sock_no_*` stubs.

## Control Flow
Creating a BNEP socket requires `SOCK_RAW`, allocates a Bluetooth socket with `bt_sock_alloc()`, assigns BNEP proto ops, marks it unconnected, and links it into `bnep_sk_list`. Ioctl handling gates add/delete operations on `CAP_NET_ADMIN`, copies request structures from userspace, resolves a provided connected L2CAP socket FD for `BNEPCONNADD`, delegates session work to `core.c`, copies updated data back to userspace, and supports connection list/info and supported-feature queries. Compat ioctl repacks the connection-list pointer for 32-bit userspace. Init registers the proto, registers `BTPROTO_BNEP` with the Bluetooth core, and creates `/proc/net/bnep`.

## State, Persistence, And Dependencies
The file maintains `bnep_sk_list` for procfs reporting. Active session state is owned by `core.c`; this socket layer only brokers user requests and references. There is no persistence beyond open sockets and active sessions.

## Integration Points
It uses common Bluetooth socket helpers from `af_bluetooth.c`, BNEP session functions from `core.c`, L2CAP sockets passed from userspace, Linux capabilities, file descriptor lookup, compat user pointers, and procfs.

## Risks
File descriptor ownership is split: on successful add, the session thread later releases the socket file; on failure, this layer must put it immediately. Ioctl structs are UAPI-like and require careful copy_to/from_user handling. Only raw sockets are supported, so wrong socket types must fail cleanly. Capability checks must remain on mutating operations.

## Test Signals
Signals include raw BNEP socket creation, non-raw rejection, permission failures for unprivileged add/delete, successful `BNEPCONNADD` returning the created device name, `BNEPCONNDEL` terminating sessions, compat `BNEPGETCONNLIST` working from 32-bit userspace, and `/proc/net/bnep` appearing and disappearing with module load/unload.
