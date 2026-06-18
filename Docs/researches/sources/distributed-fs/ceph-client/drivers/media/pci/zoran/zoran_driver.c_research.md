# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_driver.c

## Purpose
`zoran_driver.c` implements the user-facing V4L2 and videobuf2 logic for the Zoran driver. It defines supported capture formats, ioctl handlers for format/norm/input/crop negotiation, and vb2 queue operations that start, stop, queue, prepare, and complete buffers for raw or MJPEG capture/playback modes.

## Important APIs, Types, And Functions
The exported data object is `zoran_formats[]`, including RGB555/565, BGR24/32, YUYV, UYVY, and MJPEG. Important helpers are `zoran_v4l2_calc_bufsize()`, `zoran_v4l_set_format()`, `zoran_set_norm()`, `zoran_set_input()`, `zoran_enum_fmt()`, `zoran_try_fmt_vid_out()`, `zoran_try_fmt_vid_cap()`, `zoran_s_fmt_vid_out()`, `zoran_s_fmt_vid_cap()`, selection handlers, `zr_set_buf()`, vb2 ops, `zoran_queue_init()`, and `zoran_queue_exit()`. `zoran_template` wires file and ioctl ops to the V4L2 video device.

## Control Flow
Userspace opens the V4L2 device, negotiates format and controls, requests vb2 buffers, queues them, and starts streaming. Non-MJPEG format selection sets `map_mode = ZORAN_MAP_MODE_RAW`; MJPEG selection sets a JPEG map mode and recalculates compression settings/buffer size. `zr_vb2_start_streaming()` clears status rings and `inuse[]`, restarts/reinitializes hardware, then either starts raw memory grab or configures JPEG mode, feeds queued buffers, starts the codec, and enables interrupts. `zr_set_buf()` completes the previous raw buffer, pulls a new queued buffer, programs top/bottom DMA target registers, and arms frame grab. Stop disables interrupts, idles JPEG/raw hardware, returns in-use and queued buffers with errors, disables PCI mastering, and resets map mode to raw.

## State And Persistence
This file mutates `zr->v4l_settings`, `zr->jpg_settings`, `zr->buffer_size`, `zr->map_mode`, `zr->running`, `zr->vbseq`, `zr->queued`, `zr->prepared`, `zr->buf_in_reserve`, `zr->inuse[]`, and `queued_bufs`. The V4L2 lock serializes ioctl/queue operations, while `queued_bufs_lock` protects the buffer list.

## Dependencies And Integration Points
It depends on V4L2 ioctl2, vb2 DMA-contig, PCI DMA addresses, low-level hardware operations from `zoran_device.c`, card validation/default helpers from `zoran_card.c`, and register definitions via `zoran.h`. External users see standard V4L2 capture ioctls and streaming buffer operations.

## Risks
The file comments say output is temporarily disabled, but MJPEG map modes still distinguish record/play naming in code, so mode naming is easy to misread. Two TODOs note TRY_FMT behavior for invalid pixelformats returns `-EINVAL` instead of substituting a default. Empty raw queues call `vb2_queue_error()`. Format/norm/input changes are rejected while `zr->running != ZORAN_MAP_MODE_NONE`, and tests should cover that. `zoran_v4l_set_format()` compares requested size to `zr->buffer_size` immediately after assigning it, making that availability check redundant.

## Test Signals
V4L2 compliance tests should cover format enumeration, TRY/S_FMT for raw and MJPEG, invalid formats, standard/input changes while idle and busy, crop selection only in compressed mode, vb2 MMAP/DMABUF streaming, empty queue errors, and stop cleanup. Runtime capture should show monotonic timestamps and sequences with correct payload sizes.
