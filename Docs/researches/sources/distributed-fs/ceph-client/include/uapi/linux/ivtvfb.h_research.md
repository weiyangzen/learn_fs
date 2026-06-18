# sources/distributed-fs/ceph-client/include/uapi/linux/ivtvfb.h

## Purpose
`ivtvfb.h` exports the framebuffer-side private ioctl for IVTV DMA frame updates.

## Important APIs, Types, and Functions
`struct ivtvfb_dma_frame` contains a userspace source pointer plus destination x/y coordinates. `IVTVFB_IOC_DMA_FRAME` uses V4L2 private ioctl numbering to request a framebuffer DMA update.

## Control Flow
Userspace passes a frame buffer and target position to the IVTV framebuffer device. The driver validates the pointer and coordinates, then transfers the frame into display memory.

## State and Persistence
Framebuffer contents persist in device memory until overwritten or mode reset. The UAPI structure is transient.

## Dependencies and Integration Points
It includes compiler, integer, and V4L2 definitions. It integrates with the IVTV framebuffer driver and video output pipelines.

## Risks and Test Signals
Tests should cover buffer pointer validation, coordinate clipping, ioctl number compatibility with IVTV video ioctls, and behavior while the framebuffer mode changes.
