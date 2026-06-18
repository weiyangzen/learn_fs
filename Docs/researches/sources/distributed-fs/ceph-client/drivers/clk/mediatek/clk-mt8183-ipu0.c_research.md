<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu0.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu0.c

Purpose: This file registers MT8183 primary IPU core clock gates.

Important APIs, types, and functions: `ipu_core0_cg_regs` defines the register bank; `GATE_IPU_CORE0` creates `ipu_core0_clks`; `ipu_core0_desc` is selected by `mediatek,mt8183-ipu_core0`; lifecycle uses `mtk_clk_simple_probe/remove`.

Control flow: Probe maps the IPU core0 gate block, registers gates, and exposes them to IPU/NPU consumers.

State and persistence behavior: Gate state is volatile hardware state and provider data is runtime-only.

Dependencies and integration points: It depends on MT8183 clock bindings, common gate helpers, topckgen IPU parent clocks, IPU power domains, and AI/vision drivers.

Risks and edge cases: Core clock gates must be coordinated with IPU connection/bus gates and power domains. Wrong polarity or shift can leave the core inaccessible.

Test signals: IPU core0 probe/workload, runtime PM sequencing with `ipu_conn`, clk summary gate toggles, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu0.c -->
