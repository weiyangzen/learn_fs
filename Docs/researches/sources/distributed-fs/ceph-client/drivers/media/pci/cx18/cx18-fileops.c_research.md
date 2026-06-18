# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-fileops.c

## Purpose
This file implements V4L2 file operations and capture read control for cx18 encoder streams. It owns open/close, stream claiming, read, poll, capture start/stop coordination, VBI insertion splice handling, radio open behavior, and audio mute/unmute helpers.

## Important APIs, Types, and Functions
Public functions include `cx18_claim_stream()`, `cx18_release_stream()`, `cx18_start_capture()`, `cx18_stop_capture()`, `cx18_v4l2_open()`, `cx18_v4l2_read()`, `cx18_v4l2_close()`, `cx18_v4l2_enc_poll()`, `cx18_vb_timeout()`, `cx18_mute()`, and `cx18_unmute()`. Internal helpers manage MDL dequeueing, user copies, sliced VBI MPEG private stream insertion, and dual-language stereo watching.

## Control Flow
Open serializes first-open firmware initialization and creates a `cx18_open_id`. Reads and polls lazily start capture, claim the target stream, and for MPEG also claim internal IDX or VBI streams depending on VBI insertion. DMA completions fill `q_full`; reads dequeue MDLs, byteswap/process VBI or MPEG when needed, copy buffers to userspace, and return drained MDLs to firmware. Close stops radio mode, releases vb2 ownership for YUV, stops capture, clears flags, and releases stream claims.

## State and Persistence
State is maintained in stream flags (`CLAIMED`, `STREAMING`, `APPL_IO`, `INTERNAL_USE`, `STREAMOFF`), stream owner IDs, MDL queues, VBI sliced MPEG ring data, capture counters, `search_pack_header`, radio flag, and open file handles. Everything is volatile.

## Dependencies and Integration Points
It depends on queue helpers, stream start/stop helpers, mailbox APIs, VBI processing, audio/video routing, V4L2 events, vb2 for YUV, and subdevice tuner/audio calls. ALSA PCM can claim/release shared streams through exported symbols.

## Risks and Edge Cases
MPEG VBI insertion depends on correctly finding Program Stream pack boundaries and is not valid for TS. Claim/release ordering must preserve internal IDX/VBI streams. Nonblocking reads, signals, EOS, and close while streaming share queue state. Radio open rejects switching during analog capture.

## Test Signals
Exercise blocking and nonblocking read, poll-triggered capture start, encoder stop at GOP end, close during active capture, MPEG reads with and without sliced VBI insertion, VBI single-frame reads, YUV vb2 timeout, and radio open/close transitions.
