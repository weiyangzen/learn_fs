# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc.h

## Purpose
`microchip-isc.h` is the shared private interface for Microchip ISC/XISC drivers. It defines common clock, buffer, async subdevice, format, pipeline, controls, register-offset, and device-state structures plus exported common helper prototypes.

## Important APIs, Types, and Functions
Important types include `struct isc_clk`, `struct isc_buffer`, `struct isc_subdev_entity`, `struct isc_format`, `struct fmt_config`, `struct isc_ctrls`, `struct isc_reg_offsets`, and `struct isc_device`. Pipeline bit masks describe DPC, WB, CFA, CC, GAM, VHXS, CSC, CBC, and subsampling stages. Exported prototypes include interrupt handling, pipeline initialization, clock initialization/cleanup, async ops, scaler initialization/linking, media-controller initialization/cleanup, and format lookup.

## Control Flow
Product drivers allocate and fill `struct isc_device`, selecting format arrays, register offsets, maximum dimensions, DMA burst settings, clock requirements, and callback hooks. Common code then uses this structure for V4L2 format negotiation, media graph registration, streaming, DMA queuing, AWB, and clock/pipeline programming.

## State and Persistence
`struct isc_device` is the central runtime state object. It persists while the platform device is bound and contains volatile kernel state for formats, controls, current buffers, media graph entities, locks, completion, and hardware callback configuration. Nothing is persisted across driver removal.

## Dependencies and Integration Points
The header depends on Linux clock-provider, platform-device, V4L2 control/device, and vb2 DMA-contig APIs. It ties together `microchip-isc-base.c`, `microchip-isc-clk.c`, `microchip-isc-scaler.c`, and the SAMA5D2/SAMA7G5 product drivers.

## Risks and Edge Cases
The anonymous callback struct in `struct isc_device` is a tight contract: product drivers must populate every callback used by `isc_set_pipeline()` and control initialization. Locking fields have distinct purposes and should not be collapsed. Format arrays mix input media-bus formats and output pixel formats, so code must use the correct size and pointer pair.

## Test Signals
Compile both product drivers, run probe/remove with clocks and subdevices present, validate all callbacks are set before streaming, and exercise the exported helper calls through ISC and XISC module loads.
