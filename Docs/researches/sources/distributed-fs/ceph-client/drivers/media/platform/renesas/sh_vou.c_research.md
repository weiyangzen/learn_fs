# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/sh_vou.c

Purpose: legacy SuperH Video Output Unit platform driver. It exposes a V4L2 video-output device for analog output, manages a vb2 dma-contig queue, configures SuperH VOU registers, and drives an external I2C encoder subdevice using platform data.

Important APIs and functions: register helpers `sh_vou_reg_*`, vb2 ops `sh_vou_queue_setup()`, `sh_vou_buf_prepare()`, `sh_vou_buf_queue()`, `sh_vou_start_streaming()`, `sh_vou_stop_streaming()`, format/selection/std handlers, `sh_vou_isr()`, `sh_vou_hw_init()`, `sh_vou_open()`, `sh_vou_release()`, `sh_vou_probe()`, and `sh_vou_remove()`. Main state is `struct sh_vou_device`.

Control flow: probe validates platform data, maps MMIO, requests IRQ, registers a V4L2 device, initializes a vb2 output queue, binds an I2C encoder subdev, initializes hardware, then registers the video node. Open performs first-use runtime PM resume and hardware init. Streaming requires two queued buffers, programs mirror address banks for the first two frames, enables VSYNC interrupts, and turns the VOU on. The ISR acknowledges frame events, completes the active buffer, advances sequence/timestamp, and schedules the next queued buffer or reuses the current buffer when underrun would occur.

State and persistence: stores current pixel format, compose rectangle, standard, active buffer, queued list, status enum, and sequence. Register state persists across active use and is reset/reinitialized on first open. Geometry helpers choose supported scaling ratios and coordinate output crop/composition with the external encoder's pad format and selection.

Dependencies and integration: uses platform data from `media/drv-intf/sh_vou.h`, V4L2 common/device/ioctl/media-bus APIs, vb2 dma-contig, runtime PM, I2C subdev creation, and platform IRQ/MMIO resources.

Risks and test signals: risks include legacy platform-data assumptions, two-buffer minimum behavior, static variables in ISR diagnostics, hardcoded encoder bus code, incomplete PAL support, and close/open runtime PM ordering. Test with `v4l2-compliance`, write/MMAP/DMABUF output, NTSC/PAL standard switching where supported, compose selection changes, IRQ buffer churn, and encoder subdevice failure paths.
