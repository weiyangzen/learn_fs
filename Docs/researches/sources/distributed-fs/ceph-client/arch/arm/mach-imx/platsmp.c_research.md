# sources/distributed-fs/ceph-client/arch/arm/mach-imx/platsmp.c

Purpose: SMP bring-up glue for i.MX SCU-based SoCs, i.MX7D, and LS1021A.

Important APIs/types/functions: Defines `imx_scu_map_io()`, `imx_smp_prepare()`, `imx_smp_ops`, `imx7_smp_ops`, `ls1021a_smp_ops`, `imx_boot_secondary()`, `imx_smp_init_cpus()`, `imx7_smp_init_cpus()`, and the exported diagnostic-register variable `g_diag_reg` consumed by secondary startup code.

Control flow: For classic i.MX, early code maps the SCU using CP15, SCU core count limits `cpu_possible`, prepare enables SCU and snapshots the diagnostic register, and secondary boot writes the jump address through SRC then enables the core. i.MX7 counts CPU DT nodes because its SCU does not report cores. LS1021A writes `secondary_startup` to DCFG scratch and wakes CPUs via IPI.

State and persistence: State is limited to static `scu_base`, the static SCU map descriptor, and `g_diag_reg`. Hardware state includes SCU enable, SRC boot vector/core enable written by other i.MX helpers, and LS1021A DCFG scratch register.

Dependencies and integration points: Depends on ARM SMP core, SCU helpers, DT CPU nodes, i.MX SRC helpers (`imx_set_cpu_jump`, `imx_enable_cpu`), hotplug callbacks (`imx_cpu_die/kill`), and LS1021A DCFG DT node.

Risks: `BUG_ON(!dcfg_base)` and assumptions about SCU/DT availability make malformed firmware fatal. The diagnostic-register replication relies on secondary code reading `g_diag_reg` coherently after `sync_cache_w`. CPU count mismatch can hide or expose nonexistent CPUs.

Test signals: Boot SMP on i.MX6/i.MX7/LS1021A, check secondary CPU online, CPU hotplug if enabled, and verify no bad `cpu_possible` count with DT changes.
