<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mm.c

Purpose: This pdev driver registers MT8183 multimedia gates for display, SMI/LARB, MDP, mutex, DPI, DSI, and related blocks.

Important APIs, types, and functions: `mm0_cg_regs` and `mm1_cg_regs` back `mm_clks`; `mm_desc` is attached to platform ID `clk-mt8183-mm`; lifecycle uses `mtk_clk_pdev_probe/remove`.

Control flow: A parent platform device instantiates the MM clock device, pdev probe registers all gates, and display/media consumers use the registered clock IDs.

State and persistence behavior: Gate state is volatile MM register state. Provider state is runtime-only.

Dependencies and integration points: It depends on MT8183 bindings, pdev clock helpers, common gate ops, top-level MM parents, DRM/display, MDP, SMI/LARB, and power domains.

Risks and edge cases: Multimedia clocks are tightly coupled with power domains and memory ports. Bank/shift mistakes can break unrelated display blocks.

Test signals: Display and MDP operation, LARB clock sequencing, runtime PM, clock summary gate counts, and pdev unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-mm.c -->
