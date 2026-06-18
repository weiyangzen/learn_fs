<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7203.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7203.c

Purpose: defines SH7203/SH7263 legacy clock operations.

Important APIs/types/functions: `master_clk_init()`, `module_clk_recalc()`, `bus_clk_recalc()`, `arch_init_clk_ops()`.

Control flow: derives legacy master/module/bus clocks from mode pins/register values for SH7203-family devices.

State and persistence: clock framework stores derived rates after registration.

Dependencies/integration: integrates with setup-sh7203 SCIF/CMT/MTU/USB resources.

Risks: wrong base rate or divisor gives broken console and timers.

Test signals: verify early console baud, CMT tick, and peripheral clock aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7203.c -->
