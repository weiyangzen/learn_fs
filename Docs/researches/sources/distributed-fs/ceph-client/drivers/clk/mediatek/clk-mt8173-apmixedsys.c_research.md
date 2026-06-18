<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-apmixedsys.c

Purpose: This driver registers MT8173 apmixedsys PLLs with optional FHCTL/pllfh support and a special `ref2usb_tx` clock.

Important APIs, types, and functions: `plls` describes ARMCA15, ARMCA7, main, universal, MM, MSDC, VENC, TVD, MPLL, VCODEC, APLL, LVDS, and MSDCPLL2 PLLs. `pllfhs` maps selected PLLs to frequency-hopping data parsed by `fhctl_parse_dt`. `clk_mt8173_apmixed_probe` registers PLLFH clocks, registers `ref2usb_tx`, populates `CLK_APMIXED_HDMI_REF` as a fixed `tvdpll_594m`, then adds an OF provider. Remove unregisters the provider, ref2usb, and PLLFH clocks.

Control flow: Probe finds the optional `mediatek,mt8173-fhctl` node, maps apmixedsys MMIO, allocates onecell data, parses FHCTL metadata, registers PLLs with FH backing, creates the USB reference clock, fills the HDMI reference slot, and exposes clocks.

State and persistence behavior: PLL/FH/ref2usb state is hardware register state plus volatile provider data. Remove reverses provider and clock registration. There is no disk persistence.

Dependencies and integration points: It depends on `clk-fhctl.h`, `clk-pllfh.h`, `clk-pll.h`, `clk-mtk.h`, MT8173 clock IDs, FHCTL DT, and consumers in topckgen, USB, HDMI/display, CPU, storage, video, and audio.

Risks and edge cases: FHCTL parsing is optional but must align PLL IDs with hardware FH IDs. Ref2USB has custom registration and cleanup. The synthetic HDMI reference slot must match consumers expecting `CLK_APMIXED_HDMI_REF`.

Test signals: Boot with and without FHCTL node, validate PLL rates and frequency hopping registration, USB reference operation, HDMI/display clocks, error-path cleanup, and remove/unbind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-apmixedsys.c -->
