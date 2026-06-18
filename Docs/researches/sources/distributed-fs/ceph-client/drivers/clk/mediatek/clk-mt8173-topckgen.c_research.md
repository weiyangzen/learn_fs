<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-topckgen.c

Purpose: This is the MT8173 top clock generator driver. It declares fixed clocks, fixed PLL dividers, and a large composite mux table for system, memory, media, storage, USB, audio, display, HDMI, and peripheral source clocks.

Important APIs, types, and functions: `TOP_MUX_GATE`/`TOP_MUX_GATE_NOSR` define gated mux composites; `fixed_clks`, `top_divs`, and `top_muxes` are grouped in `topck_desc` with `mt8173_top_clk_lock`. The driver binds `mediatek,mt8173-topckgen` through `mtk_clk_simple_probe/remove`.

Control flow: Probe registers fixed clocks/factors/composites from the descriptor, protects shared register updates with the top clock lock, and publishes the OF provider. Downstream subsystem clock drivers and device drivers select parents by binding ID.

State and persistence behavior: Clock parent/gate state is volatile topckgen register state. Provider data lives until driver removal. No state is written outside hardware registers.

Dependencies and integration points: It depends on MT8173 apmixedsys PLL names, common MediaTek mux/composite helpers, and MT8173 clock bindings. It feeds AXI/memory, MM/VDEC/VENC/MFG, camera, UART/SPI/MSDC, USB, audio, SCP, HDMI/HDCP, and RTC-related consumers.

Risks and edge cases: Parent arrays are long and hardware-encoded; wrong order causes subtle rate failures. Gate/no-set-rate flag usage matters for glitch-sensitive muxes. HDMI/display clocks are particularly sensitive to fixed dummy rates and parent naming.

Test signals: Full boot clock summary, display/HDMI/audio/storage/USB/video/GPU operation, mux parent switching where supported, suspend/resume, and module unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-topckgen.c -->
