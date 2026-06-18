<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vencsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vencsys.c

Purpose: This driver registers MT8173 video encoder gates for both the main VENC system and the VENC-LT system.

Important APIs, types, and functions: `venc_cg_regs` backs both `venc_clks` and `venclt_clks` through `GATE_VENC`. `venc_desc` and `venc_lt_desc` are selected by `mediatek,mt8173-vencsys` and `mediatek,mt8173-vencltsys`.

Control flow: Simple probe selects the descriptor by compatible string and registers the relevant gate set. Consumers see separate providers for main encoder and lightweight encoder blocks.

State and persistence behavior: Gate enable bits are volatile hardware state. Provider registrations are runtime-only.

Dependencies and integration points: It depends on MT8173 clock IDs, common gate helpers, topckgen VENC parents, encoder drivers, and media power domains.

Risks and edge cases: The same register layout is reused for two compatible strings; wrong descriptor association would expose the wrong clock IDs. Encoder gates must be sequenced with power and memory paths.

Test signals: Main and VENC-LT node binding, hardware encode workloads, clock summary gate toggles, runtime PM, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vencsys.c -->
