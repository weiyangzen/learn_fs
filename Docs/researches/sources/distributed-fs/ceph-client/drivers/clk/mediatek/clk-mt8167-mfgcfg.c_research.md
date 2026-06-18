<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mfgcfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mfgcfg.c

Purpose: This driver exposes MT8167 GPU manufacturing-domain clock gates, primarily the GPU/MFG bus and core gate controls.

Important APIs, types, and functions: `mfg_cg_regs` defines the MFG gate register offsets; `GATE_MFG` creates gates in `mfg_clks`; `mfg_desc` is matched by `mediatek,mt8167-mfgcfg`; `mtk_clk_simple_probe/remove` handle provider lifecycle.

Control flow: On probe, the common helper registers the MFG gate table against the compatible node. GPU drivers then enable the gates through CCF before accessing the hardware.

State and persistence behavior: Only MMIO gate bits and runtime provider structures are maintained. No state survives reset or driver removal.

Dependencies and integration points: It depends on MT8167 clock IDs, common MediaTek gate helpers, and top-level MFG parent clocks selected in `clk-mt8167.c`. It integrates with the GPU and power-domain sequencing.

Risks and edge cases: GPU clocks often interact with power domains; enabling a gate while the domain is off or using the wrong parent can cause bus faults. Gate polarity must match hardware.

Test signals: GPU probe and workload execution, runtime PM suspend/resume, clock summary gate enable counts, and bind/unbind checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mfgcfg.c -->
