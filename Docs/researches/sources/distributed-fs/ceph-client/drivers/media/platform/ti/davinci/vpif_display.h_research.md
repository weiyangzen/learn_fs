<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.h

## Purpose

This header defines local types and constants for the DaVinci VPIF display/output driver, including output channels, vb2 display buffers, shared per-channel queue state, selected output/subdevice state, and the device aggregate.

## Important APIs, types, and functions

- `VPIF_DISPLAY_VERSION`, device/object constants, VBI-related constants, and `VPIF_VALID_FIELD()` describe display capabilities.
- `enum vpif_channel_id` names display channel 2 and channel 3 from the display driver's local zero-based perspective.
- `struct video_obj` stores selected field, latest-only flag, standard, and DV timings.
- `struct vpif_disp_buffer`, `struct common_obj`, `struct channel_obj`, and `struct vpif_device` mirror the capture driver with output-specific naming and platform config.

## Control flow

No direct flow is implemented in the header. `vpif_display.c` allocates the structures at probe, initializes vb2 queues and video devices, and consumes them from ioctl, streaming, and ISR paths.

## State and persistence behavior

All fields are runtime-only. The `common_obj` queue and active/next frame pointers exist only while the driver is loaded and especially while streaming.

## Dependencies and integration points

It includes vb2 DMA-contig, V4L2 device, and common `vpif.h`, and references `struct vpif_display_config` from DaVinci media platform data.

## Risks and edge cases

`VPIF_NUMOBJECTS` is set to 1 because HBI/VBI support is not added, despite constants for VBI/HBI indices. Code that assumes three objects would be wrong. The valid field set must stay consistent with offset calculation in the implementation.

## Test signals

Compile coverage plus display runtime tests for both channels, field modes, queue initialization, output selection, and stream-on/off buffer cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.h -->
