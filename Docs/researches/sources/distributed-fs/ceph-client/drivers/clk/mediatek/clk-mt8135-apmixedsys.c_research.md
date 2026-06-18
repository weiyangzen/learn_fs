<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135-apmixedsys.c

Purpose: This driver registers MT8135 apmixedsys PLLs, including ARM, main, universal, multimedia, storage, TV/display, LVDS, audio, and video decoder PLLs.

Important APIs, types, and functions: The `PLL` macro fills `struct mtk_pll_data` entries with register offsets, power registers, enable masks, PCW fields, post-divider fields, tuner registers, `HAVE_RST_BAR`, and the MT8135 reset-bar mask. `clk_mt8135_apmixed_probe` allocates `CLK_APMIXED_NR_CLK` onecell data, calls `mtk_clk_register_plls`, then `of_clk_add_hw_provider`. `clk_mt8135_apmixed_remove` unregisters the provider and PLLs.

Control flow: On `mediatek,mt8135-apmixedsys` probe, the driver obtains the node, allocates clock storage, registers every PLL table entry against the apmixedsys MMIO region through common helpers, and exposes the resulting hardware clocks to DT consumers. Error paths unregister already-created PLLs.

State and persistence behavior: PLL programming and enable state live in apmixedsys registers. The driver keeps only provider metadata and clock handles in memory. There is no persistent storage; remove deletes the provider and unregisters PLLs.

Dependencies and integration points: It depends on `clk-pll.h`, `clk-mtk.h`, MT8135 clock binding IDs, and parent consumers in topckgen and subsystem gates. The PLL names form the parent namespace used by `clk-mt8135.c`.

Risks and edge cases: Incorrect register offsets or PCW bit widths can produce wrong frequencies or failed PLL lock. Some PLLs use reset-bar behavior and some do not, so flag accuracy matters. The old manual allocation path requires remove/error cleanup symmetry.

Test signals: Boot-time PLL registration, clk summary parent rates, topckgen parent selection for `mainpll`, `univpll`, `mmpll`, `msdcpll`, `audpll`, and display PLLs, probe error injection for provider registration, and module remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8135-apmixedsys.c -->
