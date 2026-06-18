# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-clt.c

## Purpose
Implements the RNBD client data plane and lifecycle. It creates RTRS client sessions, maps remote server devices into local `gendisk` instances, translates blk-mq requests into RNBD protocol messages over RDMA, handles reconnect/remap behavior, and tears down mapped devices and sessions.

## Important APIs, types, and functions
- Public entry points: `rnbd_clt_map_device()`, `rnbd_clt_unmap_device()`, `rnbd_clt_remap_device()`, and `rnbd_clt_resize_disk()`.
- Session management uses global `sess_list`, `sess_lock`, `struct rnbd_clt_session`, `find_and_get_or_create_sess()`, `alloc_sess()`, `free_sess()`, and refcount helpers.
- Device management uses `struct rnbd_clt_dev`, IDA minor allocation, per-device mutexes, `insert_dev_if_not_exists_devpath()`, `rnbd_delete_dev()`, and dev-state transitions.
- Admin messages use `send_msg_sess_info()`, `send_msg_open()`, `send_msg_close()`, `send_usr_msg()`, and completion workers.
- I/O path uses `rnbd_queue_rq()`, `rnbd_client_xfer_request()`, `msg_io_conf()`, and `rnbd_softirq_done_fn()`.
- blk-mq integration is through `rnbd_mq_ops`, `setup_mq_tags()`, queue mapping, polling support via `rnbd_rdma_poll()`, and `rnbd_init_mq_hw_queues()`.

## Control flow
On module init the driver verifies protocol structure sizes, registers block major `rnbd`, creates sysfs, and allocates a workqueue. Mapping starts by rejecting duplicate `pathname`/session pairs, finding or creating an RTRS session, querying session attributes, allocating blk-mq tags, sending session info, allocating a client device, sending an open request, then building a disk with queue limits derived from the server open response. I/O requests require a nonblocking RTRS I/O permit, allocate a chained sg table, encode sector/size/op/prio into `rnbd_msg_io`, submit `rtrs_clt_request()`, and complete asynchronously.

Reconnect events come from RTRS. Disconnect transitions mapped devices to `DEV_STATE_MAPPED_DISCONNECTED` and emits offline uevents. Reconnect sends session info and async open messages for existing devices, updates capacity, and emits online uevents. Unmap marks the device unmapped under lock, removes it from the session list, removes sysfs/disk objects, optionally sends close, then drops references.

## State and persistence behavior
All state is in memory. Sessions are refcounted and shared by devices unless polling queues require isolated sessions. `busy`, per-CPU requeue lists, and `cpu_queues_bm` track stopped blk-mq queues waiting for RTRS permits. Device state is guarded by `dev->lock`; session device lists are guarded by `sess->lock`; global session/device uniqueness scans are guarded by `sess_lock`. Local disk IDs come from `index_ida` and are freed when the device refcount reaches zero.

## Dependencies and integration points
Depends on block layer `gendisk`, blk-mq tag sets, queue limits, request mapping, Linux IDA/refcount/workqueue/kobject APIs, RTRS client APIs, and the RNBD protocol definitions. It is invoked by client sysfs and interacts with server `rnbd-srv.c` through `RNBD_MSG_SESS_INFO`, `OPEN`, `IO`, and `CLOSE`.

## Risks and test signals
- Permit exhaustion and requeue fairness are subtle; tests should force queue depth below active hctx count and confirm no I/O hang.
- Async admin messages hold device/session refs; reconnect/remap/unmap races need lockdep, KASAN, and RTRS fault injection coverage.
- `rq_to_rnbd_flags()` maps flush/FUA semantics into protocol flags; cross-version server testing should include flush, discard, secure erase, write zeroes, and `REQ_NOUNMAP`.
- Polling queues are incompatible with shared sessions; mapping two devices with conflicting `nr_poll_queues` should fail.
- Size and queue-limit changes should be tested through remap and explicit resize.
