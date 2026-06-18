<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/main.c -->
# sources/distributed-fs/ceph-client/tools/virtio/ringtest/main.c

## Purpose

Provides the common two-thread benchmark harness for ring implementations in `tools/virtio/ringtest`. It parses options, creates eventfd-based kick/call channels, starts host and guest threads, and repeatedly drives the selected ring backend.

## Important APIs, Types, and Functions

Source size: 391 lines, 6532 bytes. Functions/classes: notify, wait_for_notify, kick, wait_for_kick, call, wait_for_call, set_affinity, poll_used, __attribute__, if, if, if, if, if, poll_avail, __attribute__, if, while, plus 4 more. Includes: getopt.h, pthread.h, assert.h, sched.h, main.h, sys/eventfd.h, stdlib.h, stdio.h, unistd.h, limits.h. Macros/defines: _GNU_SOURCE.

## Control Flow and Data Flow

The guest loop enqueues buffers until the run count or outstanding limit is reached, kicks in batches, drains completions, and either sleeps on call eventfd or polls. The host loop waits for available buffers, consumes them, optionally signals used buffers, and exits after the configured number of transfers.

## State and Persistence Behavior

Global knobs include `runcycles`, `max_outstanding`, `batch`, `param`, `do_sleep`, `do_relax`, `do_exit`, and `ring_size`. Ring-specific persistent state is owned by the linked backend implementation.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/ringtest`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Assertions are used as error handling, invalid affinity or ring-size inputs abort, and sleep mode depends on backend notification functions being implemented. Benchmark results are sensitive to CPU affinity, cache sharing, eventfd overhead, and architecture-specific delay loops.

## Test Signals

Run each backend with polling and sleep modes, small/large rings, constrained outstanding counts, batching, host/guest affinity combinations, and architecture-specific relax/barrier paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/ringtest/main.c -->
