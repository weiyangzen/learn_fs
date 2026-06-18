<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mfgcfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mfgcfg.c

Purpose: This driver exposes MT8183 GPU/MFG clock gates.

Important APIs, types, and functions: `mfg_cg_regs` describes the MFG register bank; `GATE_MFG` creates `mfg_clks`; `mfg_desc` is matched by `mediatek,mt8183-mfgcfg`.

Control flow: Simple probe registers MFG gates and publishes an OF provider. GPU consumers enable the gates through CCF.

State and persistence behavior: Gate enable state is volatile hardware state; provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8183 clock bindings, topckgen MFG muxes, MediaTek gate helpers, GPU drivers, and power-domain sequencing.

Risks and edge cases: The MFG mux has a notifier in `clk-mt8183.c`; this gate provider must interoperate with that parent-switching behavior. Power-domain ordering matters.

Test signals: GPU probe and rendering workload, MFG mux switching under load, runtime PM, clk summary gates, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mfgcfg.c -->
