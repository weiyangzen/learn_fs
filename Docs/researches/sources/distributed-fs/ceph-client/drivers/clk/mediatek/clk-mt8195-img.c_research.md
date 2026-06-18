# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-img.c

## Purpose
`clk-mt8195-img.c` registers MT8195 image subsystem clocks for main image, DIP top, DIP NR, and WPE image blocks.

## Important APIs, Types, And Functions
The driver defines `img_cg_regs`, gate arrays for `img`, `img1_dip_top`, `img1_dip_nr`, and `img1_wpe`, plus descriptors for each. OF matches include `mediatek,mt8195-imgsys`, `imgsys1_dip_top`, `imgsys1_dip_nr`, and `imgsys1_wpe`.

## Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers gates for the matched image-domain node and publishes the clock provider. State is the CCF provider and hardware gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are image, DIP, and WPE drivers. Risks include compatible-string mismatch and gate omissions in image subdomains. Test signals include image processing workloads, WPE/DIP probe, runtime PM, and suspend/resume.
