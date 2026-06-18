<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7206.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7206.c

Purpose: defines SH7206/MX-G legacy clock operations.

Important APIs/types/functions: `master_clk_init()`, `module_clk_recalc()`, `bus_clk_recalc()`, `cpu_clk_recalc()`, `arch_init_clk_ops()`.

Control flow: calculates CPU, bus, and module clocks from FRQ/mode settings and supplies ops to CPG init.

State and persistence: state lives in legacy clock objects and source hardware frequency registers.

Dependencies/integration: used by SH7206 and MX-G setup through Kbuild selection.

Risks: shared use by MX-G means subtype assumptions must be checked carefully.

Test signals: test both SH7206 and MX-G clock rates and timer serial behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7206.c -->
