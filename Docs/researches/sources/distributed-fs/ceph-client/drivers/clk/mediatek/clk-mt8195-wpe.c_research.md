# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-wpe.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-wpe.c

### Purpose
`clk-mt8195-wpe.c` registers MT8195 warp engine clocks for the root WPE system and two WPE-VPP subdomains. It gates WPE VPP links, SMI LARBs, event TX, cache/top/DMA/vector/output/mask blocks, and crop/sync units.

### Important APIs, Types, And Functions
The file defines three no-setclr inverted register banks, `GATE_WPE`, `GATE_WPE_VPP0`, `GATE_WPE_VPP1`, three gate arrays, and three descriptors. OF matching maps `mediatek,mt8195-wpesys`, `_vpp0`, and `_vpp1` to the correct descriptor. Probe/remove use `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

### Control Flow, State, And Persistence
Probe selects the OF descriptor, registers the gate array against the device resource, and exposes a onecell provider. WPE root and VPP subdomain clocks are modeled as separate providers for separate register blocks. State lives in hardware gate bits, including no-setclr inverted gates at offsets 0x0, 0x58, and 0x5c.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `top_wpe_vpp` and `top_img`, image/MDP consumers, and MT8195 clock IDs. Risks are inverted gate interpretation, duplicated VPP0/VPP1 table structure, and SMI LARB clock ordering. Test signals include WPE image-processing jobs, VPP0/VPP1 subdomain probes, SMI access without bus faults, and clock debugfs gate toggles.
