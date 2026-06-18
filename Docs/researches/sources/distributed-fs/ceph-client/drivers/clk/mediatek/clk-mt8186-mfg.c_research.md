<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mfg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mfg.c

Purpose: This file exposes MT8186 GPU/MFG subsystem gate clocks.

Important APIs, types, and functions: `mfg_cg_regs` defines the MFG gate bank; `GATE_MFG` creates `mfg_clks`; `mfg_desc` is matched by `mediatek,mt8186-mfgsys`.

Control flow: Simple probe registers MFG gates and publishes them to GPU consumers.

State and persistence behavior: Gate state is volatile register state; provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8186 bindings, common gate helpers, topckgen MFG muxes, GPU drivers, power domains, and the topckgen MFG mux notifier.

Risks and edge cases: GPU clocking depends on parent switching and power sequencing. Gate mistakes can hang GPU accesses.

Test signals: GPU probe/render workloads, runtime PM, MFG mux parent changes, clk summary gates, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mfg.c -->
