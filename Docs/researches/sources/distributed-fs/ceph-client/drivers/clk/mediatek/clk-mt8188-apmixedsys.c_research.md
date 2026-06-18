<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-apmixedsys.c

Purpose: This driver registers MT8188 apmixedsys root PLLs and a small PLL 26 MHz gate, providing root clocks for Ethernet, storage, display, multimedia, image, universal, ADSP, audio, and GPU domains.

Important APIs, types, and functions: `apmixed_clks` exposes `pll_ssusb26m_en`. `plls` defines ETHPLL, MSDCPLL, TVDPLL1/2, MMPLL, MAINPLL, IMGPLL, UNIVPLL, ADSPPLL, APLL1-5, and MFGPLL with MT8188 min/max, PCW, reset-bar, and fixed-post-divider data. `clk_mt8188_apmixed_probe` allocates `CLK_APMIXED_NR_CLK`, registers PLLs, registers gates, and adds an OF provider. Remove unregisters provider, gates, and PLLs.

Control flow: On `mediatek,mt8188-apmixedsys` probe, the driver maps apmixedsys registers, registers all PLLs first, adds the gate table, and exposes the clock provider. Error paths roll back gates and PLLs in reverse order.

State and persistence behavior: PLL programming and gate state live in volatile apmixedsys registers. Provider state is runtime-only and cleaned up on remove.

Dependencies and integration points: It depends on MT8188 clock bindings, `clk-pll.h`, `clk-gate.h`, common MediaTek registration helpers, and consumers in topckgen/subsystem drivers for Ethernet, USB, display, image, ADSP, audio, storage, and GPU clocks.

Risks and edge cases: Root PLL register definitions must match hardware exactly; mistakes propagate to many rates. Several PLLs use reset-bar and post-divider fields. Provider publication failure must clean up both gates and PLLs.

Test signals: Boot root clock registration, clk summary PLL rates, USB 26 MHz gate, Ethernet/storage/display/audio/GPU/ADSP workloads, error-path cleanup, and module unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-apmixedsys.c -->
