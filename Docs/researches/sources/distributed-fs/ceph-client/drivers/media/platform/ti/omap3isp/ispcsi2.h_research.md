# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsi2.h

## Purpose
`ispcsi2.h` defines the CSI-2 receiver data model, format/event constants, pad constants, output flags, and public functions used by the OMAP3 ISP core and CSI-2 implementation.

## Important APIs, Types, And Functions
- Format IDs: `enum isp_csi2_pix_formats` lists hardware context format encodings for YUV422, RAW10, RAW8, DPCM decompression, video-port output, and user-defined data.
- IRQ enums: `enum isp_csi2_irqevents` and `enum isp_csi2_ctx_irqevents` describe top-level and context-specific interrupt bits.
- Config structs: `struct isp_csi2_ctx_cfg`, `struct isp_csi2_timing_cfg`, and `struct isp_csi2_ctrl_cfg` mirror context, timing, and receiver-control registers.
- `struct isp_csi2_device` embeds subdev/pads/formats/video node, hardware resource IDs, output bitmask, DPCM/frame-skip state, PHY pointer, context/timing/control config, stream state, and stop wait primitives.
- Public functions cover ISR, reset, init/cleanup, and entity registration.

## Control Flow
The header has no executable flow but defines the state consumed by `ispcsi2.c`. The ISP core can allocate two instances, CSI2A and CSI2C, assign register resources, and hand each to lifecycle or IRQ functions.

## State And Persistence
The header defines persistent CSI-2 state that survives between stream operations: active media-bus formats, context configuration, output mode, frame skipping, and video-node state. Hardware registers are treated as derived state and are reprogrammed from these fields.

## Dependencies And Integration Points
It depends on Linux integer/V4L2 types and forward-declares `struct isp_csiphy`. It is coupled to `ispreg.h` bit definitions through shared register-field meanings and to `ispvideo`/media entity infrastructure through embedded fields.

## Risks And Edge Cases
`ISP_CSI2_MAX_CTX_NUM` is set to 7 and the array allocates eight contexts, but the implementation currently uses context 0 only. Output flags are bitmasks and must be updated atomically enough under media graph setup assumptions. Hardware format IDs are non-obvious constants, so adding formats requires matching the implementation mapping table.

## Test Signals
Compile-time users should catch struct and prototype mismatches. Runtime tests should verify context 0 register programming matches the cached `struct isp_csi2_ctx_cfg`, and that output bitmasks drive `vp_only_enable` and `vp_clk_enable` correctly.
