# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_dec.c

## Purpose
This file implements the decoder-facing V4L2 ioctl, control, and vb2 queue behavior for the Samsung MFC driver. It maps user-visible compressed and raw formats to firmware codec modes, controls decoder setup, manages OUTPUT/CAPTURE buffer requests, handles EOS commands and source-change events, and feeds queued buffers into the core scheduler.

## Important APIs, Types, and Functions
Static data includes the decoder `formats[]` table and decoder controls. Important helpers are `find_format()`, `s5p_mfc_ctx_ready()`, V4L2 ioctl handlers for querycap, enum/g/s/try format, reqbufs, querybuf, qbuf, dqbuf, expbuf, streamon/off, selection, decoder command, event subscribe, decoder control get/set, and vb2 ops: `s5p_mfc_queue_setup()`, `s5p_mfc_buf_init()`, `s5p_mfc_start_streaming()`, `s5p_mfc_stop_streaming()`, and `s5p_mfc_buf_queue()`. Exported accessors return decoder codec ops, queue ops, ioctl ops, set up/delete controls, and initialize default formats.

## Control Flow
The decode path starts with `S_FMT` on OUTPUT selecting compressed codec and setting `MFCINST_INIT`. OUTPUT `REQBUFS` opens a firmware instance. Header parse occurs when a source buffer is queued and the context is ready. After `SEQ_DONE`, CAPTURE format and min buffers become available. CAPTURE `REQBUFS` allocates DPB/codec buffers, queues init buffers, and waits for `INIT_BUFFERS_RET`. Streaming and buffer queue callbacks add buffers to internal queues, set work bits when `s5p_mfc_ctx_ready()` is true, and call `try_run`. `V4L2_DEC_CMD_STOP` marks EOS on the last source buffer or enters finishing state when the source queue is empty. DQBUF emits `V4L2_EVENT_EOS` when the finished EOS capture buffer is dequeued.

## State and Persistence Behavior
The file mutates `ctx->src_fmt`, `dst_fmt`, `codec_mode`, `dec_src_buf_size`, `state`, queue states, source/destination buffer arrays, queue counts, DPB counts, `dec_dst_flag`, display-delay controls, loop-filter and slice-interface flags, and default format selections. It uses vb2 queue state and V4L2 control state but writes no persistent storage.

## Dependencies and Integration Points
It integrates with V4L2 ioctl/event/control APIs, vb2 DMA-contig, core scheduler work bits, firmware control (`s5p_mfc_open_mfc_inst()`), hardware operations (`alloc_codec_buffers`, `release_codec_buffers`, `try_run`), PM clocks, and interrupt wait helpers.

## Risks
State validation is strict and easy to regress: CAPTURE buffers are valid only after header parse, OUTPUT buffers only after format init, and only MMAP memory is accepted for decoder queues. Resolution-change flow depends on core IRQ state transitions. Stop-streaming can wait for a frame interrupt while holding/releasing locks, so lock ordering is important. Format version masks must match firmware capabilities.

## Test Signals
Signals include format enumeration per hardware version, invalid format rejection, header-parse wait before CAPTURE format/min-buffers, buffer count clamping, DPB allocation failure cleanup, EOS event delivery, resolution-change source-change events, streamoff while running, and decode for H.264, MPEG2, MPEG4/H263, VC1, VP8, HEVC, and VP9 where version-gated.
