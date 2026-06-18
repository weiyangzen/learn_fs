# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vlpckgen.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vlpckgen.c

### Purpose
`clk-mt8196-vlpckgen.c` implements the MT8196 very-low-power clock generator. It provides VLP fixed factors, many VLP muxes, two VLP audio PLLs, and tuner initialization for always-on and low-power subsystems.

### Important APIs, Types, And Functions
Important pieces are `vlp_divs`, `vlp_muxes`, `vlp_plls`, `vlpckgen_regmap_config`, `clk_mt8196_vlp_probe()`, and `clk_mt8196_vlp_remove()`. It uses a local spinlock for mux registration, `mtk_pll_fenc_clr_set_ops` for `vlp_apll1/2`, regmap writes for tuner defaults, and indexed mux parents for audio clocks.

### Control Flow, State, And Persistence
Probe allocates onecell data for divs, muxes, and PLLs; ioremaps registers; creates a regmap; registers factors, muxes, and PLLs in order; adds the OF provider; then writes APLL tuner defaults. Error paths unwind in reverse. Remove deletes the provider and unregisters PLLs, muxes, and factors.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-mux.h`, `clk-pll.h`, regmap MMIO, parents from topckgen/APMIXED, and low-power/audio/camera timer consumers. Risks include tuner default mistakes, parent array string issues, HWV/fence bit mismatches, and probe leaks on early ioremap/regmap failures. Test signals include low-power subsystem boot, audio APLL rates, camera TG clocks, regmap tuner values, mux rate changes, and suspend/resume.
