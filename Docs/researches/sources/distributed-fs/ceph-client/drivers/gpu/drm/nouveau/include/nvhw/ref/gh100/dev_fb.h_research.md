# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_fb.h

## Purpose
Defines GH100 framebuffer hub sysmem flush-address registers and the NISO flush address shift.

## Important APIs, Types, And Functions
Exports `NV_PFB_NISO_FLUSH_SYSMEM_ADDR_SHIFT`, `NV_PFB_FBHUB_PCIE_FLUSH_SYSMEM_ADDR_LO`, `_HI`, and the high address mask.

## Control Flow
No control flow. Consumers program address halves before triggering or relying on FBHUB PCIe flush behavior.

## State And Persistence
No C state. Register state persists in the framebuffer hub while the GPU is initialized.

## Dependencies And Integration Points
Used by memory-management/coherency code and `nvkm_rd32/wr32` plus DRF helpers.

## Risks
Wrong address shifting or high mask truncation can invalidate host flush completion.

## Test Signals
FB coherency tests, BAR flushing behavior, and GH100 initialization/suspend-resume logs are the key signals.
