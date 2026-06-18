# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-mmu.h

## Purpose
This header defines the IPU6 MMU public data structures and function prototypes used by the PCI parent and auxiliary ISYS/PSYS devices.

## Important APIs, Types, And Data
`ISYS_MMID` and `PSYS_MMID` identify the input and processing system MMUs. `struct ipu6_mmu_info` stores the software page tables, dummy mappings, aperture, page-size bitmap, spinlock, and back-pointer to the DMA mapping. `struct ipu6_mmu` stores hardware block descriptors, MMU id, page-table base, owning device, DMA mapping, VMA list, trash page/IOVAs, ready state, ready lock, and invalidate callback.

Declared APIs initialize/cleanup the MMU object, initialize/cleanup hardware, map/unmap ranges, and translate IOVA to physical address.

## Control Flow
The PCI parent creates MMU objects before auxiliary devices are added. Runtime PM resume calls hardware init; runtime suspend calls hardware cleanup. DMA allocation/mapping paths call `ipu6_mmu_map()` and `ipu6_mmu_unmap()`.

## State And Persistence
MMU state persists while the parent PCI device is bound. The hardware-ready flag is separate from allocated page-table state so runtime PM can stop hardware without destroying mappings.

## Dependencies And Integration Points
This header is consumed by IPU6 PCI, ISYS, and DMA code. It relies on hardware variant descriptors declared elsewhere and Linux spinlock/list/page types.

## Risks And Test Signals
Callers must not use `ipu6_mmu_iova_to_phys()` on unmapped ranges. Tests should validate lifetime ordering: no DMA map calls after cleanup, no hardware invalidation after suspend, and no leaks in probe error paths.
