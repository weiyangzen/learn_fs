# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-ioctl.c

## Purpose
This file implements the V4L2 ioctl surface for the ivtv Conexant CX2341x MPEG encoder/decoder driver. It translates userspace controls for video/audio routing, TV standards, tuner frequency, capture/output formats, encoder and decoder commands, OSD overlay/framebuffer attributes, sliced/raw VBI, passthrough, and private YUV DMA into ivtv internal state and firmware mailbox calls.

## Important APIs, Types, and Functions
Externally visible helpers include `ivtv_service2vbi`, `ivtv_expand_service_set`, `ivtv_get_service_set`, `ivtv_set_osd_alpha`, `ivtv_set_speed`, `ivtv_set_funcs`, `ivtv_s_std_enc`, `ivtv_s_std_dec`, `ivtv_do_s_frequency`, and `ivtv_do_s_input`. The file defines the `v4l2_ioctl_ops` table and many per-ioctl handlers for format get/try/set, standard/frequency/input/output, encoder/decoder command, framebuffer, selection, event subscription, and default private ioctls.

## Control Flow
Most calls enter through `video_ioctl2` and dispatch through `ivtv_ioctl_ops`. Format handlers normalize V4L2 structures, clamp geometry to hardware limits, and reject changes while capture or decode is active. Decoder commands route through `ivtv_video_command`, which validates speed, output mode, pause/resume state, and calls stream start/stop helpers. Encoder commands call capture start/stop or pause/resume firmware APIs. Standard changes split into encoder and decoder paths: encoder state updates capture dimensions/VBI layout and calls video subdevices, while decoder standard changes wait for a safe vsync window before programming firmware and display rectangles.

## State and Persistence Behavior
The file mutates persistent per-card state in `struct ivtv`: active input/output, audio input, tuner standard, `std`/`std_out`, 50/60 Hz booleans, capture dimensions, VBI formats, `main_rect`, YUV playback settings, OSD alpha/chroma key flags, output mode, playback speed, program index read cursor, and stream/device capabilities. It also sets or clears internal flags for paused decode/encode and updates firmware state through cached mailbox commands.

## Dependencies and Integration Points
It depends on V4L2 ioctl, event, control, and subdev APIs; ivtv stream lifecycle, fileops, queue, VBI, routing, YUV, GPIO, controls, cards, and mailbox layers; cx2341x MPEG control helpers; tuner/video/audio subdevices; SAA7127 OSD/video output routing; and private ivtv UAPI commands such as `IVTV_IOC_DMA_FRAME` and `IVTV_IOC_PASSTHROUGH_MODE`.

## Risks
The high-risk areas are lock ordering around `serialize_lock` when waiting on DMA or vsync, rejecting mutable settings while streams are active, speed conversion edge cases, private ioctl output-mode ownership, and VBI service-line normalization across PAL/NTSC. Firmware calls can fail or hang if issued outside expected decoder timing. OSD framebuffer state must remain coherent with `ivtvfb` and YUV tracking state.

## Test Signals
Useful signals include V4L2 compliance for all node types, format clamp tests for MPEG/YUV/raw VBI/sliced VBI, input/frequency/standard switching while idle and busy, decoder speed/pause/resume/stop tests, EOS and vsync event delivery, private YUV DMA frame tests, OSD overlay flag/alpha/chroma-key checks, and log-status output under active streams.
