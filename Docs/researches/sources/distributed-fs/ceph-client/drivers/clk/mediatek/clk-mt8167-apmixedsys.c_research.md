<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-apmixedsys.c

Purpose: This driver registers MT8167 apmixedsys PLLs and one adjustable HDMI reference divider. It supplies root PLL parents used by the MT8167 top clock generator and media/peripheral clock trees.

Important APIs, types, and functions: `PLL`/`PLL_B` define `struct mtk_pll_data` entries for ARM, main, universal, MM, APLL1/APLL2, TVD, and LVDS PLLs, with `mmpll_div_table` for MMPLL post-divider choices. `adj_divs` exposes `hdmi_ref` from `tvdpll`. `clk_mt8167_apmixed_probe` maps MMIO, allocates `MT8167_CLK_APMIXED_NR_CLK`, registers PLLs, registers dividers under `mt8167_apmixed_clk_lock`, and publishes an OF provider.

Control flow: The built-in platform driver binds `mediatek,mt8167-apmixedsys` early enough for dependent clocks. Probe uses devm MMIO/allocation, then explicit rollback for PLL/divider/provider failures.

State and persistence behavior: PLL and divider settings are volatile apmixedsys register state. The clock provider is kernel runtime state. There is no remove callback because this built-in root clock driver is not intended to unload.

Dependencies and integration points: It depends on MT8167 clock bindings, `clk-pll.h`, `clk-mtk.h`, common divider helpers, and downstream topckgen/media drivers that reference `mainpll`, `univpll`, `mmpll`, `apll1`, `apll2`, `tvdpll`, and `hdmi_ref`.

Risks and edge cases: Divider registration shares apmixed registers and requires the lock. Missing remove means failed late cleanup is limited to error paths. Wrong PLL post-divider tables or reset-bar flags can break HDMI/display/audio/storage rates.

Test signals: Confirm built-in probe ordering, PLL and `hdmi_ref` presence in clk summary, HDMI/display/audio rate derivation, error rollback with simulated provider failure, and boot of topckgen consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-apmixedsys.c -->
