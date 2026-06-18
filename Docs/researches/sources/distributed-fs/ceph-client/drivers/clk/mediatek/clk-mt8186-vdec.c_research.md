<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-vdec.c

Purpose: This driver registers MT8186 video decoder gates across four VDEC gate banks.

Important APIs, types, and functions: `vdec0_cg_regs` through `vdec3_cg_regs` define register banks; `GATE_VDEC0` through `GATE_VDEC3` populate `vdec_clks`; `vdec_desc` is matched by `mediatek,mt8186-vdecsys`.

Control flow: Simple probe registers all VDEC gate clocks and publishes the OF provider for codec consumers.

State and persistence behavior: Gate enable state is volatile hardware state. Provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8186 bindings, common gate helpers, top-level VDEC parents, video decoder drivers, power domains, and memory/LARB clocks.

Risks and edge cases: Four banks increase the risk of register/shift mismatch. Decode requires coordinated memory and power clocks outside this file.

Test signals: Hardware decode, all VDEC sub-block gate enables in clk summary, runtime PM, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-vdec.c -->
