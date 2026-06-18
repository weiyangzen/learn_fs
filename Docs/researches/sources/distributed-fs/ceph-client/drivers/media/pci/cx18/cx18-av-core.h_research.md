# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-core.h

## Purpose
This header defines the internal interface and register map for the integrated cx23418 A/V decoder core. It gives the rest of the driver stable names for decoder input routing, audio routing, VBI slicer timing state, and hundreds of decoder, IR, video, VBI, audio, and firmware-download registers.

## Important APIs, Types, and Functions
Key types are `enum cx18_av_video_input`, `enum cx18_av_audio_input`, and `struct cx18_av_state`. `struct cx18_av_state` embeds a `v4l2_subdev`, a V4L2 control handler, current standard/input/audio mode fields, chip revision, initialization state, and VBI slicer line delay/offset. The file is mostly constants such as `CXADEC_CHIP_CTRL`, `CXADEC_DL_CTL`, `CXADEC_VBI_LINE_CTRL*`, `CXADEC_I2S_IN_CTL`, and `CXADEC_I2S_OUT_CTL`.

## Control Flow
There is no executable control flow in this header. Runtime users include the A/V core implementation, decoder firmware loader, VBI configuration, card input tables, and audio/video routing helpers. The register constants make those users program the same decoder address space coherently.

## State and Persistence
The persistent runtime state is in `cx18_av_state` inside `struct cx18`. It tracks the active video/audio input, detected video standard, radio mode, controls, and line offset needed to translate decoder-reported VBI slicer lines into V4L2 field lines. All hardware register state is volatile and rebuilt during probe, first open, standard changes, or firmware reloads.

## Dependencies and Integration Points
The header depends on V4L2 subdev and control APIs and is included by the main driver header. It integrates decoder state with `cx18-cards.c` board routing, `cx18-av-firmware.c` firmware upload, `cx18-av-vbi.c` sliced/raw VBI setup, and ioctl paths that set standards and formats.

## Risks and Edge Cases
Register constants are hardware contracts; a wrong value can break firmware download, clocking, routing, or VBI capture. The video input enums are bit-coded, so card tables must use valid luma/chroma combinations. VBI line comments encode important timing assumptions for 525-line and 625-line systems; changing delay or offset calculations without hardware validation can shift sliced data to the wrong line.

## Test Signals
Useful signals are successful A/V subdev probe, firmware load and verification, correct audio/video input switching on every supported board, working raw and sliced VBI formats, and stable standard changes between 50 Hz and 60 Hz modes.
