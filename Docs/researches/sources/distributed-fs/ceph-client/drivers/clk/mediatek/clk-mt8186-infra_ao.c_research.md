<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-infra_ao.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-infra_ao.c

Purpose: This is the MT8186 always-on infrastructure clock and reset provider. It exposes many gates for PMIC, SCP, security, timers, USB, I2C, PWM, UART, DMA, SPI, MSDC, DVFS, debug, audio, modem interfaces, ADSP, flash, and related AO services.

Important APIs, types, and functions: Four gate banks `infra_ao0` through `infra_ao3` are described by `infra_ao*_cg_regs` and `GATE_INFRA_AO*` macros, with selected `CLK_IS_CRITICAL` gates. `infra_ao_rst_desc` uses MTK set/clear reset support and reset maps from `mt8186-resets.h`. `infra_ao_desc` includes gates and reset descriptor and binds `mediatek,mt8186-infracfg_ao`.

Control flow: Simple probe registers all AO gates, registers the reset controller from the descriptor, and exposes the OF provider. Consumers across many buses use these clocks during normal boot and low-power transitions.

State and persistence behavior: Gate and reset state is volatile AO register state, but many clocks are always-on in practice. Provider data is runtime-only.

Dependencies and integration points: It depends on MT8186 clock and reset bindings, common MediaTek gate/reset helpers, topckgen parents, and most peripheral/infra consumers.

Risks and edge cases: This file controls critical infrastructure clocks; accidentally gating critical SCP/SSPM/security/timer clocks can hang the system. The visible stray space before one macro definition is stylistic but compile-safe. Reset mapping must match hardware bank numbering.

Test signals: Full platform boot, UART/I2C/SPI/MSDC/USB/audio/security/modem-interface operation, reset-controller consumers, suspend/resume, critical gates remaining enabled, and clk summary inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-infra_ao.c -->
