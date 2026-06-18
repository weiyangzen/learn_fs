# sources/distributed-fs/ceph-client/drivers/vhost/vhost.c

## Purpose

`vhost.c` is the shared kernel vhost core used by vhost-net, vhost-scsi, vhost-test, vhost-vdpa, and related backends. It implements owner/mm binding, worker execution, eventfd polling, virtqueue setup ioctls, descriptor translation, IOTLB miss/update handling, dirty logging, used-ring publication, notification suppression, and common character-device read/write/poll helpers for IOTLB messages.

## Important APIs, Types, and Functions

Initialization and lifecycle APIs include `vhost_dev_init()`, `vhost_dev_set_owner()`, `vhost_dev_reset_owner_prepare()`, `vhost_dev_reset_owner()`, `vhost_dev_stop()`, `vhost_dev_cleanup()`, `vhost_dev_flush()`, `vhost_dev_check_owner()`, and `vhost_dev_has_owner()`. Worker APIs include `vhost_work_init()`, `vhost_poll_init()`, `vhost_poll_start()`, `vhost_poll_stop()`, `vhost_poll_queue()`, `vhost_vq_work_queue()`, `vhost_worker_ioctl()`, and internal worker creation/attachment helpers.

Virtqueue and ioctl APIs include `vhost_dev_ioctl()`, `vhost_vring_ioctl()`, `vhost_init_device_iotlb()`, `vhost_vq_access_ok()`, `vq_meta_prefetch()`, `vhost_vq_init_access()`, `vhost_get_vq_desc_n()`, `vhost_get_vq_desc()`, `vhost_discard_vq_desc()`, `vhost_add_used()`, `vhost_add_used_n()`, `vhost_add_used_and_signal()`, `vhost_add_used_and_signal_n()`, `vhost_signal()`, `vhost_enable_notify()`, `vhost_disable_notify()`, and `vhost_vq_avail_empty()`. IOTLB and message APIs include `vhost_chr_write_iter()`, `vhost_chr_read_iter()`, `vhost_chr_poll()`, `vhost_new_msg()`, `vhost_enqueue_msg()`, `vhost_dequeue_msg()`, and `vhost_set_backend_features()`.

## Control Flow

Backends allocate their own containing device, create an array of `struct vhost_virtqueue *`, install kick handlers, and call `vhost_dev_init()`. Userspace becomes owner with `VHOST_SET_OWNER`; the core attaches the current mm, allocates per-vq iovec/log/head arrays, creates a default worker when the backend uses workers, and attaches every vq to it. Common ioctls then configure memory tables, logging, vring size/address/base, kick/call/error eventfds, busyloop timeouts, optional endian mode, and optional IOTLB mode.

Polling starts when a backend attaches a file or kick fd. `vhost_poll_start()` registers a waitqueue callback through `vfs_poll()`. On wakeup, the callback either runs work directly for no-worker devices such as vDPA or queues work to the vq's worker. Worker threads drain lockless work lists, clear queued bits, run callbacks under the owner mm for kthread workers, and integrate with KCOV. Flush enqueues a completion work item to every worker and waits for it, providing a barrier for backend teardown and endpoint changes.

Descriptor consumption starts with `vhost_get_avail_idx()`, which reads and validates the guest available index. `vhost_get_vq_desc_n()` then selects the head, walks direct or indirect descriptors, translates guest addresses through either the memory table or device IOTLB, enforces output-before-input ordering, records writable log ranges, advances `last_avail_idx` and `next_avail_head`, and returns the head. Backends can roll this back with `vhost_discard_vq_desc()` after transient backend failures. Completion writes used elements, updates the used index with ordering barriers, logs dirty used-ring writes when enabled, and signals the call eventfd only when notification rules require it.

IOTLB mode is enabled by `vhost_init_device_iotlb()`. When translation misses, the core queues `VHOST_IOTLB_MISS` messages to `read_list` and wakes userspace. Userspace reads the miss through `vhost_chr_read_iter()`, which moves miss nodes to `pending_list`, then writes UPDATE/INVALIDATE messages through `vhost_chr_write_iter()`. The default handler updates the shared IOTLB, clears metadata caches, validates userspace memory access, and requeues pending vqs whose misses are satisfied. vDPA supplies its own message handler for DMA map/unmap side effects.

## State and Persistence Behavior

The core maintains per-device state in `struct vhost_dev`: owner mm, memory table `umem`, device IOTLB, vq list, worker xarray, logging eventfd, read and pending IOTLB message lists, weight limits, backend feature flags, and the fork-owner mode. Each vq stores ring pointers, descriptor counters, feature bits, backend private data, eventfd/file references, IOTLB pointers, metadata-cache entries, logging fields, worker pointer, and scratch arrays. State is in-memory and scoped to the opened backend device. Cleanup drops eventfd and file refs, resets every vq, frees iovecs, frees IOTLBs and queued messages, destroys workers, wakes readers, and detaches the owner mm.

## Dependencies and Integration Points

`vhost.c` depends on Linux eventfd, poll, waitqueue, kthread and vhost_task workers, mm ownership, cgroups, xarray, IOTLB interval trees, virtio ring definitions, user-copy helpers, dirty page logging, module parameters, and optional cross-endian legacy support. Backend drivers call the exported symbols to implement protocol-specific devices. Userspace VMMs interact with this core through the common vhost ioctls and IOTLB read/write protocol.

## Risks and Edge Cases

This file is a high-trust boundary between guest-controlled descriptors and kernel memory access. Address translation must reject overflow, invalid permissions, descriptor loops, nested indirect descriptors, out-after-in ordering, and unavailable IOTLB mappings. Used-ring publication depends on memory barriers paired with guest notification logic. Worker reassignment uses RCU plus flushes; missing a flush can leave callbacks running on old backend state. Owner/mm lifetime differs between worker and no-worker devices. Dirty logging must mark the correct guest pages for both direct memory tables and IOTLB-translated used rings. `vhost_add_used_n_in_order()` and descriptor discard need exact descriptor counts for `VIRTIO_F_IN_ORDER`. IOTLB miss messages are retained on `pending_list` after userspace reads them, so cleanup and successful updates must free or requeue them correctly.

## Test Signals

Core signals include vhost-net, vhost-scsi, vhost-test, vhost-vsock, and vhost-vdPA integration tests; syzkaller coverage for vhost ioctls and descriptor parsing; lockdep/KCSAN for worker reassignment and teardown; KASAN/KMSAN for user-copy paths; migration dirty-log tests; IOTLB miss/update/invalidate tests; packed and split ring tests; `VIRTIO_F_IN_ORDER` tests; worker creation/free/attach ioctls; and fault injection for eventfd, memory table, and IOTLB allocation failures.
