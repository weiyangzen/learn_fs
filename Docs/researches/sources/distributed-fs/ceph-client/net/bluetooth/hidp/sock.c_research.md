# sources/distributed-fs/ceph-client/net/bluetooth/hidp/sock.c

## Purpose
Provides the HIDP PF_BLUETOOTH raw socket endpoint and ioctl bridge used by userspace to add, remove, list, and inspect HIDP sessions. It also registers the HIDP Bluetooth protocol family entry, procfs listing, and protocol object.

## APIs, Types, and Functions
Socket operations are `hidp_sock_create()`, `hidp_sock_release()`, `hidp_sock_ioctl()`, and optional `hidp_sock_compat_ioctl()`, wired through `hidp_sock_ops`. The ioctl dispatcher `do_hidp_sock_ioctl()` handles `HIDPCONNADD`, `HIDPCONNDEL`, `HIDPGETCONNLIST`, and `HIDPGETCONNINFO`. `hidp_init_sockets()` registers `hidp_proto`, `BTPROTO_HIDP`, and `/proc` support; `hidp_cleanup_sockets()` tears them down. `hidp_sk_list` tracks open HIDP sockets.

## Control Flow, State, and Persistence
Creating a socket requires `SOCK_RAW`, allocates a `struct bt_sock`, assigns HIDP proto ops, marks it unconnected, and links it into `hidp_sk_list`. Release unlinks, orphans, and drops the socket reference.

For `HIDPCONNADD`, ioctl handling requires `CAP_NET_ADMIN`, copies `struct hidp_connadd_req` from userspace, looks up the supplied control and interrupt socket file descriptors, NUL-terminates the name, calls `hidp_connection_add()`, optionally copies the request back, and drops both socket fd references. `HIDPCONNDEL` also requires `CAP_NET_ADMIN` and calls `hidp_connection_del()`. Listing and info ioctls copy request structs in, delegate to `core.c`, and copy updated results out. Compat handling remaps 32-bit pointers for `HIDPGETCONNLIST` and `HIDPCONNADD`.

Persistent state is limited to registered protocol metadata and the global Bluetooth socket list. Actual HIDP session state is owned by `core.c`.

## Dependencies and Integration
Depends on Bluetooth socket helpers (`bt_sock_alloc`, `bt_sock_link`, `bt_sock_register`, procfs helpers), Linux file descriptor lookup, usercopy helpers, capability checks, compat pointer conversion, and the HIDP core connection APIs. It integrates with module init/exit in `core.c` and exposes the legacy userspace control plane for creating HIDP sessions over already-connected L2CAP sockets.

## Risks and Test Signals
Risks include ioctl ABI compatibility, usercopy failures after sessions are created, fd lifetime/reference mistakes around `sockfd_lookup()`/`sockfd_put()`, insufficient privilege checks on future mutating commands, 32-bit compat structure drift, and raw socket creation outside the initial network namespace assumptions implied by procfs init on `init_net`.

Strong test signals are raw socket create/release, unsupported socket type rejection, capability checks for add/delete, bad user pointer handling, invalid `cnum` rejection, fd lookup cleanup when one socket lookup fails, compat add/list from a 32-bit process, registration rollback if `bt_sock_register()` or procfs init fails, and cleanup removing procfs/protocol registrations.
