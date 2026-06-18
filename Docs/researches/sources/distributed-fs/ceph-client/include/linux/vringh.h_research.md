# sources/distributed-fs/ceph-client/include/linux/vringh.h

## Purpose
`vringh.h` defines host-side helpers for accessing a virtio vring owned by another entity. It is used when kernel code must parse descriptors, copy data, complete buffers, and handle notifications for user, kernel, or IOTLB-backed virtqueues.

## Important APIs, Types, and Functions
`struct vringh` records endian mode, event-index support, barrier strength, address mode, last avail/used indexes, completion count, the underlying `struct vring`, optional IOTLB and lock, and a notify callback. `struct vringh_config_ops` lets virtio drivers find/delete host vrings. `struct vringh_range` describes accessible memory. `struct vringh_iov` and `struct vringh_kiov` track consumed user iovecs and kernel kvecs. User APIs include `vringh_init_user()`, `vringh_getdesc_user()`, `vringh_iov_pull_user()`, `vringh_iov_push_user()`, completion, notification enable/disable, and need-notify checks. Kernel APIs mirror these with `vringh_init_kern()`, `vringh_getdesc_kern()`, `vringh_kiov_advance()`, completion and notify APIs. Optional IOTLB APIs include `vringh_set_iotlb()`, `vringh_init_iotlb*()`, descriptor, push/pull, complete, and notification helpers. Inline endian conversion wrappers use virtio byteorder helpers.

## Control Flow
A host initializes `vringh` with feature bits and ring addresses, repeatedly obtains descriptor chains into read/write iovecs, consumes or fills buffers, marks descriptor heads used with lengths, and checks whether notification is needed. Iovec reset restores consumed offsets if callers need to retry. IOTLB mode translates guest addresses through a vhost IOTLB protected by the supplied lock.

## State and Persistence
State is transient vring-processing state held in `struct vringh` and the foreign vring memory. `last_avail_idx`, `last_used_idx`, and `completed` persist across processing iterations until ring reset. Iov structs mutate while copying and must be reset or cleaned up. No durable persistence exists.

## Dependencies and Integration Points
The header depends on uapi virtio ring structures, virtio byteorder conversion, uio/kvec types, slab allocation, spinlocks, barriers, and optionally vhost IOTLB. It integrates with vhost, virtio drivers exposing host vrings, eventfd/kick notification code, and descriptor-copying paths.

## Risks
Foreign vring memory may be user-controlled or guest-controlled, so descriptor validation and range checks are critical. Endian and barrier settings must match negotiated features. Iov cleanup must free allocated arrays exactly once. Event-index notification logic is easy to get wrong and can cause missed kicks or interrupt storms. IOTLB translations require correct locking and stale mapping handling.

## Test Signals
Signals include descriptor-chain parsing tests, indirect and malformed descriptor rejection, user and kernel vring copy tests, notification suppression/enable tests, endian compatibility, IOTLB translation and invalidation tests, wraparound of avail/used indexes, and vhost integration traffic.
