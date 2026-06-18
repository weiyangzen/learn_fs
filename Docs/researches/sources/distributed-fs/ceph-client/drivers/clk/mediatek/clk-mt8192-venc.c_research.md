# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-venc.c

## Purpose
`clk-mt8192-venc.c` registers MT8192 video encoder clocks.

## Important APIs, Types, And Functions
It defines `venc_cg_regs`, `venc_clks`, `venc_desc`, and OF compatible `mediatek,mt8192-vencsys`. Probe/remove are the common simple helper functions.

## Control Flow, State, And Persistence
The helper registers encoder gates and publishes them to OF; remove unregisters them. No additional state is kept.

## Dependencies, Integration Points, Risks, And Test Signals
Integration is with V4L2/media encoder drivers and top VENC parent muxes. Risks include gate bit drift and missing clocks for encoder sub-blocks. Test signals include encode workloads, probe/remove, runtime PM, and suspend/resume.
