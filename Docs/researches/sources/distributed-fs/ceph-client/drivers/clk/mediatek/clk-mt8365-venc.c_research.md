# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-venc.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-venc.c

### Purpose
`clk-mt8365-venc.c` registers MT8365 video encoder gates for the VENC core and JPEG encoder.

### Important APIs, Types, And Functions
The file defines `venc_cg_regs`, `GATE_VENC`, `venc_clks`, and `venc_desc`. Gates use `mtk_clk_gate_ops_setclr_inv`. OF matching uses `mediatek,mt8365-vencsys`, and registration is via `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
Probe registers the two inverted gates and publishes them as an OF provider. Clock state persists only in the VENC CG register block; the driver has no custom state or runtime PM logic.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `mm_sel`, VENC/JPEG consumers, and MT8365 clock bindings. Risks include inverted gate modeling, missing auxiliary encoder bus clocks, and JPEG-only paths not being exercised. Test signals include video encode, JPEG encode, clk summary state, runtime open/close cycles, and module unload.
