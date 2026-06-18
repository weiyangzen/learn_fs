# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-vbi.h

## Purpose

`cx231xx-vbi.h` is the public internal header for cx231xx raw VBI capture. It declares the VBI vb2 queue operations, PAL/NTSC VBI geometry constants, VBI URB sizing constants, and parser/copy functions implemented by `cx231xx-vbi.c`.

## Important APIs, Types, and Constants

`extern struct vb2_ops cx231xx_vbi_qops` is the main object consumed by analog device registration. The VBI geometry constants define NTSC lines 10-21 and PAL lines 6-23, with `NTSC_VBI_LINES` and `PAL_VBI_LINES` computed from the start/end pairs. `VBI_STRIDE` and `VBI_SAMPLES_PER_LINE` are fixed at 1440, while `CX231XX_NUM_VBI_PACKETS` and `CX231XX_NUM_VBI_BUFS` size the VBI USB transfer ring.

The function declarations expose the stream lifecycle (`cx231xx_init_vbi_isoc()`, `cx231xx_uninit_vbi_isoc()`), line parser (`cx231xx_get_vbi_line()`), copy helpers (`cx231xx_copy_vbi_line()`, `cx231xx_do_vbi_copy()`), parser reset (`cx231xx_reset_vbi_buffer()`), and completion predicate (`cx231xx_is_vbi_buffer_done()`).

## Control Flow

The header has no control flow, but it defines the call graph boundary. `cx231xx-video.c` registers `cx231xx_vbi_qops`; vb2 then calls into `cx231xx-vbi.c`. The URB callback path invokes the parser functions declared here to reconstruct VBI buffers.

## State and Persistence Behavior

No state is stored in the header. The constants encode the driver's expected VBI layout and therefore act as a stable contract among V4L2 format reporting, vb2 queue sizing, and the byte-copy path. State lives in `struct cx231xx_video_mode`, `struct cx231xx_dmaqueue`, and `struct cx231xx_bulk_ctl` from `cx231xx.h`.

## Dependencies and Integration Points

The prototypes require `struct cx231xx`, `struct cx231xx_dmaqueue`, and `struct urb` definitions from included kernel and driver headers. It is included by both VBI implementation and analog video registration. It depends on V4L2/vb2 semantics because `cx231xx_vbi_qops` is installed directly into a `struct vb2_queue`.

## Risks

Mismatch between `VBI_LINE_LENGTH` in `cx231xx.h`, `VBI_STRIDE`/`VBI_SAMPLES_PER_LINE` here, and the copy logic in `cx231xx-vbi.c` would produce incorrect payload sizes or line placement. The header exposes implementation functions broadly inside the driver, so callers must respect the locking and parser-state assumptions used by the URB callback.

## Test Signals

Build coverage should catch missing declarations and type drift. Runtime signals include correct VBI device registration, buffer sizes matching the reported V4L2 raw VBI format, and successful PAL/NTSC VBI streaming without queue errors.
