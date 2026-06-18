# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/vmm.h

## Purpose
Declares the NVIF virtual memory manager wrapper and high-level VA allocation/map APIs.

## Important APIs, Types, And Functions
Defines VMM types `UNMANAGED/MANAGED/RAW`, get modes `ADDR/PTES/LAZY`, `nvif_vma`, `nvif_vmm`, page capability flags, constructor/destructor, `get/put/map/unmap`, and raw get/put/map/unmap/sparse helpers.

## Control Flow
Construction creates a VA space and discovers page capabilities. Clients allocate VA ranges, map memory objects, unmap, or use raw helpers for direct page-table operations.

## State And Persistence
VMM state stores address start/limit and page descriptors until destruction. VMA allocations and mappings persist until put/unmap.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/mem.h`, and `nvif/mmu.h`; used by buffer-object mapping, sparse memory, and channel resources.

## Risks
Address/size/page alignment, sparse reference balancing, and raw operation misuse can cause page faults or leaks.

## Test Signals
VA allocation/free, map/unmap, raw/sparse tests, and GPU page-fault monitoring validate behavior.
