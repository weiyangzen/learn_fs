<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.c

Purpose: Standby power-management support for Marvell Kirkwood. It maps DDR operation and memory power-control registers and registers suspend callbacks for `PM_SUSPEND_STANDBY`.

Important APIs/types/functions: `kirkwood_pm_init`, `kirkwood_low_power`, `kirkwood_suspend_enter`, and `kirkwood_pm_valid_standby` integrate with Linux suspend through `platform_suspend_ops` and `suspend_set_ops`.

Control flow, state, and persistence: Suspend saves `MEMORY_PM_CTRL`, forces peripheral low power, requests DDR self-refresh, executes `cpu_do_idle`, then restores the saved register. State persists only in the mapped hardware registers.

Dependencies and integration points: `kirkwood_pm_init`, `kirkwood_low_power`, `kirkwood_suspend_enter`, and `kirkwood_pm_valid_standby` integrate with Linux suspend through `platform_suspend_ops` and `suspend_set_ops`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: The code assumes `ioremap` succeeds and only supports standby. Risks are bad physical constants, missing wake sources, and relaxed-write ordering around DDR self-refresh. Test standby/resume, serial wake, peripheral retention, and suspend rejection for unsupported states.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 68 lines, 1495 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.c -->
