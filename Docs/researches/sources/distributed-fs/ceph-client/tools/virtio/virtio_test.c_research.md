<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio_test.c -->
# sources/distributed-fs/ceph-client/tools/virtio/virtio_test.c

## Purpose

Userspace regression/performance test for kernel virtqueue code against `/dev/vhost-test`. It creates a synthetic virtio device, maps one vhost memory region, configures a vring, and sends many buffers through the vhost test backend.

## Important APIs, Types, and Functions

Source size: 403 lines, 9088 bytes. Functions/classes: vq_notify, vq_callback, vq_reset, vq_info_add, vdev_info_init, wait_for_interrupt, if, run_test, while, if, if, if, while, if, if, help, main, switch, plus 2 more. Includes: getopt.h, limits.h, string.h, poll.h, sys/eventfd.h, stdlib.h, assert.h, unistd.h, sys/ioctl.h, sys/stat.h, sys/types.h, fcntl.h, stdbool.h, linux/virtio_types.h, linux/vhost.h, linux/virtio.h, linux/virtio_ring.h, ../../drivers/vhost/test.h. Macros/defines: _GNU_SOURCE, RANDOM_BATCH.

## Control Flow and Data Flow

`vdev_info_init()` opens the control fd and installs memory. `vq_info_add()` allocates vring memory, creates a `virtqueue`, and programs vhost vring ioctls. `run_test()` disables callbacks, batches outbuf submissions, kicks the backend, drains completions, optionally resets backend/ring state, and waits using normal or delayed interrupts.

## State and Persistence Behavior

State is held in `struct vdev_info`, `struct vq_info`, eventfds, one guest memory buffer, vhost memory table, and feature bits for indirect descriptors, event index, and virtio 1.0.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test assumes `/dev/vhost-test` and matching kernel headers. Reset paths manipulate backend and vring base while transfers are active. All failures are assertion-based, so it is best as a developer smoke/regression test.

## Test Signals

Run with `--no-indirect`, `--no-event-idx`, `--no-virtio-1`, delayed interrupts, random batch sizes, and reset intervals; verify no lost completions or vhost ioctl failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/virtio_test.c -->
