# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192.c

## Purpose
`clk-mt8192.c` is the aggregate MT8192 main clock driver for topckgen, infracfg, and pericfg nodes. It defines root fixed clocks, top-level fixed factors, muxes, composites, gates, infra/peri gates, reset metadata, and GPU mux-notifier behavior.

## Important APIs, Types, And Functions
Major data includes `mt8192_clk_lock`, `top_fixed_clks`, `top_divs`, many parent arrays, `top_mtk_muxes`, `top_muxes`, infra/peri/top gate tables, `clk_rst_desc`, and three `mtk_clk_desc` objects. `clk_mt8192_reg_mfg_mux_notifier()` locates `CLK_TOP_MFG_PLL_SEL` in the mux table and registers a notifier with bypass index 0 to switch to the 26 MHz crystal during MFG parent changes.

## Control Flow, State, And Persistence
OF match data selects between `mediatek,mt8192-infracfg`, `mediatek,mt8192-pericfg`, and `mediatek,mt8192-topckgen`. `mtk_clk_simple_probe()` uses the selected descriptor to register fixed clocks, factors, muxes, composites, gates, reset controllers, and the optional notifier. Registered clocks persist as OF providers until simple remove unwinds them.

## Dependencies, Integration Points, Risks, And Test Signals
This file is a central MT8192 integration point for bus, storage, display, image, camera, audio, USB, UFS, SPI/I2C, video, ADSP, and GPU clocks. Risks include parent order mismatches, critical infra gate flags, reset-controller map errors, and the MFG notifier failing to protect GPU PLL switching. Test signals include full boot with unused-clock cleanup, peripheral probe matrix, reset-controller consumers, GPU devfreq transitions, `clk_summary` topology checks, and suspend/resume.
