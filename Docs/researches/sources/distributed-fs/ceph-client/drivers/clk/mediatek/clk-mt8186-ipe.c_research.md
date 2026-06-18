<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-ipe.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-ipe.c

Purpose: This driver registers MT8186 image processing engine gates.

Important APIs, types, and functions: `ipe_cg_regs` describes the IPE gate bank; `GATE_IPE` creates `ipe_clks`; `ipe_desc` is selected by `mediatek,mt8186-ipesys`.

Control flow: Simple probe registers the IPE gate provider for image-processing consumers.

State and persistence behavior: Gate state is volatile MMIO state; provider data is runtime-only.

Dependencies and integration points: It depends on MT8186 clock IDs, common gate helpers, top-level IPE/ISP parents, image processing drivers, power domains, and memory/LARB clocks.

Risks and edge cases: IPE operation depends on companion image and memory clocks; isolated gate enable is not enough. Bit-offset errors can cause image workload timeouts.

Test signals: IPE workload execution, runtime PM gate toggles, clk summary inspection, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-ipe.c -->
