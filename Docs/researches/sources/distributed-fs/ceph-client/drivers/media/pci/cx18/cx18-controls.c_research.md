# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-controls.c

## Purpose
This file implements cx18 callbacks for the shared `cx2341x_handler` MPEG encoder control framework. It translates control changes into decoder, audio, and VBI-side state changes.

## Important APIs, Types, and Functions
The exported object is `cx18_cxhdl_ops`. Callback functions are `cx18_s_stream_vbi_fmt()`, `cx18_s_video_encoding()`, `cx18_s_audio_sampling_freq()`, and `cx18_s_audio_mode()`. They operate on `struct cx2341x_handler` embedded in `struct cx18`.

## Control Flow
When a V4L2 MPEG control changes, the cx2341x core calls these hooks. VBI format changes are rejected while analog capture is active, allocate the sliced-MPEG insertion ring on demand, enable or disable IVTV-style VBI insertion only for supported MPEG-2 PS stream types, and install default service lines when none are configured. Video encoding changes update the decoder pad format width for MPEG-1 half-width mode. Audio sample frequency changes call all audio subdevices to adjust clock frequency. Audio mode changes cache dualwatch stereo mode.

## State and Persistence
State changes are in `cx->vbi.insert_mpeg`, `cx->vbi.sliced_mpeg_data[]`, `cx->dualwatch_stereo_mode`, decoder subdev format state, and audio subdev clock state. Allocated VBI buffers live until device removal.

## Dependencies and Integration Points
This file depends on `cx2341x_handler`, V4L2 subdev pad and audio operations, cx18 VBI helpers, mailbox-backed control application, and global capture counters. It is installed during `cx18_init_struct1()`.

## Risks and Edge Cases
VBI insertion is intentionally limited to MPEG-2 PS/DVD/SVCD streams; enabling it for TS would corrupt assumptions in file copy splice logic. Buffer allocation is all-or-nothing across 32 frames. The code relies on capture counters to prevent mid-stream changes.

## Test Signals
Change MPEG stream type and VBI insertion controls before and during capture, verify `-EBUSY` while capturing, confirm default sliced service lines are created, and check audio clock changes at 32/44.1/48 kHz.
