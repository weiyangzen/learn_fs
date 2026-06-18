<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-venc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-venc.c

Purpose: This driver registers MT8183 video encoder gates.

Important APIs, types, and functions: `venc_cg_regs` defines the gate bank; `GATE_VENC_I` creates inverted gate entries in `venc_clks`; `venc_desc` is matched by `mediatek,mt8183-vencsys`.

Control flow: Simple probe registers the VENC gate provider; encoder drivers enable gates while encoding.

State and persistence behavior: State is MMIO gate bits plus runtime provider metadata. Remove unregisters provider state.

Dependencies and integration points: It depends on MT8183 clock IDs, inverted gate helpers, top-level VENC parents, encoder drivers, and power domains.

Risks and edge cases: Gate polarity is inverted. Encoder clocks must be sequenced with media power and memory path clocks.

Test signals: Hardware encode, runtime PM enable/disable, clk summary gate state, suspend/resume, and unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-venc.c -->
