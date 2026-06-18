# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-video.c

## Purpose
`tw686x-video.c` implements the TW686x V4L2 video capture side. It registers one video device per hardware channel, manages videobuf2 queues, programs per-channel format/standard/input/framerate registers, implements three DMA strategies, and services video interrupts by completing and refilling P/B buffers.

## Important APIs, Types, And Functions
The file defines supported formats UYVY, RGB565, and YUYV through `struct tw686x_format`. DMA behavior is selected through `struct tw686x_dma_ops` instances: `memcpy_dma_ops`, `contig_dma_ops`, and `sg_dma_ops`. Key vb2 functions are `tw686x_queue_setup()`, `tw686x_buf_queue()`, `tw686x_buf_prepare()`, `tw686x_start_streaming()`, and `tw686x_stop_streaming()`. V4L2 ioctl handlers include `tw686x_g_fmt_vid_cap()`, `tw686x_try_fmt_vid_cap()`, `tw686x_s_fmt_vid_cap()`, `tw686x_s_std()`, `tw686x_querystd()`, `tw686x_s_parm()`, and input enumeration/setters. Externally visible functions are `tw686x_video_init()`, `tw686x_video_free()`, and `tw686x_video_irq()`.

## Control Flow
Video init chooses DMA ops from `dev->dma_mode`, registers `v4l2_device`, optionally sets up SG table sizing, initializes each `struct tw686x_video_channel`, programs NTSC/full-size/default input/default framerate, initializes vb2 and controls, allocates and registers a `video_device`, then writes global decoder/video-mode registers. When userspace streams, queued vb2 buffers move to `vidq_queued`; `start_streaming` refills both hardware P/B slots, schedules the core delayed DMA enable, and initializes sequence/parity. IRQ handling validates signal state, FIFO status, and expected P/B parity. A good IRQ calls `tw686x_buf_done()` and then the active DMA mode's `buf_refill()` for the same parity slot.

## State And Persistence
Per-channel state includes queued and current buffers, DMA descriptors, optional SG descriptor tables, V4L2 controls, current format, standard, dimensions, channel/input numbers, fps, sequence, current P/B slot, and no-signal state. State is volatile and protected by `vc->qlock` for queues and by `dev->lock` for shared device presence/DMA register state. Format and standard changes are rejected while the queue is busy.

## Dependencies And Integration Points
The file uses V4L2, videobuf2 vmalloc/contig/sg memory backends, Linux DMA mapping, and the core TW686x channel enable/disable functions. In memcpy mode, hardware writes to coherent internal buffers and data is copied into vmalloc-backed userspace buffers. In contiguous mode, hardware writes directly to vb2 DMA-contig buffers. In SG mode, per-frame descriptor tables are filled from vb2 DMA-SG scatterlists and pointed to by page-table registers.

## Risks
The SG path caps descriptor count at 256 and entry size at 4096 bytes; unsupported scatterlist shapes fail the buffer with `VB2_BUF_STATE_ERROR`. The memcpy path allocates two coherent frame buffers per channel and copies on IRQ, increasing memory bandwidth. Hot-unplug protection depends on checking `dev->pci_dev` under lock in queue/start/stop/free paths. Several operations return `-EBUSY` while streaming, so tests must cover userspace reconfiguration attempts. P/B parity mismatch or FIFO errors trigger channel resets, which are necessary but can drop frames.

## Test Signals
Exercise each pixel format, NTSC/PAL/SECAM standard changes, standard detection when idle, half/full width and height, frame interval requests, input switching, and stream-on/off. DMA mode matrix testing is essential: `dma_mode=memcpy`, `contig`, and `sg` should all produce monotonic timestamps/sequences and recover from no-signal/FIFO-error events. Hot-unplug or forced remove while buffers are queued should complete buffers with errors rather than dereferencing a stale PCI device.
