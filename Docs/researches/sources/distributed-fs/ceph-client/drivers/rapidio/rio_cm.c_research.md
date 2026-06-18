# sources/distributed-fs/ceph-client/drivers/rapidio/rio_cm.c

## Purpose
Provides the RapidIO Channelized Messaging character device (`/dev/rio_cm`). It maps userspace ioctl operations onto RapidIO data-message mailboxes, with connection-oriented channel IDs, accept/connect handshakes, send/receive queues, endpoint discovery lists, mport lists, and teardown on device/mport removal or reboot.

## Important APIs, types, and functions
Core types are `struct cm_dev` for one local mport, `struct rio_channel` for each local channel, `struct chan_rx_ring` for queued/in-use receive buffers, `struct cm_peer` for reachable endpoints, and packet headers `rio_ch_base_bhdr`/`rio_ch_chan_hdr`. Global state includes `ch_idr`, `idr_lock`, `cm_dev_list`, `rdev_sem`, the cdev/class objects, and module parameters `cmbox` and `chstart`. Main operations include `riocm_ch_alloc/create/free/close`, `riocm_ch_bind/listen/accept/connect/send/receive`, `riocm_post_send`, `riocm_queue_req`, inbound work handler `rio_ibmsg_handler`, outbound completion `rio_txcq_handler`, ioctl dispatcher `riocm_cdev_ioctl`, RapidIO bus interface add/remove hooks, mport class interface add/remove hooks, and reboot notifier `rio_cm_shutdown()`.

## Control flow
Module init registers a class, chrdev region, mport class interface, RapidIO bus subsystem interface, reboot notifier, and cdev. Adding an mport allocates `cm_dev`, reserves inbound/outbound mailbox `cmbox`, creates an RX workqueue, pre-posts 128 inbound buffers, and publishes it. Adding a capable endpoint records it as a peer for the matching mport. Userspace creates a channel, binds it to an mport, listens or connects, and then sends/receives. Connect sends `CM_CONN_REQ`, waits up to `RIOCM_CONNECT_TO`, and transitions to connected on `CM_CONN_ACK`. Accept waits on the listening channel completion, allocates a new channel, matches the peer, sends ACK, and returns the new channel ID. Inbound mailbox callbacks queue work; the work handler drains messages, dispatches control packets or enqueues data to the channel RX ring. TX completions advance ring accounting and flush queued request packets.

## State and persistence
All state is volatile. Channel IDs live in an IDR and are file-descriptor-owned. RX buffers are tracked in both mport-level inbound rings and per-channel queued/in-use arrays. Removal paths close affected channels and free peers, mailboxes, workqueues, and buffers. The reboot notifier sends close packets for connected channels but does not persist metadata.

## Dependencies and integration
Depends on RapidIO mailbox APIs from `rio.c`, RapidIO bus and mport classes, `linux/rio_cm_cdev.h` ioctl ABI, IDR, krefs, completions, workqueues, cdev, reboot notifiers, and endian conversion helpers. Endpoint capability is determined by `RIO_SRC_OPS_DATA_MSG` and `RIO_DST_OPS_DATA_MSG`.

## Risks
The send path assumes mport `add_outb_message()` copies the buffer immediately; direct-buffer mport implementations could cause use-after-free. `cm_ep_get_list()` copies `info[0] + 2` entries even when only `nent + 2` were allocated, a notable bounds risk if user-requested count exceeds current peer count. Channel close/free uses `comp_close` and manual kfree after kref completion, making refcount sequencing important. The ioctl ABI trusts user-provided buffer sizes for receive truncation and does not return actual message length. TX accounting depends on hardware completion slot order.

## Test signals
Run ioctl create/bind/listen/accept/connect/send/receive/close flows, nonblocking and timeout waits, peer and mport hot-remove, reboot notifier, mailbox full and queued control-packet behavior, TX completion wraparound, invalid destIDs/mport IDs/channel ownership, receive ring full/in-use full cases, and memory-safety tests around endpoint-list copy sizes.
