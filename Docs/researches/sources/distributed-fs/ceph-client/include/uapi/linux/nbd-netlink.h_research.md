# sources/distributed-fs/ceph-client/include/uapi/linux/nbd-netlink.h

## Purpose
Defines generic netlink family, multicast group, commands, and nested attributes for configuring Network Block Device instances.

## Important APIs, Types, And Functions
Exports `NBD_GENL_FAMILY_NAME`, `NBD_GENL_VERSION`, `NBD_GENL_MCAST_GROUP_NAME`, command enum `NBD_CMD_*`, top-level attrs `NBD_ATTR_*`, nested device-list attrs `NBD_DEVICE_*`, and nested socket attrs `NBD_SOCK_*`.

## Control Flow
Userspace sends netlink CONNECT, DISCONNECT, RECONFIGURE, STATUS requests with attributes such as index, size, block size, timeouts, flags, sockets, backend identifier, and device list. Kernel replies or multicasts link-dead events.

## State, Persistence, And Dependencies
State persists in configured NBD devices, socket attachments, timeouts, and flags. No external header dependencies.

## Integration Points
Used by nbd-client tooling and kernel NBD generic netlink configuration paths, complementing legacy ioctl setup in `nbd.h`.

## Risks
Nested list policies must be parsed exactly. Socket fds are passed as attributes and must be validated. Reconfigure semantics can race with active block I/O.

## Test Signals
Validate family/version, connect with multiple sockets, status dumps, device list nesting, disconnect events, backend identifier round trip, and malformed attribute rejection.
