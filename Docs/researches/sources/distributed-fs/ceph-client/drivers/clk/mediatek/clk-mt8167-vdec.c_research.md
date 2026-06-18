<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-vdec.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-vdec.c

Purpose: This driver registers MT8167 video decoder subsystem gates.

Important APIs, types, and functions: Two gate banks are described by `vdec0_cg_regs` and `vdec1_cg_regs`. `GATE_VDEC0_I` and `GATE_VDEC1_I` use inverted gate operations for VDEC gate bits. `vdec_desc` is selected by `mediatek,mt8167-vdecsys`.

Control flow: `mtk_clk_simple_probe` maps the VDEC register block, registers the gate clocks, and exposes the OF clock provider. Codec drivers enable the gates while decoding.

State and persistence behavior: Runtime gate enable state is held in VDEC MMIO registers; the driver stores only provider metadata. Removal unregisters the gates and provider.

Dependencies and integration points: It depends on MT8167 binding IDs, MediaTek gate helpers, top-level VDEC parent muxes, media codec drivers, and often power-domain sequencing.

Risks and edge cases: The inverted gate ops are essential; using normal polarity would disable clocks when consumers request enable. Codec hardware may hang if LARB/SMI and VDEC gates are not sequenced coherently.

Test signals: Hardware video decode, clock summary enable counts during decode, suspend/resume of the VDEC power domain, and probe/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-vdec.c -->
