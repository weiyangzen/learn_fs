# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-img.c

## Purpose
`clk-mt8192-img.c` registers MT8192 image subsystem clocks for two image-system nodes.

## Important APIs, Types, And Functions
The file defines `img_cg_regs`, `img_clks`, `img2_clks`, and descriptors `img_desc` and `img2_desc`. It binds `mediatek,mt8192-imgsys` and `mediatek,mt8192-imgsys2` through the simple MediaTek clock helpers.

## Control Flow, State, And Persistence
Probe registers the matched image gate table and publishes a onecell provider. The driver maintains no extra state beyond CCF registrations.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are image processing and camera pipeline drivers. Risks include choosing the wrong descriptor for the second image node or top image parent drift. Tests include image pipeline probe, clock lookup for both nodes, and suspend/resume.
