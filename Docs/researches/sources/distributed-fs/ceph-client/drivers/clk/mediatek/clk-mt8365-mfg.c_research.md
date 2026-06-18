# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mfg.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mfg.c

### Purpose
`clk-mt8365-mfg.c` registers MT8365 GPU manufacturing clock gates for the BG3D core and MBIST diagnostic clock.

### Important APIs, Types, And Functions
The file defines two gate register banks, `GATE_MFG0` using set/clear ops, `GATE_MFG1` using no-setclr ops, `mfg_clks`, and `mfg_desc`. OF matching uses `mediatek,mt8365-mfgcfg`, and common simple probe/remove do the registration.

### Control Flow, State, And Persistence
Probe registers the two gate descriptors and adds the provider. BG3D uses the normal 0x0/0x4/0x8 gate block, while MBIST uses a direct 0x280 register without set/clear sideband. State is hardware-only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `mfg_sel` and `mbist_diag_sel`, GPU consumers, and MT8365 clock IDs. Risks include no-setclr semantics for MBIST, GPU availability if `mfg_sel` is absent, and diagnostic clocks being rarely tested. Test signals include GPU probe/render, MBIST clock lookup, clk debugfs toggles, and provider unbind.
