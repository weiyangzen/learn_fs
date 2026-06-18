# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-ipe.c

## Purpose
`clk-mt8188-ipe.c` registers MT8188 Image Processing Engine clocks for FD, FE, RSC, DPE, and IPE top paths.

## Important APIs, Types, And Functions
The file defines `ipe_cg_regs`, `ipe_clks`, `ipe_sys_rst_desc`, and `ipe_desc`. It matches `mediatek,mt8188-ipesys` and delegates probe/remove to the generic MediaTek simple clock helpers.

## Control Flow, State, And Persistence
Probe maps the IPE register region, registers each gate clock, publishes the OF provider, and registers reset lines from the descriptor. Runtime state is limited to the clock provider, gate bits, and reset metadata.

## Dependencies, Integration Points, Risks, And Test Signals
Integration points are IPE imaging drivers and reset-controller consumers. Risks include incorrect `top_ipe` parentage, reset ID drift, and gate coverage omissions that only appear under specific camera/vision workloads. Test signals include IPE device probe, reset assertions, clock enable counts during image processing, and suspend/resume.
