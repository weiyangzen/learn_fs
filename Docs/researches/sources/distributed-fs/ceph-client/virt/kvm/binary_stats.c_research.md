<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/binary_stats.c -->
# sources/distributed-fs/ceph-client/virt/kvm/binary_stats.c

## Purpose

Common reader for KVM binary stats file descriptors. It exposes a contiguous virtual file layout containing header, id string, descriptor array, and raw stats data.

## Important APIs, Types, and Functions

Source size: 144 lines, 4604 bytes. Functions/classes: kvm_stats_read. Includes: linux/kvm_host.h, linux/kvm.h, linux/errno.h, linux/uaccess.h.

## Control Flow and Data Flow

`kvm_stats_read()` computes the available length from the current offset, then conditionally copies each region in order with offset-aware slicing and advances the file offset.

## State and Persistence Behavior

The function does not own stats storage; it reads caller-provided id/header/descriptors/data. Persistent state is the userspace fd offset and the underlying KVM stats memory.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Offset math must not overrun the descriptor or data regions. A partial `copy_to_user()` returns `-EFAULT` after prior bytes may have been copied. Header offsets must match the actual layout.

## Test Signals

pread/read header-only, id-only, descriptor-only, data-only, unaligned cross-boundary reads, EOF reads, and injected user-copy faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/binary_stats.c -->
