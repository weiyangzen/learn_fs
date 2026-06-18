<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-topckgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-topckgen.c

Purpose: This is the MT8186 top clock generator driver. It registers fixed clocks, PLL-derived factors, many top-level muxes, audio I2S/APLL composites, and an MFG mux notifier.

Important APIs, types, and functions: `top_fixed_clks`, `top_divs`, `top_mtk_muxes`, and `top_muxes` are grouped into `topck_desc` with `mt8186_clk_lock`. Parent arrays cover AXI, SCP, MFG, camera timers, UART/SPI/MSDC/audio/display/USB/security/VENC/ISP/VDEC/MDP/UFS/ADSP/NNA/WPE/DPI/SPMI/SPINOR domains. `clk_mt8186_reg_mfg_mux_notifier` registers a `struct mtk_mux_nb` for safe MFG parent switching.

Control flow: Simple probe selects `topck_desc` for `mediatek,mt8186-topckgen`, registers factors/muxes/composites, installs the MFG notifier, and publishes the OF provider. Consumers select parents and rates through CCF.

State and persistence behavior: Mux, divider, and composite state is volatile topckgen register state. The spinlock serializes shared updates; notifier state is devm-managed.

Dependencies and integration points: It depends on MT8186 apmixedsys PLLs, MediaTek mux/composite helpers, clock bindings, and nearly every subsystem clock consumer including CPU/GPU, camera, display, MDP, video, audio, UFS, USB, ADSP, NNA, and WPE.

Risks and edge cases: Parent-order mistakes or mux field errors have broad impact. MFG notifier behavior is critical for GPU rate changes. Many muxes use update bits and shared registers, so locking and register layout are important.

Test signals: Full boot clock summary, GPU DVFS, audio/display/camera/video/MDP/UFS/USB/ADSP/NNA/WPE workloads, mux parent changes, suspend/resume, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-topckgen.c -->
