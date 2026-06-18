<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-xfipll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-xfipll.c

Purpose: This is the MT7988 XFI PLL clock provider for USXGMII. It creates a fixed-factor PLL clock from `top_xtal`, exposes an enable gate, and applies a documented analog software workaround before registering the clocks.

Important APIs, types, and functions: `xfipll_divs` defines `xfipll_pll` as a 125/32 factor of `top_xtal`; `xfipll_clks` defines `xfipll_pll_en` using `mtk_clk_gate_ops_no_setclr_inv`; `xfipll_desc` groups both. `clk_mt7988_xfipll_probe` maps the register block with `of_iomap`, writes `RG_XFI_PLL_ANA_SWWA` to `XFI_PLL_ANA_GLB8`, unmaps it, and delegates to `mtk_clk_simple_probe`.

Control flow: The custom probe performs the analog register write first. If mapping fails it returns `-ENOMEM`; otherwise the simple MediaTek probe registers the fixed factor and gate and publishes the OF provider for `mediatek,mt7988-xfi-pll`.

State and persistence behavior: Runtime state is limited to the registered clocks and the MMIO gate bit. The workaround write changes hardware register state for the lifetime of the device until reset or later firmware/kernel writes. Removal uses `mtk_clk_simple_remove`.

Dependencies and integration points: It depends on the MT7988 clock binding, common MediaTek gate/factor helpers, OF address mapping, and consumers in the USXGMII/XFI Ethernet path.

Risks and edge cases: The workaround uses raw `of_iomap`/`iounmap`, so failure handling is deliberately minimal. The gate uses inverted no-set/clear semantics, so a wrong gate operation would invert enable state. The fixed factor assumes the expected crystal parent.

Test signals: Validate that `xfipll_pll` and `xfipll_pll_en` appear in clock summary, the analog register contains `0x02283248` after probe, USXGMII links train reliably, and probe fails cleanly if the MMIO resource is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-xfipll.c -->
