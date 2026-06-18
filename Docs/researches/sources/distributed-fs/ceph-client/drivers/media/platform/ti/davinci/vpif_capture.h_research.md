<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.h

## Purpose

This header defines the DaVinci VPIF capture driver's local data structures and constants for capture channels, video state, vb2 buffers, common DMA queue state, channel objects, and the device aggregate.

## Important APIs, types, and functions

- `VPIF_CAPTURE_VERSION`, channel/object count constants, and `VPIF_VALID_FIELD()` define capture capabilities.
- `enum vpif_channel_id` names capture channel 0 and channel 1.
- `struct video_obj` stores selected field, standard, and DV timings.
- `struct vpif_cap_buffer` wraps `vb2_v4l2_buffer` with a DMA queue list node.
- `struct common_obj` stores active/next buffers, format, vb2 queue, DMA queue, lock, address callback, offsets, width, and height.
- `struct channel_obj` and `struct vpif_device` aggregate video node, input/subdev selection, VPIF parameters, channels, V4L2 device, subdevices, async notifier, and platform config.

## Control flow

The header has no direct control flow. `vpif_capture.c` allocates and fills these structures during probe, updates them through ioctl calls, and uses them in vb2 and ISR paths.

## State and persistence behavior

All declared state is runtime memory. Buffer pointers and queue links are transient during streaming; selected input and format reset to defaults after driver reload.

## Dependencies and integration points

It includes vb2 DMA-contig, V4L2 device, and common `vpif.h`. It also depends on platform-data types referenced through `struct vpif_capture_config`.

## Risks and edge cases

The common object holds both synchronization primitives and hardware address callback state; incorrect initialization can break streaming. The valid-field macro admits `ANY`, `NONE`, `INTERLACED`, `SEQ_TB`, and `SEQ_BT`, so offset calculations must match every accepted case.

## Test signals

Compile coverage and runtime capture tests that allocate buffers, switch fields, change inputs, and run both capture channels are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.h -->
