# sources/distributed-fs/ceph-client/drivers/block/nbd.c

## Purpose
This file implements the Linux Network Block Device client driver. It exposes `/dev/nbd*` block devices, binds them to TCP or stream UNIX sockets through legacy ioctls or generic netlink, sends block requests using the NBD protocol, receives replies in workqueue threads, supports reconnect/multi-connection operation, and manages debugfs/sysfs/status reporting.

## Important APIs, Types, And Functions
Runtime state is split into `struct nbd_device` for the disk/tag-set/lifetime, `struct nbd_config` for a live configuration, `struct nbd_sock` for each socket, and `struct nbd_cmd` for per-request state. Device creation/removal uses `nbd_dev_add()`, `nbd_dev_remove()`, `nbd_put()`, and IDR `nbd_index_idr`. Request handling uses blk-mq ops `nbd_queue_rq()`, `nbd_complete_rq()`, `nbd_init_request()`, and `nbd_xmit_timeout()`.

Transport functions include `nbd_send_cmd()`, `nbd_pending_cmd_work()`, `nbd_read_reply()`, `nbd_handle_reply()`, `recv_work()`, `sock_xmit()`, and `__sock_xmit()`. Configuration paths include ioctl handlers `nbd_ioctl()` and `__nbd_ioctl()`, config allocation/refcounting in `nbd_alloc_and_init_config()` and `nbd_config_put()`, netlink handlers `nbd_genl_connect()`, `nbd_genl_disconnect()`, `nbd_genl_reconfigure()`, and `nbd_genl_status()`, plus `nbd_start_device()`, `nbd_disconnect_and_put()`, and `nbd_reconnect_socket()`.

## Control Flow
Module init validates `max_part`/`nbds_max`, registers the NBD major, creates an async delete workqueue, registers the generic-netlink family, initializes debugfs, and pre-creates `nbds_max` devices. Opening a disk creates a config if needed. Legacy ioctl setup adds sockets, sets size/block size/timeout/flags, then `NBD_DO_IT` starts receive workers and waits for them to exit. Netlink setup can allocate or reuse a device, allocate config, set size/timeouts/server/client flags, add sockets, optional backend identifier, create sysfs backend, start receive workers, and return the selected index.

For I/O, blk-mq calls `nbd_queue_rq()`, which locks the command and sends through a socket selected by hardware queue index. `nbd_send_cmd()` builds an NBD request with a cookie/tag handle, sends the header, sends write payload bvecs if needed, and marks the command inflight. Partial sends are pinned to the socket via `nsock->pending` and resumed by `nbd_pending_cmd_work()` to avoid tag confusion. Receive workers read reply headers, validate magic/tag/socket/cookie/inflight state, receive read payloads into request bvecs, clear inflight, and complete the request.

Timeouts either requeue to another live socket, wait for reconnect if configured, warn and extend when socket timeout is disabled, or mark the connection timed out, shut down sockets, and complete the request with error. Disconnect sends `NBD_CMD_DISC`, shuts down sockets, clears inflight requests, resets capacity on last opener, drops config refs, and may destroy the device if `DESTROY_ON_DISCONNECT` is set.

## State And Persistence Behavior
NBD stores no block data locally; all persistence is in the remote server. Kernel state includes config flags, runtime flags, bytesize, block size, live socket array, live/recv thread counters, backend string, sysfs files, debugfs directory, per-request cookies, and refcounts. `NBD_RT_BOUND` distinguishes netlink-controlled devices from ioctl-controlled devices. `NBD_DESTROY_ON_DISCONNECT` and `NBD_DISCONNECT_REQUESTED` control device lifetime.

## Dependencies And Integration Points
The driver integrates with blk-mq, gendisk, block ioctls, generic netlink (`linux/nbd-netlink.h`), NBD UAPI (`linux/nbd.h`), sockets, kernel credentials for socket I/O, workqueues, debugfs, sysfs device attributes, IDR indexing, module parameters, tracepoints (`trace/events/nbd.h`), and queue limit updates for discard, flush/FUA, write zeroes, rotational, block size, capacity, and partition scanning.

## Risks
The highest-risk areas are request lifetime races between send completion and receive completion, partial-send recovery, timeout/requeue races, stale replies after reconnect, and config teardown while workers hold refs. The code uses cookies and `NBD_CMD_INFLIGHT` to detect double or stale replies. Socket I/O uses `GFP_NOIO`/memalloc context because block I/O over networking can recurse into reclaim. Netlink status intentionally reads some state racefully. Legacy ioctl and netlink controls are mutually constrained to prevent mixed ownership.

## Test Signals
Signals include successful creation of default `/dev/nbd*` devices, ioctl attach/read/write/disconnect, netlink connect/reconfigure/status/disconnect, multi-connection rejection unless server flags allow it, reconnect after dead link, timeout behavior with and without `tag_set.timeout`, sysfs `pid`/`backend`, debugfs entries, discard/flush/FUA/write-zeroes queue limit changes, partition scan after sizing, and blktests NBD coverage under forced socket failures.
