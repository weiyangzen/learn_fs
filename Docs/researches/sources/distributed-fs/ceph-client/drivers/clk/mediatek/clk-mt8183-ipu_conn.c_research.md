<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_conn.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_conn.c

Purpose: This file registers MT8183 IPU connection and bus clock gates, including APB and several AXI gate banks that connect IPU cores to the rest of the SoC.

Important APIs, types, and functions: It defines five gate-register groups: `ipu_conn_cg_regs`, `ipu_conn_apb_cg_regs`, `ipu_conn_axi_cg_regs`, `ipu_conn_axi1_cg_regs`, and `ipu_conn_axi2_cg_regs`. `ipu_conn_clks` combines normal and inverted gates through `GATE_IPU_CONN*` macros. `ipu_conn_desc` is matched by `mediatek,mt8183-ipu_conn`.

Control flow: Simple probe registers all bus/connection gates and exposes them as one OF provider. IPU core and ADL drivers depend on these clocks for bus access.

State and persistence behavior: Gate state is volatile across IPU connection MMIO registers. Provider state exists only while the driver is bound.

Dependencies and integration points: It depends on MT8183 bindings, common gate helpers, topckgen IPU parents, IPU core drivers, power domains, and memory fabric/IOMMU paths.

Risks and edge cases: Multiple banks and inverted gates make bit/polarity errors likely. Bus gates must be enabled before core access, so sequencing bugs can cause bus faults.

Test signals: IPU subsystem probe order, IPU workloads, runtime PM with core0/core1/ADL, clk summary for APB/AXI gates, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-ipu_conn.c -->
