<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-wpe.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-wpe.c

Purpose: This provider registers MT8186 Warp Engine clock gates.

Important APIs, types, and functions: `wpe_cg_regs` defines the gate bank; `GATE_WPE` creates `wpe_clks`; `wpe_desc` is selected by `mediatek,mt8186-wpesys`.

Control flow: Simple probe registers WPE gates and publishes them to warp/image-processing consumers.

State and persistence behavior: Gate state is volatile hardware state; provider data is runtime-only.

Dependencies and integration points: It depends on MT8186 clock IDs, common gate helpers, top-level WPE parents, image/warp engine drivers, power domains, and memory clocks.

Risks and edge cases: WPE clocking depends on MDP/image and memory paths. A wrong parent or gate bit can produce pipeline stalls.

Test signals: WPE workload execution, runtime PM enable/disable, clk summary gate counts, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-wpe.c -->
