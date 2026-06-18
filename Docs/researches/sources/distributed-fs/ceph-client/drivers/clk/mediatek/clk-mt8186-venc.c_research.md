<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-venc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-venc.c

Purpose: This file registers MT8186 video encoder gate clocks.

Important APIs, types, and functions: `venc_cg_regs` defines the gate bank; `GATE_VENC` creates `venc_clks`; `venc_desc` is matched by `mediatek,mt8186-vencsys`.

Control flow: Simple probe registers the VENC gates and publishes a clock provider for encoder consumers.

State and persistence behavior: Gate state is volatile MMIO state; provider state is runtime-only.

Dependencies and integration points: It depends on MT8186 clock bindings, common gate helpers, top-level VENC parents, encoder drivers, and power domains.

Risks and edge cases: Encoder operation also depends on MM/MDP and memory clocks. Gate bit mistakes can manifest as encode timeouts.

Test signals: Hardware encode, runtime PM gate transitions, clk summary inspection, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-venc.c -->
