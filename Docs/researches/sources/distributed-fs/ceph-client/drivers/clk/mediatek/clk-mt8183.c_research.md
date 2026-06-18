<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183.c

Purpose: This is the main MT8183 topckgen, infracfg, pericfg, and mcucfg clock driver. It defines fixed clocks, PLL factors, top muxes, audio composites, infrastructure/peripheral gates, MCU muxes, reset controller data, and an MFG mux notifier.

Important APIs, types, and functions: `top_fixed_clks`, `top_divs`, `top_muxes`, `top_aud_comp`, `top_clks`, `infra_clks`, `peri_clks`, and `mcu_muxes` are grouped into `topck_desc`, `infra_desc`, `peri_desc`, and `mcu_desc`. `clk_rst_desc` exposes infracfg resets. `clk_mt8183_reg_mfg_mux_notifier` registers `struct mtk_mux_nb` for MFG parent switching. Compatible strings cover `mediatek,mt8183-infracfg`, `mediatek,mt8183-mcucfg`, `mediatek,mt8183-pericfg`, and `mediatek,mt8183-topckgen`.

Control flow: `mtk_clk_simple_probe` selects the descriptor, registers its factors/muxes/composites/gates/resets, and invokes the descriptor notifier hook for topckgen. The notifier temporarily switches the MFG mux to a safe parent around parent-rate changes.

State and persistence behavior: Clock selections, gates, and reset state are volatile hardware registers. Provider data is runtime-only. `mt8183_clk_lock` protects shared mux/composite registers.

Dependencies and integration points: It depends on MT8183 apmixedsys PLLs, common MediaTek clock/mux/gate/reset helpers, DT bindings, and consumers across CPU, infra, peri, display, camera, IPU, GPU, audio, storage, USB, UFS, SCP, security, and SPM domains.

Risks and edge cases: This is a central table file; parent-order and bit-field mistakes affect many devices. The MFG notifier is critical for safe GPU mux/rate changes. Critical or bus clocks should not be inadvertently gated.

Test signals: Full SoC boot, clk summary validation, GPU DVFS/mux changes, reset-controller users, storage/audio/display/camera/IPU/USB/UFS workloads, suspend/resume, and module removal where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183.c -->
