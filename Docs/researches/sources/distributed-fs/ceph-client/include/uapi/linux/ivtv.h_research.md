# sources/distributed-fs/ceph-client/include/uapi/linux/ivtv.h

## Purpose
`ivtv.h` defines private V4L2 ioctls and types for IVTV MPEG encoder/decoder hardware.

## Important APIs, Types, and Functions
`struct ivtv_dma_frame` carries a userspace buffer pointer, type, pixel format, and width/height for DMA frame operations. `IVTV_IOC_DMA_FRAME` submits a frame transfer. `IVTV_IOC_PASSTHROUGH_MODE` controls passthrough mode. Sliced VBI type macros alias V4L2 MPEG VBI constants.

## Control Flow
Userspace video applications call IVTV private ioctls through a V4L2 device. The driver copies or DMA-transfers frame data and toggles passthrough behavior for hardware paths.

## State and Persistence
Passthrough mode and device DMA state are driver-owned and persist while the device/session is configured. Frame buffers are transient.

## Dependencies and Integration Points
It includes `<linux/compiler.h>`, `<linux/types.h>`, and `<linux/videodev2.h>`. Integration points are V4L2, IVTV hardware drivers, MPEG capture/playback applications, and VBI data handling.

## Risks and Test Signals
Tests should cover pointer validation, DMA frame dimensions/format compatibility, private ioctl numbering relative to `BASE_VIDIOC_PRIVATE`, passthrough state changes, and VBI constant compatibility.
