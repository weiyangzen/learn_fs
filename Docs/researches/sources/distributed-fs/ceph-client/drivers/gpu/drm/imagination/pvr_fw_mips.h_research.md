# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_mips.h

## Purpose
Defines MIPS firmware private data used by the common firmware device state and MIPS backend.

## Important APIs, types, and functions
- `PVR_MIPS_PT_PAGE_COUNT` converts the firmware's maximum 4 KiB page-table footprint into host pages.
- `struct pvr_fw_mips_data` stores page-table pages, CPU page-table pointer, DMA mappings for each page, boot code/data/exception DMA addresses, cache policy, and PFN mask.

## Control flow
No executable control flow exists in the header. The macro handles host `PAGE_SIZE` differences at compile time.

## State and persistence
The struct is persistent processor-private firmware state under `pvr_fw_device.processor_data.mips_data`. It survives for the firmware lifetime and is used during boot wrapper setup and VM mapping.

## Dependencies and integration points
Depends on Rogue MIPS ABI constants, `asm/page.h`, and Linux math/types. Used by `pvr_fw_mips.c`, common firmware state, and MIPS VM helpers.

## Risks
The firmware assumes 4 KiB page-table granularity even when host pages are larger. Any mismatch in `ROGUE_MIPSFW_MAX_NUM_PAGETABLE_PAGES` or `ROGUE_MIPSFW_PAGE_SIZE_4K` changes allocation and DMA programming requirements.

## Test signals
Build coverage for different host page sizes and runtime MIPS firmware boot are the main signals. Page-table DMA values in boot data should map all firmware-required 4 KiB pages.
