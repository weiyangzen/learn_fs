<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vringh_test.c -->
# sources/distributed-fs/ceph-client/tools/virtio/vringh_test.c

## Purpose

Comprehensive userspace test for host-side `vringh` helpers, including direct descriptors, indirect descriptors, split user address mappings, iov expansion, multi-completion, event index, and a parallel host/guest stress mode.

## Important APIs, Types, and Functions

Source size: 758 lines, 20556 bytes. Functions/classes: never_notify_host, never_callback_guest, getrange_iov, getrange_slow, parallel_notify_host, no_notify_host, find_cpus, if, vringh_get_head, parallel_test, if, while, if, if, if, if, if, if, plus 8 more. Includes: sched.h, err.h, linux/kernel.h, linux/err.h, linux/virtio.h, linux/vringh.h, linux/virtio_ring.h, linux/virtio_config.h, linux/uaccess.h, sys/types.h, sys/stat.h, sys/mman.h, sys/wait.h, fcntl.h. Macros/defines: _GNU_SOURCE, USER_MEM, RINGSIZE, ALIGN, NUM_XFERS.

## Control Flow and Data Flow

The non-parallel path creates a guest virtqueue and host `vringh` view over user memory, then tests descriptor fetch, pull/push, completion, large scatterlists, many completions, and unusual indirect descriptor layouts. `parallel_test()` mmaps the same file at different host/guest addresses, forks host and guest, exchanges notifications through pipes, and optionally uses a fast opencoded get-head path.

## State and Persistence Behavior

Global user address bounds and offset simulate translated user memory. Parallel state uses shared mmap rings/data, pipes, CPU affinity, `guest_virtio_device`, and notification counters.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The test is intentionally aggressive: it forces allocations through fake kmalloc pointers, depends on `/tmp/vringh_test-file`, assumes enough descriptors, and uses many assertions. Mapping math and slow one-byte ranges are the key correctness stressors.

## Test Signals

Run base mode with `--indirect`, `--eventidx`, `--virtio-1`, `--slow-range`; run `--parallel` with and without `--fast-vringh`; check no descriptor leaks, bad lengths, or notification hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vringh_test.c -->
