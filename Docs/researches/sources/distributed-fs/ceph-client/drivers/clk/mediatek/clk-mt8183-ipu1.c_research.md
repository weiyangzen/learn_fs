<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu1.c

Purpose: This file registers MT8183 secondary IPU core clock gates.

Important APIs, types, and functions: `ipu_core1_cg_regs`, `GATE_IPU_CORE1`, `ipu_core1_clks`, and `ipu_core1_desc` describe the provider matched by `mediatek,mt8183-ipu_core1`.

Control flow: The common simple probe registers the core1 gate table and publishes an OF clock provider. IPU drivers enable the gates when scheduling work on the second core.

State and persistence behavior: Gate state is MMIO-backed and volatile. Provider metadata is removed on unbind.

Dependencies and integration points: It depends on MT8183 bindings, MediaTek gate helpers, IPU bus/connection clocks, power domains, and AI/vision consumers.

Risks and edge cases: Core1 depends on shared bus and connection gates; standalone enable may be insufficient. Register shift mistakes can affect the wrong IPU clock.

Test signals: IPU core1 workload, multi-core IPU use with `ipu0` and `ipu_conn`, runtime PM, clock summary transitions, and unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu1.c -->
