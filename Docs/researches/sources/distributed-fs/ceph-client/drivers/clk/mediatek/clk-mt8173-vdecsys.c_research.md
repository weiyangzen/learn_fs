<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vdecsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vdecsys.c

Purpose: This file registers MT8173 video decoder subsystem gates.

Important APIs, types, and functions: `vdec0_cg_regs` and `vdec1_cg_regs` define the VDEC gate banks; `GATE_VDEC` creates `vdec_clks`; `vdec_desc` is matched by `mediatek,mt8173-vdecsys`; the driver uses `mtk_clk_simple_probe/remove`.

Control flow: The platform driver maps the VDEC clock registers, registers VDEC gates, and provides them through OF. Codec drivers enable the gates around decode work.

State and persistence behavior: Gate state is hardware register state only. Provider metadata is runtime-only and removed on unbind.

Dependencies and integration points: It depends on MT8173 clock bindings, common gate helpers, topckgen VDEC parent clocks, media codec drivers, and power domains.

Risks and edge cases: Wrong bank selection or polarity can stop decoder clocks. VDEC operation also depends on power and memory clocks outside this file.

Test signals: Hardware decode, runtime PM enable/disable sequences, clk summary gate counts, suspend/resume, and bind/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-vdecsys.c -->
