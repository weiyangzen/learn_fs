<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_0_9.c -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_0_9.c

## Purpose

Implements a benchmark backend modeled on virtio 0.9 split rings, with optional `RING_POLL` and `INORDER` compile-time variants.

## Important APIs, Types, and Functions

Source size: 333 lines, 7155 bytes. Functions/classes: alloc_ring, add_inbuf, used_empty, disable_call, kick_available, disable_kick, avail_empty, use_buf, call_used. Includes: main.h, stdlib.h, stdio.h, assert.h, string.h, linux/virtio_ring.h. Macros/defines: _GNU_SOURCE, HOST_GUEST_PADDING.

## Control Flow and Data Flow

Guest allocates descriptors, writes avail entries or in-order state, publishes `avail->idx`, and later consumes used entries. Host reads available heads, translates descriptors, writes used entries or in-order lengths, publishes `used->idx`, and uses `vring_need_event()` for kicks/calls.

## State and Persistence Behavior

State spans `struct vring ring`, guest free-list/indices, host used indices, and side data tokens. `virtio_ring_poll.c` and `virtio_ring_inorder.c` include this file with feature defines to build alternate code paths.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The three variants share source and are mutually exclusive in assumptions. Barrier A/B/C/D pairs must match virtio split-ring visibility requirements. Ring polling encodes high bits in ids and can break if index masking changes.

## Test Signals

Build all variants, run wraparound and sleep-mode tests, compare notification counts, and test with and without outstanding limits on x86 and weaker memory-order architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/virtio_ring_0_9.c -->
