# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-yuv.h

## Purpose
This header declares YUV playback helpers and hardware constants for cx23415 decoder memory and scaler filter tables.

## Important APIs, Types, and Functions
It defines `IVTV_YUV_BUFFER_UV_OFFSET`, filter-table offsets, update flags, exports `yuv_offset`, and declares YUV filter check, stream frame setup, userspace DMA frame transfer, frame completion, private DMA frame preparation, close, and deferred work handler functions.

## Control Flow
There is no standalone flow. Decode IRQ paths, ioctl handlers, stream fileops, and cleanup code call these functions to feed and display YUV frames.

## State and Persistence Behavior
The header stores no state. The implementation mutates `itv->yuv_info`, decoder registers, UDMA state, and YUV output flags.

## Dependencies and Integration Points
It depends on `struct ivtv`, `struct ivtv_dma_frame`, userspace pointers, and shared constants such as `IVTV_YUV_BUFFERS`. It integrates with IRQ, UDMA, ioctl, and framebuffer OSD tracking.

## Risks
Offset constants and update flags must stay synchronized with hardware and implementation assumptions. Callers must not use YUV helpers without decoder/output support.

## Test Signals
Build coverage, YUV DMA frame tests, vsync-driven display, OSD panning/tracking, filter checks, and cleanup after YUV playback validate this interface.
