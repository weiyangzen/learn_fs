<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-mm.c

Purpose: This provider registers MT8173 multimedia gates for display, SMI/LARB, MDP, DPI/DSI, mutex, and related MM blocks.

Important APIs, types, and functions: Two register banks `mm0_cg_regs` and `mm1_cg_regs` back `mt8173_mm_clks`. `mm_desc` is supplied by platform ID `clk-mt8173-mm`, and lifecycle is handled by `mtk_clk_pdev_probe/remove`.

Control flow: A parent device creates the platform device; pdev probe registers all MM gates from `mm_desc`. Display/media drivers consume the clocks through normal CCF lookup.

State and persistence behavior: Gate bits are volatile MM register state. Provider and gate handles are runtime-only and removed on pdev remove.

Dependencies and integration points: It depends on MT8173 clock IDs, common gate helpers, pdev clock helpers, topckgen MM parents, DRM/display, MDP, and memory/LARB consumers.

Risks and edge cases: Display clock gating must coordinate with power domains and memory ports. Wrong bank/shift values can disable unrelated multimedia blocks.

Test signals: Display bring-up, MDP operation, DSI/DPI paths, LARB/SMI enable ordering, clock summary during runtime PM, and pdev unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-mm.c -->
