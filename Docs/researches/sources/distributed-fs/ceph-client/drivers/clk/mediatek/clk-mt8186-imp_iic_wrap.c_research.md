<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-imp_iic_wrap.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-imp_iic_wrap.c

Purpose: This driver exposes MT8186 I2C wrapper clock gates.

Important APIs, types, and functions: `imp_iic_wrap_cg_regs` defines the gate bank; `GATE_IMP_IIC_WRAP` populates `imp_iic_wrap_clks`; `imp_iic_wrap_desc` is matched by `mediatek,mt8186-imp_iic_wrap`.

Control flow: Simple probe registers wrapper gates and publishes them for I2C wrapper consumers.

State and persistence behavior: Gate state is volatile hardware state; provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8186 clock bindings, common gate helpers, topckgen I2C/AXI parents, and I2C controller/wrapper drivers.

Risks and edge cases: I2C wrapper gates affect multiple buses; a wrong gate bit can break peripheral discovery. Runtime PM ordering with infracfg clocks matters.

Test signals: Probe all I2C buses behind the wrapper, transfer traffic, observe gate enable counts, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-imp_iic_wrap.c -->
