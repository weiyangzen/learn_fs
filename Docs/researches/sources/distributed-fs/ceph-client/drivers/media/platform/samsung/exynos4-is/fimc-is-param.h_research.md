# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-param.h

## Purpose
`fimc-is-param.h` defines the FIMC-IS firmware parameter-region ABI, including parameter bit numbers, timeout and default capture constants, control/format/error values, packed parameter structures, tuning/EXIF/frame/face/shared-memory structures, and parameter helper prototypes.

## Important APIs, Types, and Functions
Important definitions include `FIMC_IS_CONFIG_TIMEOUT`, default frame sizes/rates, `FIMC_IS_REGION_VER`, `FIMC_IS_MAGIC_NUMBER`, `FIMC_IS_PARAM_MAX_SIZE`, `enum is_param_bit`, FIMC-IS interrupt numbers, OTF/DMA/control command values, ISP 3A/flash/AWB/effect/ISO/adjust/metering/AFC constants, and FD configuration constants. Packed ABI types include `struct param_control`, `param_otf_input`, `param_dma_input`, `param_otf_output`, `param_dma_output`, all ISP/FD/scaler parameter structs, `struct is_param_region`, `struct is_region`, `struct is_share_region`, and `struct sensor_open_extended`.

## Control Flow
There is no executable control flow, but the layout controls how `fimc-is-param.c` copies 64-byte parameter entries and how firmware interprets the DMA-shared `struct is_region`.

## State and Persistence
The header defines volatile shared-memory state exchanged with firmware. The driver allocates the region in coherent DMA memory; the ABI fields persist only while the driver and firmware session are active.

## Dependencies and Integration Points
The header is included by the FIMC-IS core, parameter update code, ISP subdevice controls, and register command layer. It depends on packed structure layout remaining compatible with the firmware blob and setfile.

## Risks and Edge Cases
Packed structure sizes and reserved arrays must keep each parameter block at `FIMC_IS_PARAM_MAX_SIZE`; accidental field changes can corrupt following firmware fields. `FIMC_IS_PARAM_SIZE` is based on `FIMC_IS_REGION_SIZE + 1`, which should not be confused with a byte-exact struct size. The ABI includes many blocks not fully manipulated by current code, so unused constants may be firmware-facing but untested. FD bits cross the first 32-bit dirty bitmap boundary.

## Test Signals
Use compile-time size/offset checks where possible, firmware boot magic-number validation, successful initial parameter upload, frame/face metadata interpretation, DMA2 output address array offset use by ISP video, shared-region firmware version/debug data, and failure injection for invalid OTF/DMA/FD parameter values.
