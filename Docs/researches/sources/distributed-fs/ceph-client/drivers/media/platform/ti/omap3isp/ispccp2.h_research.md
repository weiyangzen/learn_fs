# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccp2.h

## Purpose
`ispccp2.h` declares the CCP2 media subdevice contract used by the OMAP3 ISP core and `ispccp2.c`. It defines pad indexes, media-graph input/output state enums, cached hardware configuration structures, and the public CCP2 lifecycle/ISR functions.

## Important APIs, Types, And Functions
- Pad constants: `CCP2_PAD_SINK`, `CCP2_PAD_SOURCE`, and `CCP2_PADS_NUM`.
- Routing enums: `enum ccp2_input_entity` distinguishes no input, sensor input, and memory input; `enum ccp2_output_entity` distinguishes no output, CCDC output, and memory output placeholder.
- Cached register config: `struct isp_interface_lcx_config` stores CRC, data start/size, and format for logical channel configuration; `struct isp_interface_mem_config` stores memory-channel destination, dimensions, and offsets.
- Device state: `struct isp_ccp2_device` embeds the V4L2 subdev, media pads, active formats, routing state, video queue, PHY/regulator handles, stream state, wait queue, and stop atomic.
- Public functions expose initialization, cleanup, entity registration, entity unregistration, and interrupt handling.

## Control Flow
The header itself has no executable control flow. Its declarations enable the ISP core to initialize CCP2 during driver probe, register/unregister the CCP2 subdev during media-device setup/teardown, and dispatch CCP2 interrupts to `omap3isp_ccp2_isr()`.

## State And Persistence
The struct fields define all persistent in-kernel CCP2 state. There is no userspace ABI here beyond the V4L2/media behavior implemented by the C file. The header deliberately caches format and link state outside registers so stream configuration can be regenerated when links or formats change.

## Dependencies And Integration Points
It depends on V4L2 media-bus types and forward-declares `struct isp_device` and `struct isp_csiphy`. It is included by `ispccp2.c` and by ISP core code that owns `struct isp_device`.

## Risks And Edge Cases
The output enum contains `CCP2_OUTPUT_MEMORY`, but the implementation comments state CCP2 write-to-memory is not currently supported. Consumers must treat that enum as future-facing rather than implemented functionality. The `formats` array size is tied to `CCP2_PADS_NUM`; pad constants must remain consistent with media entity setup.

## Test Signals
Build coverage should catch mismatched function declarations and struct layout users. Runtime tests should verify that media links set `input` and `output` consistently with the enum values stored in this struct.
