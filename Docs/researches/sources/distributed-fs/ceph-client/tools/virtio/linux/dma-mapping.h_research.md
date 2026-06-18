<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/dma-mapping.h -->
# sources/distributed-fs/ceph-client/tools/virtio/linux/dma-mapping.h

## Purpose

`dma-mapping.h` is a header for the local userspace/kernel-test compatibility layer or exported build shim. It provides includes (none), macros (_LINUX_DMA_MAPPING_H, dma_alloc_coherent, dma_free_coherent, dma_map_page, dma_map_page_attrs, dma_map_single, dma_map_single_attrs, dma_mapping_error, dma_unmap_single, dma_unmap_page, dma_unmap_page_attrs, sg_dma_address, plus 7 more), and declarations needed by nearby C sources without pulling in full kernel internals.

## Important APIs, Types, and Functions

Source size: 63 lines, 2157 bytes. Macros/defines: _LINUX_DMA_MAPPING_H, dma_alloc_coherent, dma_free_coherent, dma_map_page, dma_map_page_attrs, dma_map_single, dma_map_single_attrs, dma_mapping_error, dma_unmap_single, dma_unmap_page, dma_unmap_page_attrs, sg_dma_address, sg_dma_len, dma_need_sync, dma_unmap_single_attrs, dma_sync_single_range_for_cpu, dma_sync_single_range_for_device, dma_max_mapping_size, plus 1 more.

## Control Flow and Data Flow

There is no standalone control flow. Included macros and inline helpers are expanded into userspace tests or kernel build units at compile time.

## State and Persistence Behavior

State is either absent or stored in caller-owned structs and globals. Header-defined wrappers often model kernel primitives over libc, pthreads, eventfd-safe memory, or direct include forwarding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio/linux`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Stub semantics may diverge from in-kernel behavior. Macro-only APIs can hide type/ordering bugs, and include-forwarding paths can break when the kernel tree layout changes.

## Test Signals

Compile all dependent virtio, ringtest, vhost, and initramfs header-test targets with warnings enabled; run the corresponding runtime tests where the header models synchronization or memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/linux/dma-mapping.h -->
