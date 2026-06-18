<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/clock-sh7619.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/clock-sh7619.c

Purpose: defines SH7619 legacy clock operations.

Important APIs/types/functions: `master_clk_init()`, `module_clk_recalc()`, `bus_clk_recalc()`, `arch_init_clk_ops()`.

Control flow: uses `CONFIG_SH_PCLK_FREQ` as root, derives module/bus clocks, and supplies ops to legacy CPG registration.

State and persistence: clock rates live in registered legacy `struct clk` instances.

Dependencies/integration: integrates with `clock-cpg.c` and SH7619 timer/serial/ether devices.

Risks: wrong divisors break serial baud and timer tick.

Test signals: verify clock rates for CMT, SCIF, and Ethernet on SH7619.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/clock-sh7619.c -->
