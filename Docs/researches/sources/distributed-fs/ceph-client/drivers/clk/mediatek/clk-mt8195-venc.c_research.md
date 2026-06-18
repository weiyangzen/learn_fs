# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-venc.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-venc.c

### Purpose
`clk-mt8195-venc.c` registers MT8195 video encoder clocks for the main VENC system and the second VENC core. It covers LARB, VENC, JPEG encode/decode, secondary JPEG decode, and GALS clocks.

### Important APIs, Types, And Functions
The file defines one inverted set/clear gate bank, `GATE_VENC`, two gate arrays (`venc_clks` and `venc_core1_clks`), and two descriptors selected by OF compatible strings. The platform driver uses `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()` instead of a platform ID table.

### Control Flow, State, And Persistence
At probe, the common simple helper selects the descriptor from `of_match_clk_mt8195_venc`, registers the selected gate set, and publishes the OF clock provider. Hardware state is held in the VENC gate register at offsets 0x0/0x4/0x8; the two compatibilities instantiate independent providers for separate register blocks.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `top_venc`, OF nodes `mediatek,mt8195-vencsys` and `mediatek,mt8195-vencsys_core1`, and V4L2/media encoder consumers. Risks are inverted gate semantics, core0/core1 binding mismatches, and missing LARB/GALS clocks causing DMA failures. Test signals are encoder/JPEG runtime PM paths, clk summary for both providers, media pipeline encode/decode tests, and clean unregistration on driver unload.
