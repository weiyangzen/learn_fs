# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-vbi.c

## Purpose
`cx88-vbi.c` implements V4L2 vertical blanking interval capture for cx8800 analog video devices. It defines VBI format negotiation, videobuf2 queue operations, RISC program creation, VBI DMA start/stop, and queue restart.

## Important APIs, Types, And Functions
Externally used functions are `cx8800_vbi_fmt()`, `cx8800_stop_vbi_dma()`, `cx8800_restart_vbi_queue()`, and exported `cx8800_vbi_qops`. Internal helpers are `cx8800_start_vbi_dma()`, `queue_setup()`, `buffer_prepare()`, `buffer_finish()`, `buffer_queue()`, `start_streaming()`, and `stop_streaming()`.

## Control Flow
Format negotiation returns fixed grey samples with `VBI_LINE_LENGTH`, offset 244, and NTSC/PAL-specific sampling rate, start lines, and line counts. Buffer setup selects a single plane sized to line count times line length times two fields. `buffer_prepare()` validates plane size, sets payload, and builds a RISC program with `cx88_risc_buffer()`. Queued buffers are linked into `dev->vbiq.active`; the first loops to itself and later buffers patch the previous RISC jump to chain DMA. Streaming starts by programming SRAM channel 24, enabling VBI capture bits in `MO_VBOS_CONTROL` and `VID_CAPTURE_CONTROL`, enabling video interrupts, and starting VBI DMA. Stop paths clear capture/DMA/interrupt bits and return active buffers with `VB2_BUF_STATE_ERROR`.

## State, Persistence, And Dependencies
State lives in `dev->vbiq`, `dev->vb2_vbiq`, buffer RISC memory, and hardware counters/registers. The output is transient DMA data delivered through vb2 buffers. Dependencies include `cx88_risc_buffer()`, `cx88_sram_channel_setup()`, `cx88_wakeup()` in the video IRQ path, V4L2 standards, and DMA coherent allocation for RISC programs.

## Integration Points
`cx88-video.c` registers the VBI video device, initializes the vb2 queue with these ops, routes VBI ioctls to `cx8800_vbi_fmt()`, handles VBI RISC1 interrupts in `cx8800_vid_irq()`, and restarts VBI after resume.

## Risks
`start_streaming()` assumes at least one queued buffer because vb2 min queued buffers are configured in the video driver. Video and VBI share `MO_VID_DMACNTRL` and video interrupt masks, so stop paths must not inadvertently disrupt another active stream beyond intended shared bits. Line counts depend on current `core->tvnorm`; changing standards while queues are busy is guarded elsewhere.

## Test Signals
Use VBI capture on NTSC and PAL norms, verify buffer sizes and timestamps, confirm no active buffers remain after streamoff, test suspend/resume with VBI active, and check VBI RISC1 interrupt completions through `MO_VBI_GPCNT`.
