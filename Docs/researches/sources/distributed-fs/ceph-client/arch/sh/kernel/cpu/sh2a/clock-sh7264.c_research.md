<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7264.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7264.c

Purpose: registers SH7264 modern legacy-clock objects.

Important APIs/types/functions: `arch_clk_init()`, `pll_recalc()`, main clocks, div4 clocks, MSTP clocks, clkdev lookup table.

Control flow: derives PLL from FRQCR and mode pins, registers root/divider/module-stop clocks, and maps device fck aliases to MSTP gates.

State and persistence: clock state is registered clk objects plus STBCR gate bits and FRQCR divisor fields.

Dependencies/integration: integrates SCIF, VDC, CMT, USB, MTU2, SDHI, ADC, RTC clock lookup.

Risks: wrong mode-pin divisor or MSTP bit disables devices or skews rates.

Test signals: verify clock tree rates and enable/disable for each listed peripheral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7264.c -->
