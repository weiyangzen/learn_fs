# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-vbi.c

## Purpose
Provides the videobuf2 queue operations for AU0828 raw VBI capture.

## Important APIs, types, and functions
`vbi_queue_setup()` sizes one plane as `vbi_width * vbi_height * 2`. `vbi_buffer_prepare()` validates plane capacity and sets payload. `vbi_buffer_queue()` stores the plane address/length in `struct au0828_buffer` and appends it to `dev->vbiq.active` under `dev->slock`. `au0828_vbi_qops` wires these callbacks to media-source enabling, shared analog stream start, and VBI-specific stop.

## Control flow and state
VBI buffers are queued independently from video buffers but share the analog ISO stream. `au0828-video.c` packet parsing fills `dev->isoc_ctl.vbi_buf` from the active queue and completes it on field boundaries or timeout.

## Dependencies and integration points
Depends on vb2-vmalloc, V4L2 media controller source enabling, `au0828_start_analog_streaming()`, and `au0828_stop_vbi_streaming()`.

## Risks and test signals
Risks are mismatched VBI size assumptions with `au0828-video.c`, shared stream user reference count imbalance between video and VBI queues, and queue operations after disconnect. Test signals include successful VBI `REQBUFS/QBUF/STREAMON`, periodic VBI buffers even on timeout, correct GREY VBI format reporting, and clean stop returning queued buffers with error.
