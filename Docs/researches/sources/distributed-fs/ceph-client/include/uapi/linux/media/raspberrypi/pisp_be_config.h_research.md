# sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_be_config.h

## Purpose
Defines the Raspberry Pi PiSP back-end userspace ABI: packed configuration records for Bayer and RGB processing blocks, DMA buffer addresses, format metadata, AXI bus settings, crop/scale/output programming, HOG output, and tile descriptors. It is a hardware register and buffer contract rather than executable logic.

## Important APIs, Types, And Functions
Key exports include `pisp_be_global_config`, `pisp_be_config`, `pisp_tile`, and `pisp_be_tiles_config`. Enable masks split into `pisp_be_bayer_enable`, `pisp_be_rgb_enable`, and `pisp_be_dirty`. Processing structs cover DPC, GEQ, TDN, SDN, HDR stitch, CDN, LSC, CAC, debin, tonemap, demosaic, CCM, saturation, false colour, sharpen, gamma, CSC, downscale, resample, crop, output format, and HOG.

## Control Flow
Userspace populates `pisp_be_tiles_config`: global enable bits select which pipeline blocks are live, block structs provide register values, dirty flags indicate which sections need reprogramming, and each `pisp_tile` supplies per-tile offsets, crop margins, phases, output dimensions, and buffer offsets. Drivers validate alignment, dimensions, tile count, and enabled-block dependencies before submitting work.

## State, Persistence, And Dependencies
All state is explicit in packed UAPI structs and DMA addresses. Temporal denoise and stitch blocks add frame-to-frame persistence through TDN/stitch input and output buffers. The header depends on `linux/types.h` and `pisp_common.h`; all ABI layout depends on fixed-width integer sizes and packed attributes.

## Integration Points
Integrated with Raspberry Pi media/V4L2 ISP drivers and userspace camera algorithms that compute PiSP block parameters. It shares image format, compression, decompression, black-level, white-balance, and AXI structs with `pisp_common.h`, and its HOG/output branches align with downstream capture buffers.

## Risks
The ABI is dense and highly layout-sensitive. Risks include misaligned DMA addresses, stale dirty flags, tile count greater than 64, overflow in 16-bit tile dimensions/phases, invalid grid offsets into LSC/CAC LUTs, and userspace/kernel disagreement over packed struct layout. Buffer address arrays allow multi-plane formats, so plane count and stride validation are critical.

## Test Signals
Useful tests assert `sizeof`/offset stability, tile geometry bounds, alignment rules, enable/dirty mask handling, per-output branch independence, HOG output behavior, and successful rendering of edge tiles. Runtime signals include DMA faults, corrupted tile seams, invalid colour transforms, denoise history artifacts, and driver rejection of malformed configs.
