
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-video.c

## Purpose
`stk1160-video.c` owns STK1160 isochronous USB transfer allocation, completion handling, packet parsing, field interlacing, and copying captured video into queued vb2 buffers.

## Important APIs, Types, and Functions
Important functions are `stk1160_next_buffer()`, `stk1160_buffer_done()`, `stk1160_copy_video()`, `stk1160_process_isoc()`, `stk1160_isoc_irq()`, `stk1160_cancel_isoc()`, `stk1160_free_isoc()`, `stk1160_uninit_isoc()`, `stk1160_fill_urb()`, and `stk1160_alloc_isoc()`. The `debug` module parameter controls packet-level logging.

## Control Flow
`stk1160_alloc_isoc()` allocates up to `STK1160_NUM_BUFS` URBs, each with `STK1160_NUM_PACKETS` packet descriptors sized from the selected alternate setting. Submitted URBs complete in `stk1160_isoc_irq()`, which ignores unlink/shutdown statuses, processes packet data, clears packet status/length fields, and resubmits the URB. `stk1160_process_isoc()` walks each isochronous packet: `0xc0` starts a second field and can complete the previous frame, `0x80`/`0xc0` mark field parity and reset position, and data packets are copied into the current buffer. `stk1160_copy_video()` skips a 4-byte packet header and interlaces field lines into the destination based on the current odd/even field and line offset. When a frame completes, `stk1160_buffer_done()` sets sequence, field, timestamp, payload bytes, and marks the vb2 buffer done.

## State and Persistence
State lives in `dev->isoc_ctl`: current URB count, max packet size, per-URB transfer buffers, and the current partially filled `stk1160_buffer`. Per-buffer state tracks memory, length, bytes used, current position, and odd/even field. No state is persisted beyond active streaming.

## Dependencies and Integration Points
The file depends on Linux USB isochronous URB APIs, noncoherent USB transfer buffer allocation, vb2 buffer completion, and the queue/list state managed by `stk1160-v4l.c`. It uses endpoint `STK1160_EP_VIDEO`.

## Risks and Edge Cases
Packet parsing relies on first-byte field markers and can lose sync if the device emits unexpected packet headers. Copy code contains several bounds checks and ratelimited warnings; wrong standard/format settings can trigger out-of-bounds offsets or incomplete frames. Allocation can continue with fewer URBs only if at least `STK1160_MIN_BUFS` is available. URBs must be killed before freeing transfer buffers or clearing the current buffer.

## Test Signals
Test stable streaming with all supported alternate settings, frame sequence increments, correct field interlace ordering, bounds-warning absence under NTSC/PAL, behavior under USB packet errors (`-EOVERFLOW`, `-EPROTO`, `-EILSEQ`), partial URB allocation, URB cancellation on streamoff, and disconnect while completion callbacks are active.
