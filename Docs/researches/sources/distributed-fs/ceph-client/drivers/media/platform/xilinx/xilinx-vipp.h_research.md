# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.h

Purpose: declares the composite Xilinx Video IP device state shared by the composite driver and DMA helpers.

Important type: `struct xvip_composite_device` contains `v4l2_device`, `media_device`, parent device pointer, V4L2 async notifier, DMA channel list, and aggregate V4L2 capability bits for querycap.

Control flow/state: this header has no functions; `xilinx-vipp.c` initializes media/V4L2/notifier state and `xilinx-dma.c` consumes `xdev` to register DMA video nodes and expose caps.

Dependencies and integration: includes Linux list/mutex and media/V4L2 async/control/device headers. The primary risk is stale assumptions about ownership of `dmas` and `v4l2_caps`. Test signals are build coverage and composite probe/remove tests.
