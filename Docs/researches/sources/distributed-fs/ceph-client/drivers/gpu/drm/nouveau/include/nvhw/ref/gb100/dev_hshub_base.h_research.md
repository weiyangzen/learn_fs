# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb100/dev_hshub_base.h

## Purpose
Defines GB100 HSHUB register ranges and PCIe sysmem flush address registers for host system hub programming.

## Important APIs, Types, And Functions
Exports `NV_PFB_HSHUB0`, the generic `NV_PFB_HSHUB` range, and `NV_PFB_HSHUB_PCIE_FLUSH_SYSMEM_ADDR_{LO,HI}` plus `NV_PFB_HSHUB_EG_PCIE_FLUSH_SYSMEM_ADDR_{LO,HI}` address fields and masks.

## Control Flow
No executable flow exists. Driver code writes low/high address registers before using hardware flush paths.

## State And Persistence
No C state is stored. The target physical/sysmem flush address persists in HSHUB registers until reset or reprogramming.

## Dependencies And Integration Points
Integrated with framebuffer/host-memory coherency code and DRF helpers that pack the address fields.

## Risks
Address masks require 256-byte alignment and limit high address bits. Wrong programming can break PCIe flush completion or write to an unintended sysmem location.

## Test Signals
Host memory coherency tests, PCIe flush validation, suspend/resume register replay, and absence of timeout/error logs indicate correctness.
