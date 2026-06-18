<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/initramfs_data.S -->
# sources/distributed-fs/ceph-client/usr/initramfs_data.S

## Purpose

`initramfs_data.S` embeds the generated initramfs binary blob into the kernel image and exposes its size for early boot code.

## Important APIs, Types, and Functions

Source size: 36 lines, 1243 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Assembler places `.incbin "usr/initramfs_inc_data"` between start/end labels in `.init.ramfs`, then emits `__initramfs_size` in `.init.ramfs.info` as a 32-bit or 64-bit quantity.

## State and Persistence Behavior

Persistent state is the linked initramfs bytes and size symbol in the kernel image. Runtime unpacking is performed by early userspace/initramfs code elsewhere.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Missing generated `initramfs_inc_data`, assembler `.incbin` support, wrong section flags, or size-width mismatch can break boot image construction.

## Test Signals

Build kernels with empty, uncompressed, and compressed initramfs inputs on 32-bit and 64-bit configurations; inspect symbols and boot unpacking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/initramfs_data.S -->
