<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7201.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7201.c

Purpose: defines SH7201 legacy clock operations.

Important APIs/types/functions: `master_clk_init()`, `module_clk_recalc()`, `bus_clk_recalc()`, `cpu_clk_recalc()`, `arch_init_clk_ops()`.

Control flow: reads mode/frequency configuration and derives module, bus, and CPU clock rates for the legacy clock framework.

State and persistence: state is registered clock rates and hardware mode bits.

Dependencies/integration: integrates with SH7201 setup devices, timer, and serial drivers.

Risks: bad divisor tables break baud/timer calibration.

Test signals: boot SH7201 and verify cpu/peripheral/bus clock rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7201.c -->
