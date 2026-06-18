# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mm.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365-mm.c

### Purpose
`clk-mt8365-mm.c` provides MT8365 multimedia gates for MDP, display, DSI/DPI/LVDS, SMI, image relay/async, and 26 MHz HRTWT clocks.

### Important APIs, Types, And Functions
Two gate banks are defined by `mm0_cg_regs` and `mm1_cg_regs`; `GATE_MM0` and `GATE_MM1` fill `mm_clks`. The descriptor `mm_desc` is selected by a platform device ID table and registered via `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The platform helper registers all multimedia gates and publishes the provider. Gate state is in MM0/MM1 hardware set/clear/status registers. The driver contains no custom runtime PM or persistent software state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `mm_sel`, `dpi0_sel`, `dsi0_lntc_dsick`, `vpll_dpix`, and `lvdstx_dig_cts`, plus DRM/MDP/camera consumers. Risks include display output parent naming, SMI/LARB gating errors, and platform-device creation from the SoC clock controller. Test signals include display modeset, MDP operations, DSI/DPI/LVDS outputs, SMI access, and clk debugfs.
