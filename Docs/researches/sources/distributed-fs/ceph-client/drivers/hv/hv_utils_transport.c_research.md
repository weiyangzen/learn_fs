<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.c

## Purpose

`hv_utils_transport.c` provides the kernel-to-userspace transport abstraction used by Hyper-V KVP and VSS daemons. It supports both legacy connector/netlink and newer misc character devices, serializes one outbound message at a time for char devices, receives daemon replies, and handles reset/destroy state transitions.

## Important APIs, Types, and Functions

- Global `hvt_list` plus `hvt_list_lock` tracks transports for connector callback lookup.
- `hvt_op_open()`, `hvt_op_read()`, `hvt_op_write()`, `hvt_op_poll()`, and `hvt_op_release()` implement misc device file operations.
- `hvt_cn_callback()` routes connector messages to the matching transport.
- `hvutil_transport_send()` sends a kernel message to userspace via connector or char device and optionally calls `on_read_cb` when consumed.
- `hvutil_transport_init()` allocates a transport, registers the misc device, and optionally registers a connector callback.
- `hvutil_transport_destroy()` marks destroy state, wakes readers, unregisters connector and misc device, and waits for open char-device release when necessary.
- `hvt_reset()` clears pending outbound state and invokes service reset callback.

## Control Flow

Initialization fills connector IDs, miscdevice metadata, embedded file operations, waitqueue, mutex, and completion, adds the transport to the global list, registers the misc device, and optionally registers connector callback. A daemon can communicate via connector first, which switches mode from INIT to NETLINK, or open the char device, which switches INIT or NETLINK to CHARDEV and resets any netlink state. `hvutil_transport_send()` rejects INIT/DESTROY, allocates and sends a connector message in NETLINK mode, or stores a single `outmsg`, wakes readers, and records an `on_read` callback in CHARDEV mode.

Reads block until an outbound message exists or mode changes, copy the whole message, free it, and call `on_read`. Writes copy user data and pass it to the service's `on_msg()` callback. Release resets pending state and returns to INIT unless destroy is active; destroy waits for that release if a char-device fd is open.

## State and Persistence Behavior

`struct hvutil_transport` persists from init to destroy and stores mode, callbacks, pending outbound message, waitqueue, lock, miscdevice, connector ID, and release completion. The mode is the core state machine: INIT, NETLINK, CHARDEV, DESTROY. Pending char-device messages are single-slot; services must not queue a second message before userspace reads the first.

## Dependencies and Integration Points

The transport depends on miscdevice, connector, poll, usercopy, and service callbacks supplied by `hv_kvp.c` and `hv_snapshot.c`. It is initialized by those services through `hv_util.c`.

## Risks and Edge Cases

Mode transitions can reset active service transactions, so reset callbacks must fail or clean pending host work. `hvutil_transport_send()` in NETLINK mode calls `on_read_cb` immediately because delivery completion is unknown; char-device mode waits for actual read. A second char-device outbound send fails with `-EFAULT` if the previous message was not read. Destroy must avoid freeing a transport while file operations are active.

## Test Signals

Test char-device open/read/write/poll/release, connector fallback, switching from netlink to char device, daemon reset during active KVP/VSS transactions, destroy with and without open fds, send before daemon registration, duplicate send before read, and wakeup behavior on destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.c -->
