# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb10b/dev_fbhub.h

## Purpose
Defines GB10B FBHUB PCIe flush sysmem address registers.

## Important APIs, Types, And Functions
Exports `NV_PFB_FBHUB0_PCIE_FLUSH_SYSMEM_ADDR_LO` and `_HI` plus `ADR`, `ADR_INIT`, and `ADR_MASK` fields.

## Control Flow
No executable control flow. Consumers write the low/high halves of a flush target address.

## State And Persistence
The header has no software state. Register contents persist in hardware until changed or reset.

## Dependencies And Integration Points
Used by Nouveau memory/bar/fb coherency code on GB10B hardware with NVHW DRF accessors.

## Risks
High address width and low alignment masks must match the hardware. Incorrect masks can truncate or misalign the flush target.

## Test Signals
PCIe flush behavior, BAR/sysmem coherency checks, and hardware init logs are the relevant signals.
