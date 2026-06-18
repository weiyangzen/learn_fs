# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isppreview.h

## Purpose
`isppreview.h` defines the preview engine's public device structure, feature flags, pad constants, routing enums, image-processing parameter cache, and lifecycle/ISR APIs.

## Important APIs, Types, And Functions
- Control constants define brightness and contrast ranges, defaults, steps, and units.
- Feature bits extend the OMAP3 ISP preview ABI with `OMAP3ISP_PREV_CONTRAST`, `OMAP3ISP_PREV_BRIGHTNESS`, and `OMAP3ISP_PREV_FEATURES_END`.
- Routing constants define `enum preview_input_entity`, `PREVIEW_OUTPUT_RESIZER`, and `PREVIEW_OUTPUT_MEMORY`.
- `struct prev_params` stores all configurable preview processing blocks, feature/update/busy masks, and brightness/contrast values.
- `struct isp_prev_device` embeds V4L2 subdev, pads, formats, crop, control handler, routing state, video input/output nodes, double-buffered parameter state with spinlock, stream state, and stop synchronization.
- Public functions expose init/cleanup, entity registration, frame-sync ISR, main ISR, busy check, and context restore.

## Control Flow
This header defines the state consumed by `isppreview.c` and by ISP core IRQ/probe code. The core calls init/register during setup, dispatches preview interrupts and frame-sync interrupts at runtime, and calls cleanup/unregister during teardown.

## State And Persistence
The nested `params` object is the most important persistent state: two copies of `struct prev_params`, an active-bit mask selecting which copy owns each feature, and a spinlock. Formats, crop, input/output routing, and stream state persist between operations and drive register programming.

## Dependencies And Integration Points
It includes the OMAP3 ISP ABI, V4L2 controls, and `ispvideo.h`. It links the preview engine to media graph nodes, video queues, V4L2 control handling, and ISP core interrupt/context-management paths.

## Risks And Edge Cases
Feature bits must remain aligned with the `update_attrs` array in `isppreview.c`; adding a feature requires updating both. Output flags are bitmasks, and the implementation currently rejects multiple simultaneous output paths. `PREV_PADS_NUM` must match the formats/pads arrays and media entity setup.

## Test Signals
Build tests catch layout/prototype mismatches. Runtime tests should verify active/shadow parameter transitions, brightness/contrast control limits, media link state transitions, and that public ISR/context functions operate on the state fields declared here.
