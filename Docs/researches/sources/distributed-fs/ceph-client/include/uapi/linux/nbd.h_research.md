# sources/distributed-fs/ceph-client/include/uapi/linux/nbd.h

## Purpose
Defines legacy Network Block Device ioctl ABI, NBD protocol command/flag constants, and wire request/reply packet layouts.

## Important APIs, Types, And Functions
Exports `NBD_SET_*`, `NBD_DO_IT`, `NBD_DISCONNECT`, command enum `NBD_CMD_*`, server flags `NBD_FLAG_*`, command flags, client flags, magics `NBD_REQUEST_MAGIC`/`NBD_REPLY_MAGIC`, and packed `nbd_request`/`nbd_reply`.

## Control Flow
Userspace configures an NBD block device with ioctls, hands sockets to the kernel, starts serving with `NBD_DO_IT`, and handles read/write/flush/trim/write-zeroes requests over the socket protocol.

## State, Persistence, And Dependencies
State persists in NBD device configuration, sockets, block queue, and protocol request cookies. Depends on `linux/types.h`.

## Integration Points
Used by legacy nbd-client/server implementations and kernel block device request paths. Generic netlink configuration is defined separately in `nbd-netlink.h`.

## Risks
Wire fields are network byte order and packed. Unsupported structured replies are explicitly not defined here. Server/client flags have different semantics and gaps preserved for userspace compatibility.

## Test Signals
Validate ioctl setup, block size/size flags, disconnect behavior, request/reply magic and cookie matching, command flag handling, flush/trim/write-zeroes support, and endian correctness.
