<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock.c

Purpose: coordinates SH architecture clock initialization.

Important APIs/types/functions: `clk_init()`.

Control flow: calls `arch_clk_init()` unless common-clk is used, then machine-vector `mv_clk_init`, recalculates root clocks, and enables init clocks.

State and persistence: clock framework state persists in registered clock objects.

Dependencies/integration: integrates CPU clock code, machine vector clock hooks, and legacy/common clock configuration.

Risks: failure ordering can leave partially registered clocks; missing init clocks breaks timer/console early.

Test signals: boot with and without common-clk and verify clock lookup/rates for timers and serial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock.c -->
