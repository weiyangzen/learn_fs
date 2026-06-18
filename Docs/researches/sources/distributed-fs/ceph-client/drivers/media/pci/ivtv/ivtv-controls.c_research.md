# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-controls.c

## Purpose
`ivtv-controls.c` implements ivtv-specific V4L2 and cx2341x control callbacks. It bridges generic MPEG encoder/decoder controls to ivtv firmware calls, VBI MPEG insertion state, video decoder format changes, audio sample-clock programming, and volatile decoder timing controls.

## Important APIs, Types, and Functions
The exported operation tables are `ivtv_cxhdl_ops` for `cx2341x_handler` callbacks and `ivtv_hdl_out_ops` for decoder output controls. Key functions are `ivtv_s_stream_vbi_fmt()`, `ivtv_s_video_encoding()`, `ivtv_s_audio_sampling_freq()`, `ivtv_s_audio_mode()`, `ivtv_g_pts_frame()`, `ivtv_g_volatile_ctrl()`, and `ivtv_s_ctrl()`.

## Control Flow
When the cx2341x control handler changes VBI insertion, sliced MPEG buffers are allocated lazily and the sliced service set is defaulted if needed. Video encoding changes program the active video subdev width, halving width for MPEG-1. Audio sampling changes broadcast a matching clock frequency to audio subdevices. Decoder volatile controls read cached timing if valid or ask firmware for current PTS/frame when decoding is active. Decoder audio playback menu changes are translated into `CX2341X_DEC_SET_AUDIO_MODE`.

## State and Persistence
Mutable state is in `struct ivtv`: `vbi.sliced_mpeg_data`, `vbi.insert_mpeg`, `dualwatch_stereo_mode`, `audio_stereo_mode`, `audio_bilingual_mode`, `last_dec_timing`, and `i_flags`. Allocated VBI insertion buffers persist until driver remove frees them.

## Dependencies and Integration Points
The file depends on the cx2341x control framework, V4L2 controls, media bus subdev format calls, ivtv mailbox APIs, and VBI helpers from `ivtv-vbi.h`. Probe installs these ops in `ivtv-driver.c`; file operations consume inserted VBI buffers while reading MPEG.

## Risks and Edge Cases
The sliced VBI buffer size is hardcoded as 2049 bytes, and partial allocation must unwind correctly. Timing controls return zero when idle, so users must distinguish idle from valid zero values. Firmware timing reads can fail with `-EIO`. MPEG-1 width adjustment assumes the video decoder accepts active format updates during control changes.

## Test Signals
Validate VBI MPEG insertion allocation and cleanup, default sliced service selection for 50 Hz and 60 Hz, MPEG-1/MPEG-2 format changes reaching the decoder subdev, audio sampling clock updates, decoder PTS/frame volatile controls while idle and decoding, and decoder audio playback mode firmware calls.
