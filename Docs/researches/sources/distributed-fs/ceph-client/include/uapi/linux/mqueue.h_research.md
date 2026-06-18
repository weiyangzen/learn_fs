# sources/distributed-fs/ceph-client/include/uapi/linux/mqueue.h

## Purpose
Defines POSIX message queue limits, attributes, and Linux-specific netlink cookie behavior for `SIGEV_THREAD` notification emulation.

## Important APIs, Types, And Functions
Exports `MQ_PRIO_MAX`, `MQ_BYTES_MAX`, `mq_attr`, notification states `NOTIFY_NONE`, `NOTIFY_WOKENUP`, `NOTIFY_REMOVED`, and `NOTIFY_COOKIE_LEN`.

## Control Flow
Userspace configures queues with `mq_attr`. For `SIGEV_THREAD`, userspace passes an AF_NETLINK fd in `sigev_signo` and a cookie pointer; kernel sends the cookie to the netlink socket and rewrites its last byte with a notification code.

## State, Persistence, And Dependencies
Queue state persists in mqueue objects and per-uid kernel memory accounting. Depends on `linux/types.h`.

## Integration Points
Used by libc POSIX mqueue implementation, real-time applications, and notification helpers.

## Risks
`SIGEV_THREAD` is explicitly userspace-implemented; misuse of signal fields or cookie length breaks notification. Limits are defaults/ceilings interacting with sysctls and per-uid accounting.

## Test Signals
Test queue creation with attributes, priority limit, per-uid byte limit behavior, notify set/remove, netlink cookie contents, and reserved fields zeroing.
