<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.h

## Purpose

This header defines the shared data model and helper interfaces for the TI CAL driver: device, CAMERARX PHY, capture context, DMA queue, format metadata, register access wrappers, debug macros, constants, and cross-file function prototypes.

## Important APIs, types, and functions

- Constants describe context counts, CSI2 ports, CAMERARX pads, and DMA width/height limits.
- `struct cal_format_info` maps V4L2 fourcc, media-bus code, bits per pixel, and metadata flag.
- `struct cal_dmaqueue` tracks queued, pending, and active capture buffers plus DMA state and stop wait queue.
- `struct cal_camerarx`, `struct cal_dev`, and `struct cal_ctx` model one PHY, whole CAL subsystem, and one CSI2/pixel/DMA capture context respectively.
- Inline helpers `cal_read()`, `cal_write()`, `cal_read_field()`, `cal_write_field()`, and `cal_set_field()` centralize MMIO and bitfield access.
- Prototypes expose format lookup, CAMERARX lifecycle, CAL context lifecycle, and V4L2 video-node lifecycle.

## Control flow

The header has no executable driver flow by itself, but it encodes the object relationships used by the implementation. Probe creates a `cal_dev`, creates `cal_camerarx` PHYs, then creates `cal_ctx` instances that reference both. Video nodes use `cal_ctx`, while IRQ and runtime PM paths operate through `cal_dev` and `cal_camerarx`.

## State and persistence behavior

The declared structures are in-memory driver state only. The most important mutable state is the DMA queue and state machine, per-VC frame sequence counters, reserved pixel processors, selected format, and currently selected source subdevice. No persistent storage is defined.

## Dependencies and integration points

It pulls in Linux bitfield, I/O, list, mutex, spinlock, waitqueue, V4L2, media-device, V4L2 async/control/subdev/fwnode, and vb2 V4L2 headers. It is the contract between `cal.c`, `cal-video.c`, and `cal-camerarx.c`.

## Risks and edge cases

Because the register helper macros do plain read/modify/write without internal locking, callers must use appropriate context locks when shared registers can be touched concurrently. `cal_rx_pad_is_source()` accepts pads up to `CAL_CAMERARX_NUM_SOURCE_PADS`, which is the last source-pad index because pad zero is the sink. DMA state and buffer pointer invariants must be preserved by all users of `struct cal_dmaqueue`.

## Test signals

Compile coverage is the primary signal for this header, plus runtime tests that stress every structure field: format negotiation, media link setup, VC sequence handling, DMA queue transitions, and CAMERARX pad routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.h -->
