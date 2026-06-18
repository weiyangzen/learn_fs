<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_adl.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_adl.c

Purpose: This driver exposes the MT8183 IPU ADL clock gate.

Important APIs, types, and functions: `ipu_adl_cg_regs` defines the ADL gate bank; `GATE_IPU_ADL_I` creates inverted gate entries in `ipu_adl_clks`; `ipu_adl_desc` is matched by `mediatek,mt8183-ipu_adl`.

Control flow: Simple probe registers the ADL gate provider for consumers in the IPU subsystem.

State and persistence behavior: State is limited to volatile gate bits and CCF provider metadata.

Dependencies and integration points: It depends on MT8183 clock bindings, inverted MediaTek gate ops, top-level IPU parents, and IPU data-link/accelerator consumers.

Risks and edge cases: The inverted gate operation is significant; normal polarity would reverse enable behavior. ADL also depends on broader IPU connection clocks.

Test signals: IPU ADL consumer probe, enable/disable behavior in clk summary, IPU workload involving ADL, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_adl.c -->
