# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-vbi.c

## Purpose

`cx231xx-vbi.c` implements raw VBI capture for the cx231xx V4L2 driver. It owns the VBI vb2 queue operations, bulk URB allocation and teardown for the VANC endpoint, URB completion handling, SAV/EAV parsing for VBI fields, and copying of VBI samples into userspace-visible videobuf2 buffers. The implementation mirrors the main analog video parser but only accepts VBI SAV markers and lays field 1 and field 2 data into a two-field raw VBI frame.

## Important APIs, Types, and Functions

The exported queue operations are `cx231xx_vbi_qops`, with `vbi_queue_setup()`, `vbi_buf_prepare()`, `vbi_buf_queue()`, `vbi_start_streaming()`, and `vbi_stop_streaming()`. These are installed on `dev->vbiq` by `cx231xx_register_analog_devices()` in `cx231xx-video.c`.

The URB lifecycle is exposed through `cx231xx_init_vbi_isoc()` and `cx231xx_uninit_vbi_isoc()`, both exported with `EXPORT_SYMBOL_GPL`. Despite the name, VBI uses bulk URBs through `usb_fill_bulk_urb()` on `dev->vbi_mode.end_point_addr`. The copy callback passed into initialization is normally `cx231xx_isoc_vbi_copy()`.

The parser and copy path is split across `cx231xx_isoc_vbi_copy()`, `cx231xx_get_vbi_line()`, `cx231xx_copy_vbi_line()`, `cx231xx_reset_vbi_buffer()`, `cx231xx_do_vbi_copy()`, and `cx231xx_is_vbi_buffer_done()`. It reuses shared SAV/EAV scanning helpers declared in `cx231xx.h` and implemented in `cx231xx-video.c`.

## Control Flow

When userspace starts VBI streaming, vb2 calls `vbi_start_streaming()`. The function resets the VBI DMA sequence and calls `cx231xx_init_vbi_isoc()` with `CX231XX_NUM_VBI_PACKETS`, `CX231XX_NUM_VBI_BUFS`, the VBI alternate packet size, and the VBI copy callback. Initialization first calls `cx231xx_uninit_vbi_isoc()` to clear previous URBs, clears endpoint halt, initializes parser counters in `dev->vbi_mode.vidq`, allocates arrays of URB pointers and transfer buffers, fills bulk URBs, submits them, and finally calls `cx231xx_capture_start(dev, 1, Vbi)`.

Each URB completion enters `cx231xx_irq_vbi_callback()`. Nonfatal statuses are logged, fatal unlink/shutdown statuses return, and successful completions take `dev->vbi_mode.slock`, invoke the configured bulk copy callback, release the lock, reset the URB status, and resubmit with `GFP_ATOMIC`.

`cx231xx_isoc_vbi_copy()` scans the transfer buffer for SAV/EAV sequences, including markers split over URB boundaries via `dma_q->partial_buf`. For VBI field markers, `cx231xx_get_vbi_line()` maps `SAV_VBI_FIELD1` and `SAV_VBI_FIELD2` to field numbers and delegates to `cx231xx_copy_vbi_line()`. Copying advances `bytes_left_in_line`, `lines_completed`, `current_field`, and `pos`; once all lines for field 2 are complete, `vbi_buffer_filled()` timestamps and completes the vb2 buffer.

## State and Persistence Behavior

Runtime state is held in `dev->vbi_mode`, particularly `bulk_ctl` and `vidq`. `bulk_ctl` persists URB arrays, transfer buffers, the active vb2 buffer pointer, packet size, and callback. `vidq` persists parser state across URBs: partial SAV bytes, current field, bytes left in line, completed lines, sequence number, and active buffer list. Device-level state such as `dev->norm` and `dev->width` determines VBI line count and buffer size. No on-disk persistence is used.

## Dependencies and Integration Points

This file depends on the cx231xx core for USB endpoint setup, `cx231xx_capture_start()`, and shared parser helpers. It depends on the V4L2/vb2 framework for buffer ownership and on `cx231xx-video.c` for VBI ioctl exposure and registration. It uses constants from `cx231xx-vbi.h` and `cx231xx-reg.h`, including PAL/NTSC VBI line ranges and VBI SAV marker values.

## Risks

Several paths assume nonzero URB payload length before copying the last four bytes into `partial_buf`; short or malformed URBs are a boundary-risk area. Parser state is protected by a spinlock in the URB callback, but open/close and stream teardown interact with URB killing and buffer completion, so regressions can produce use-after-free, double completion, or resubmission after disconnect. VBI size calculations use `dev->width` and norm-derived height; inconsistencies with the V4L2 VBI format constants can expose payload-size mismatches to userspace.

## Test Signals

Expected signals include successful `/dev/vbi*` registration, `VIDIOC_G_FMT` reporting correct PAL or NTSC line ranges, `v4l2-ctl --stream-mmap` or read streaming returning monotonically timestamped buffers, clean streamoff/open-close cycles, no URB resubmit errors after disconnect, and correct operation for both 525-line and 625-line norms. Tests should also exercise VBI capture after analog video streaming because both paths share device power, alternate settings, and parser helper code.
