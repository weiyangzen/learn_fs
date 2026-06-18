# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-cam.c

## Purpose
`clk-mt8192-cam.c` registers MT8192 camera clocks for the main CAMSYS block and RAW A/B/C sub-blocks.

## Important APIs, Types, And Functions
Definitions include `cam_cg_regs`, gate arrays for main and raw blocks, descriptors `cam_desc`, `cam_rawa_desc`, `cam_rawb_desc`, `cam_rawc_desc`, and OF compatibles `mediatek,mt8192-camsys`, `camsys_rawa`, `camsys_rawb`, and `camsys_rawc`.

## Control Flow, State, And Persistence
`mtk_clk_simple_probe()` selects the descriptor from the OF match data, registers the gates, and publishes an OF provider. No custom state or reset handling is present in this file.

## Dependencies, Integration Points, Risks, And Test Signals
It integrates with camera sensor/ISP nodes and MT8192 top camera parents. Risks are compatible-string underscore differences, raw-domain gate omissions, and parent name mismatches. Test signals include camera probe, raw pipeline capture, runtime PM gate toggling, and suspend/resume.
