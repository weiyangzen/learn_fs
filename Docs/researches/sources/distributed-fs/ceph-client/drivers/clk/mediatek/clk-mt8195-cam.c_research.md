# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-cam.c

## Purpose
`clk-mt8195-cam.c` registers MT8195 camera clocks for main, MRAW, RAW A/B, and YUV A/B camera domains.

## Important APIs, Types, And Functions
The file defines `cam_cg_regs`, six gate arrays, six descriptors, and OF matches for `mediatek,mt8195-camsys`, `camsys_mraw`, `camsys_rawa`, `camsys_rawb`, `camsys_yuva`, and `camsys_yuvb`. It uses the common simple probe/remove helpers.

## Control Flow, State, And Persistence
The selected descriptor drives gate registration and OF provider creation. There is no reset-controller descriptor in this file; state is limited to the registered clocks and gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Integration is with MT8195 camera/ISP drivers and top camera parent muxes. Risks include compatible underscore naming, split raw/yuv domain mistakes, and missing MRAW gates. Test signals include camera capture over raw/yuv paths, MRAW use, runtime PM, and suspend/resume.
