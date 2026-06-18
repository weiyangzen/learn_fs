# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mmu.h

## Purpose
This header defines the SGX MMU software state structures and public MMU management API for the GMA500 driver.

## Important APIs, Types, and Functions
Key types are `struct psb_mmu_driver`, `struct psb_mmu_pd`, and `struct psb_mmu_pt`. The driver stores the rwsem/spinlock, flush flags, default PD, saved BIF control, clflush details, and DRM device pointer. A PD stores the hardware context, software PT table, directory page, dummy PT/page, PTE masks, and driver pointer. A PT stores parent PD, index, present-entry count, backing page, and temporary mapped virtual address. Function declarations mirror the implementation’s init/takedown, allocation/free, context binding, insert/remove, and flush APIs.

## Control Flow
There is no executable flow. The declarations define the sequence used by driver load: initialize driver, allocate optional pagefault PD, bind contexts, insert mappings, flush, then free on unload.

## State and Persistence Behavior
The structs are long-lived kernel driver state and contain both software-only pointers and hardware-visible page backing. Comments document the required lock ordering: take `psb_mmu_driver.sem` before the page-table spinlock.

## Dependencies and Integration Points
The header is included by `psb_drv.h`, `mmu.c`, and other GMA500 memory-management code. It depends on DRM device, page, semaphore, spinlock, and atomic types being available through included kernel headers.

## Risks
External code can directly inspect or misuse MMU internals because the structs are fully exposed. Violating the documented lock order or editing PT `count` outside the provided APIs can corrupt mappings or deadlock.

## Test Signals
Build-time consumers should resolve all MMU APIs, and lockdep/runtime testing should show no inversion between `sem` and `lock`. Mapping tests should observe state transitions through the exported functions rather than direct struct mutation.
