# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_mmu.h

## Purpose
Declares the public PowerVR MMU API and constants used by VM, firmware-context, and memory-binding code. It exposes device page-size and address-space assumptions while keeping the concrete MMU context and operation-context layouts private to `pvr_mmu.c`.

## Important APIs, types, and functions
- Constants: `PVR_DEVICE_PAGE_SIZE`, `PVR_DEVICE_PAGE_SHIFT`, `PVR_DEVICE_PAGE_MASK`, `PVR_PAGE_TABLE_ADDR_SPACE_SIZE`, `PVR_PAGE_TABLE_ADDR_BITS`, and `PVR_PAGE_TABLE_ADDR_MASK`.
- Opaque types: `struct pvr_mmu_context` and `struct pvr_mmu_op_context`.
- Flush APIs: `pvr_mmu_flush_request_all()` and `pvr_mmu_flush_exec()`.
- Context APIs: `pvr_mmu_context_create()`, `pvr_mmu_context_destroy()`, and `pvr_mmu_get_root_table_dma_addr()`.
- Operation APIs: `pvr_mmu_op_context_create()`, `pvr_mmu_op_context_destroy()`, `pvr_mmu_map()`, and `pvr_mmu_unmap()`.

## Control flow
The header has no runtime control flow. It defines the lifecycle expected by callers: create an MMU context, create one or more operation contexts around SG-backed map or unmap work, call map/unmap, destroy the operation context to sync and free staging resources, and execute MMU flushes before GPU work observes the changed mappings.

## State and persistence
No storage is defined in the header. Its constants make the current ABI assumption explicit: device pages track `PAGE_SIZE`, and the represented GPU virtual address space is 1 TiB. The opaque context pointers refer to persistent page-tree state managed by the implementation.

## Dependencies and integration points
Depends on Linux memory and type headers plus forward declarations for `pvr_device`, `pvr_vm_context`, and `sg_table`. It integrates with VM bind paths, GEM object mapping, firmware memory context creation, and queue submission paths that need pending MMU flushes completed before new jobs run.

## Risks
Changing the page-size or address-space constants affects page-table encoding, VM validation, firmware-visible root tables, and every caller's alignment assumptions. The opaque API keeps internals private, but callers must still obey page alignment and lifetime rules because the implementation does not defensively validate every address/index.

## Test signals
Build coverage catches signature and include drift. Runtime signals come from VM bind/unbind tests, firmware context boot with the root table DMA address, and job submission after map/unmap plus flush.
