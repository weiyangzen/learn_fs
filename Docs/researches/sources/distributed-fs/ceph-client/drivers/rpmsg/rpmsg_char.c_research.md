# sources/distributed-fs/ceph-client/drivers/rpmsg/rpmsg_char.c

Purpose: character-device interface for rpmsg endpoints. It exposes `/dev/rpmsgN` endpoint devices that userspace can open, read, write, poll, use for flow-control ioctls, and destroy when dynamically created.

Important APIs, types, and functions: `struct rpmsg_eptdev` owns the device, cdev, parent `rpmsg_device`, channel info, endpoint lock, endpoint pointer, optional default endpoint, SKB RX queue, read waitqueue, and remote flow-control flags. Exported functions are `rpmsg_chrdev_eptdev_create()` and `rpmsg_chrdev_eptdev_destroy()`. File ops are `rpmsg_eptdev_open()`, `release()`, `read_iter()`, `write_iter()`, `poll()`, and `ioctl()`. The rpmsg driver binds `rpmsg-raw` and `rpmsg_chrdev`.

Control flow: probe allocates an endpoint char device for matching rpmsg channels and reuses `rpdev->ept` as `default_ept`; dynamically created endpoints use `rpmsg_chrdev_eptdev_create()`. Open enforces single-open, gets a device reference, creates an endpoint if needed, sets `flow_cb`, and stores private data. RX callback copies inbound payloads into SKBs and wakes readers. Read blocks unless nonblocking, dequeues one SKB, copies up to user buffer length, and drops excess from that message. Write copies the iov into a kernel buffer and sends via `rpmsg_sendto()` or `rpmsg_trysendto()`. Poll reports readable data, flow-control priority updates, and backend TX readiness. Destroy detaches the endpoint, wakes readers, removes cdev/device, and drops the device reference.

State and persistence: all state is in memory and tied to rpmsg device lifetime. The incoming queue persists messages until read or release. `ept_lock` serializes endpoint pointer changes; `queue_lock` protects SKB queue operations. `remote_flow_updated` is cleared by `RPMSG_GET_OUTGOING_FLOWCONTROL`.

Dependencies and integration points: depends on rpmsg core APIs, `rpmsg_internal.h`, `rpmsg_char.h`, uapi `linux/rpmsg.h`, cdev/IDA allocation, SKB queues, wait queues, and backend support for flow control where available. `rpmsg_ctrl.c` uses the exported create/destroy helpers.

Risks: one open per endpoint is enforced; userspace expecting multi-reader semantics will get `-EBUSY`. Reads truncate messages larger than the supplied buffer and discard the remainder because the whole SKB is freed. `RPMSG_SET_INCOMING_FLOWCONTROL` calls backend flow control on `eptdev->ept`; callers must avoid ioctl after endpoint teardown. Allocation of write buffer equals user write length and can be large until backend rejects oversize messages.

Test signals: create static `rpmsg-raw` and dynamic endpoints, verify single-open, blocking and nonblocking read/write, poll for RX/TX and `EPOLLPRI`, flow-control ioctls, endpoint destroy ioctl, parent rpmsg removal while readers block, and message truncation semantics.
