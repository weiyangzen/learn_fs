<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mm.c

Purpose: This pdev driver registers MT8186 multimedia/display gates.

Important APIs, types, and functions: `mm0_cg_regs` and `mm1_cg_regs` back `mm_clks`; `mm_desc` is associated with platform ID `clk-mt8186-mm`; lifecycle uses `mtk_clk_pdev_probe/remove`.

Control flow: A parent device instantiates the pdev, pdev probe registers all MM gate clocks, and media/display consumers use them by binding ID.

State and persistence behavior: Gate bits are volatile MM registers. Provider state is runtime-only.

Dependencies and integration points: It depends on MT8186 clock IDs, pdev clock helpers, common gate ops, top-level display/MM parents, DRM/display, MDP, SMI/LARB, and power domains.

Risks and edge cases: Multimedia clock gating requires power-domain coordination. Wrong bank/shift values can disable display-critical clocks.

Test signals: Display pipeline, MDP/MM consumers, LARB access, runtime PM, clk summary gate counts, and pdev removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mm.c -->
