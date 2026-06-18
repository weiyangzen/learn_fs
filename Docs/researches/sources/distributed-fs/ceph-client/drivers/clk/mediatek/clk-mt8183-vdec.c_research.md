<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-vdec.c

Purpose: This file registers MT8183 video decoder gates.

Important APIs, types, and functions: `vdec0_cg_regs` and `vdec1_cg_regs` define two inverted gate banks; `vdec_clks` is grouped into `vdec_desc`; the provider matches `mediatek,mt8183-vdecsys`.

Control flow: Simple probe registers VDEC gates and publishes them to media codec consumers.

State and persistence behavior: Gate bits are volatile hardware state. Provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8183 clock bindings, inverted MediaTek gate ops, VDEC parent clocks from topckgen, codec drivers, power domains, and memory/LARB clocks.

Risks and edge cases: Inverted gates must not be converted to normal gates. Decode failures can result from missing companion power or memory clocks rather than this provider alone.

Test signals: Hardware decode, runtime PM, clock summary enable counts, suspend/resume, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-vdec.c -->
