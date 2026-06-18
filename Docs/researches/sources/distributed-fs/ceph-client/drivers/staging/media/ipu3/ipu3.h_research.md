# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3.h

## Purpose

This header defines the shared IPU3 ImgU driver model used by PCI, V4L2, CSS, DMA, and MMU code. It names queue/node topology, supported size limits, buffer wrappers, media-pipe structures, and driver-wide device state.

## Important APIs, Types, and Functions

Important constants include `IMGU_QUEUE_MASTER`, `IMGU_NODE_*`, `IMGU_NODE_NUM`, input/output min/max dimensions, and queue depth. Key structures are `imgu_vb2_buffer`, `imgu_buffer`, `imgu_node_mapping`, `imgu_video_device`, `imgu_v4l2_subdev`, `imgu_media_pipe`, and `imgu_device`. Prototypes expose node/queue mapping, buffer queueing, V4L2 registration, buffer completion, and stream control. `imgu_bytesperline()` calculates NV12 or RAW packed line stride.

## Control Flow

There is no executable flow beyond `imgu_bytesperline()`. The type layout shapes flows implemented in `ipu3.c` and `ipu3-v4l2.c`: video nodes own vb2 queues and buffer lists; media pipes own per-node state plus CSS dummy buffers; `imgu_device` owns the global CSS/MMU/V4L2/PM state.

## State and Persistence Behavior

The header defines persistent in-memory state for the lifetime of the PCI device and its registered media graph. Buffer wrappers bind vb2 buffers to CSS buffers and DMA maps. Per-pipe state tracks enabled queues, dummy buffers, media pipeline, subdevice rectangles, controls, and running mode.

## Dependencies and Integration Points

It includes Linux IOVA/PCI, V4L2 controls/devices, vb2 DMA-SG, and `ipu3-css.h`. It is the central integration header for `ipu3.c`, `ipu3-v4l2.c`, and support modules.

## Risks and Edge Cases

Several structures rely on first-member embedding for `container_of()` conversions. Node IDs, CSS queue IDs, and enabled pipe bits must remain aligned. The stride helper encodes hardware-specific raw packing assumptions.

## Test Signals

Compile coverage is the main header signal. Runtime signals include format setup across all nodes, queue/node mapping, vb2 buffer completion, and RAW/NV12 stride correctness across edge widths.
