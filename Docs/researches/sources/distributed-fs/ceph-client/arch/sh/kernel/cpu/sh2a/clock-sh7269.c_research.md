<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7269.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7269.c

Purpose: registers SH7269 modern legacy-clock objects.

Important APIs/types/functions: `arch_clk_init()`, `pll_recalc()`, peripheral recalc helpers, div4 and MSTP clock arrays.

Control flow: registers root/extal/PLL/peripheral clocks, DIV4 CPU/bus clocks, and per-device MSTP gates for SCIF0-7, CMT, USB, MTU2, ADC, RTC.

State and persistence: state is clock framework objects and FRQCR/STBCR hardware fields.

Dependencies/integration: integrates SH7269 platform devices with clkdev aliases.

Risks: fixed PLL/peripheral divisors must match board oscillator or timers and baud rates drift.

Test signals: verify extal override, clock rates, and gated peripheral resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7269.c -->
