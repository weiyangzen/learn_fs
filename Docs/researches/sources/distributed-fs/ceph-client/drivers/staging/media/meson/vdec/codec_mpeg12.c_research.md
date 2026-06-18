# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/codec_mpeg12.c

Purpose: this file implements MPEG-1/MPEG-2 codec operations for the Meson VDEC_1 firmware path. It programs canvases and firmware scratch registers, owns a small workspace, recycles capture buffers to firmware, handles display-aspect-ratio updates, signals EOS, and completes decoded frames from mailbox IRQs.

Important APIs and functions: `struct codec_mpeg12` stores the 128 KiB DMA workspace. `codec_mpeg12_start()` allocates that workspace, maps capture buffers to `AV_SCRATCH_0..7` canvases through `amvdec_set_canvases()`, writes workspace and command registers, clears error/wait state, and marks `keyframe_found`. `codec_mpeg12_can_recycle()` and `codec_mpeg12_recycle()` use `MREG_BUFFERIN` to return buffers to firmware. `codec_mpeg12_threaded_isr()` handles fatal error detection, frame-ready status, interlace field selection, DAR update, VIFIFO offset reading, and `amvdec_dst_buf_done_idx()` completion. `codec_mpeg12_eos_sequence()` returns a static MPEG sequence end code padded to 1 KiB.

Control flow: generic VDEC startup loads firmware through `vdec_1.c`, then calls `codec_mpeg12_start()`. The recycle thread returns freed capture buffer indices when `MREG_BUFFERIN` is clear. The hard ISR only wakes the thread. The threaded ISR clears mailbox status, checks `MREG_FATAL_ERROR`, reads `MREG_BUFFEROUT`, ignores an unclear all-ones marker, derives progressive/interlaced field from `MREG_PIC_INFO`, maps the low nibble buffer ID to a zero-based index, reads `MREG_FRAME_OFFSET`, and completes the matching capture buffer.

State and persistence: session-private workspace persists until `codec_mpeg12_stop()`. Firmware state persists in DOS scratch registers: sequence info, picture info, buffer-in/out mailboxes, command dimensions, workspace pointer, error counters, and frame offsets. The codec does not track a DPB list in software; firmware and the generic recycle path coordinate buffer ownership.

Dependencies and integration points: depends on `dos_regs.h`, V4L2 mem2mem/vb2 DMA, `vdec_helpers` for canvas setup, PAR setting, buffer completion, and abort. It is selected by platform format tables through `codec_mpeg12_ops`.

Risks: the ISR contains an "unclear what this means" condition for a special `MREG_BUFFEROUT` bit pattern, so behavior around that firmware status is not fully understood. `amvdec_set_canvases()` only maps the currently queued capture buffers, making queue setup/minimum buffer enforcement important. Fatal firmware errors abort both queues.

Test signals: MPEG-1 and MPEG-2 streams with progressive and interlaced pictures, DAR codes 4:3/16:9/2.21:1/default, EOS stop command, recycle pressure, fatal error injection, and capture queue sizes up to the eight scratch-register canvas slots used here.
