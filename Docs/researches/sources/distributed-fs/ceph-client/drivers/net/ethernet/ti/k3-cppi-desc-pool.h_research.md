# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/k3-cppi-desc-pool.h

## Purpose
This header declares the opaque CPPI5 descriptor pool API implemented by `k3-cppi-desc-pool.c`. It is the public contract for drivers that allocate fixed-size coherent DMA descriptors.

## Important APIs, types, and functions
- `struct k3_cppi_desc_pool` is opaque to callers.
- `k3_cppi_desc_pool_create_name()` creates a named pool; `k3_cppi_desc_pool_create()` is a convenience macro using the device name.
- Destroy, CPU/DMA translation, allocation/free, available count, descriptor size, CPU base address, and sideband descriptor-info accessors are declared.

## Control flow
Callers create a pool, allocate descriptors, translate addresses as needed for hardware rings, optionally store sideband info by descriptor index, free descriptors, then destroy the pool.

## State and persistence behavior
The header owns no state. The implementation maintains coherent DMA memory and metadata until destroy.

## Dependencies and integration points
It includes Linux device and types headers and is consumed by TI networking or DMA clients needing CPPI descriptor pools.

## Risks and edge cases
- Because the pool is opaque, callers rely on API discipline for valid addresses and descriptor indices; the implementation does not enforce all bounds.
- The create macro hides the name argument, which is convenient but can make multi-pool diagnostics less clear unless callers use `_create_name()`.

## Test signals
Compile users against the declarations, verify symbol exports, and run pool allocation/free/translation tests through a client driver or KUnit-style harness.
