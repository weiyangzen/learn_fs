# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-video.h

Purpose: declares the cx25821 video module interface and pulls in the kernel/V4L2 dependencies needed by the video implementation.

Important APIs and constants: defines `VIDEO_DEBUG`, a `dprintk` macro, `FORMAT_FLAGS_PACKED`, and prototypes for `cx25821_start_video_dma`, `cx25821_video_irq`, `cx25821_video_unregister`, and `cx25821_video_register`.

Control flow: core setup calls `cx25821_video_register`; teardown calls `cx25821_video_unregister` per channel; the PCI IRQ handler calls `cx25821_video_irq`; streaming uses `cx25821_start_video_dma` from the VB2 start path.

State and persistence: the header contains no state. Its prototypes operate on `struct cx25821_dev`, `struct cx25821_dmaqueue`, `struct cx25821_buffer`, and `struct sram_channel` defined in `cx25821.h`.

Dependencies and integration points: includes many kernel headers, `cx25821.h`, and V4L2 common/ioctl/event headers. It is included by `cx25821-core.c` and `cx25821-video.c`.

Risks: `dprintk` references a `dev` variable implicitly and checks constant `VIDEO_DEBUG`, so it is context-sensitive and not controlled by the runtime `video_debug` module parameter in `cx25821-video.c`. Broad includes increase compile coupling.

Test signals: compile coverage and base/video module linkage validate the declarations. Runtime tests for registration, IRQ, and streaming validate the API contract.
