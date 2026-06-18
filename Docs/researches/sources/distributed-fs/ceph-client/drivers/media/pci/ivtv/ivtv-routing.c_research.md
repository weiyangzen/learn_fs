# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-routing.c

## Purpose
This file centralizes audio and video input/output routing for ivtv cards. It programs board-specific subdevices and GPIO/mux chips based on the current active input, audio input, radio mode, and card wiring tables.

## Important APIs, Types, and Functions
The exported functions are `ivtv_audio_set_io` and `ivtv_video_set_io`. They consume card description structures for audio inputs, radio input, video inputs, muxer hardware, video processors, GPIO, and optional UPD64031A/UPD6408X chips.

## Control Flow
Audio routing chooses the radio input when radio mode is active, otherwise the current audio input, then routes through an optional M52790 muxer and the card's audio decoder. Video routing sends the active video input to the main video subdevice, classifies tuner/S-Video/composite, programs GPIO routing when present, and configures optional UPD64031A/UPD6408X processing paths for tuner, composite, and S-Video variants.

## State and Persistence Behavior
The file does not own long-lived software state, but it applies persistent hardware routing state in subdevices and GPIO chips. It reads `itv->active_input`, `itv->audio_input`, radio flags, and card configuration to decide the routing.

## Dependencies and Integration Points
It depends on V4L2 subdev routing calls, ivtv card tables, GPIO support, MSP3400, M52790, UPD64031A, UPD64083, tuner/video/audio hardware masks, and ioctl input/audio selection paths.

## Risks
Board tables must match physical wiring. Wrong input classification can select the wrong ADC, disable needed 3D Y/C separation, or route audio incorrectly. Radio mode overrides normal audio input and must be cleared by caller lifecycle code.

## Test Signals
Switch all card inputs, verify tuner/composite/S-Video capture, radio audio routing, GPIO routing on affected boards, UPD filter behavior, and input changes while capture is blocked by ioctl busy checks.
