<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atalk.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atalk.h

## Purpose
Defines AppleTalk socket address, network range, and protocol constants for Linux AppleTalk networking compatibility.

## Important APIs, Types, And Functions
Exports AppleTalk port/address constants, DDP size/hop limits, `SIOCATALKDIFADDR`, `struct atalk_addr`, `struct sockaddr_at`, and `struct atalk_netrange`.

## Control Flow
Userspace uses `sockaddr_at` with AppleTalk sockets and private ioctls to configure addresses. Kernel networking code uses network/node/port fields to bind, route, and send DDP traffic.

## State And Persistence
Runtime state includes interface AppleTalk addresses and network ranges. Persistence is external, through network configuration.

## Dependencies And Integration Points
Depends on Linux socket/types and byte order. Integrates with netatalk compatibility, AppleTalk protocol stack, and socket APIs.

## Risks And Edge Cases
The ABI is legacy; broadcast/any values, localtalk port constraints, and big-endian network fields must be handled correctly.

## Test Signals
Socket bind/connect tests, ioctl address configuration, endian checks for network fields, broadcast/any address behavior, and interoperability with netatalk tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atalk.h -->
