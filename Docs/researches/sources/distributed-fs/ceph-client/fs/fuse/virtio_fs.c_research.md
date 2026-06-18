# sources/distributed-fs/ceph-client/fs/fuse/virtio_fs.c

## Purpose
Implements the virtio-fs transport and filesystem registration layer: discovers virtio filesystem devices, exposes them in sysfs, maps FUSE requests onto virtqueues, handles completions and forgets, optionally sets up DAX shared memory, and mounts virtiofs through the common FUSE superblock path.

## Important APIs, Types, And Functions
`struct virtio_fs` stores device instance state: tag, virtqueues, CPU-to-queue map, DAX device, and shared memory window. `struct virtio_fs_vq` stores per-virtqueue lock, queued/end request lists, work items, FUSE device pointer, connection flag, and in-flight count. Probe/remove are handled by `virtio_fs_probe()` and `virtio_fs_remove()`. Queue setup and teardown use `virtio_fs_setup_vqs()`, `virtio_fs_init_vq()`, `virtio_fs_map_queues()`, `virtio_fs_start_all_queues()`, `virtio_fs_stop_all_queues()`, and drain helpers. Request transport uses `virtio_fs_send_req()`, `virtio_fs_enqueue_req()`, SG counting/init helpers, `copy_args_to_argbuf()`, `copy_args_from_argbuf()`, completion workers, and response verification. Forget handling uses the hiprio queue via `virtio_fs_send_forget()` and `send_forget_request()`. Mount integration uses `virtio_fs_init_fs_context()`, `virtio_fs_parse_param()`, `virtio_fs_get_tree()`, `virtio_fs_fill_super()`, `virtio_kill_sb()`, and `virtio_fs_conn_destroy()`. DAX support uses `virtio_fs_setup_dax()`, `virtio_fs_direct_access()`, and `virtio_fs_zero_page_range()`.

## Control Flow
Device probe allocates an instance, reads and validates the tag, creates virtqueues, maps request queues to CPUs, optionally maps the DAX cache window, marks the virtio device ready, and publishes the instance in sysfs/list state. Mount lookup finds an instance by tag, creates FUSE connection/mount objects, caps `max_pages_limit` by virtqueue size, shares superblocks per instance, allocates one `fuse_dev` per queue, fills the common FUSE superblock, installs devices, restarts queues, and sends FUSE INIT. Request submission assigns a unique ID, selects a request queue from `mq_map`, builds scatterlists from headers/argbuf/folios, adds the request to the virtqueue and FUSE processing hash, and kicks the device. Full queues move requests to per-vq queued lists for workqueue retry. Completion workers collect buffers, verify response length and unique ID, copy out args, zero short page replies when requested, end FUSE requests, and decrement in-flight counts. Remove/unmount paths stop queues, drain in-flight work, reset virtio queues, and release FUSE devices and instance refs.

## State And Persistence
Global state includes `virtio_fs_instances`, `virtio_fs_mutex`, and `/sys/fs/virtiofs` kset state. Per-device state includes tag, virtqueues, CPU mapping, DAX window mapping, sysfs kobjects, and queue connection/in-flight counters. Per-request transient state includes `req->argbuf`, `FR_SENT`, processing-list membership, and virtqueue buffer ownership. The file does not persist filesystem contents itself; persistence is provided by the host virtiofs daemon/backing store.

## Dependencies And Integration Points
Depends on virtio core, FUSE connection and device queues, fs_context parsing, sysfs/kobject APIs, DAX/dev_pagemap infrastructure, workqueues, scatterlists, CPU affinity helpers, and common FUSE superblock code. Integrates as a `virtio_driver` for `VIRTIO_ID_FS` and a `file_system_type` named `virtiofs`.

## Risks
Transport correctness depends on SG layout matching the FUSE protocol and virtqueue direction conventions. Response verification prevents misdelivered or malformed replies but converts failures to `EIO`. Queue-full retry paths must preserve in-flight accounting exactly. Remove/unmount races are controlled by `virtio_fs_mutex`, connected flags, and queue drains. DAX setup maps device memory into kernel address space and must reject missing or busy cache windows. Suspend/resume is not supported and returns `EOPNOTSUPP`.

## Test Signals
Test probe/remove, duplicate tags, invalid/newline tags, mount by tag, no-source mount failure, multiqueue CPU mapping, full virtqueue retry, malformed response headers, forget queue pressure, unmount while requests are in flight, DAX `dax=always/never/inode` behavior, sysfs attributes and uevents, and max_pages limiting by vring size.
