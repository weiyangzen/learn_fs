<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock-cpg.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock-cpg.c

Purpose: provides the deprecated legacy CPG clock registration path.

Important APIs/types/functions: `cpg_clk_init()`, weak `arch_clk_init()`, master/peripheral/bus/cpu clocks and clkdev aliases.

Control flow: registers on-chip clocks, attaches subtype ops via `arch_init_clk_ops`, adds timer/peripheral aliases, and returns combined registration status.

State and persistence: clock rates and enable flags live in legacy `struct clk` objects.

Dependencies/integration: integrates old SH clock framework with TMU/CMT/MTU and subtype clock ops.

Risks: clock ordering is explicitly significant; alias drift breaks timer/serial clock lookup.

Test signals: boot legacy CPG platforms and verify timer and serial clocks resolve/rate correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock-cpg.c -->
