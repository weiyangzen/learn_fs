<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/pm.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/pm.c

Purpose: Registers firmware-assisted suspend-to-RAM for Loongson64 LEFI systems.

Important APIs/types/functions: `loongson_lefi_sleep()` assembly entry, `lefi_pm_enter()`, `lefi_pm_valid_state()`, and `loongson_pm_init()`.

Control flow: Only `PM_SUSPEND_MEM` is valid, and only when firmware provided `loongson_sysconf.suspend_addr`. Enter marks suspend via firmware, calls the firmware sleep routine with that address, marks resume via firmware, and returns.

State and persistence: Installs platform suspend ops when `fw_interface == LOONGSON_LEFI`.

Dependencies and integration: Requires `sleeper.S` and firmware reset/suspend table parsing in `env.c`.

Risks: Firmware suspend address is trusted executable code. DTB-only systems get no suspend ops from this file.

Test signals: `/sys/power/state` should offer mem only when suspend address exists; entering mem should call firmware and return through `loongson_lefi_sleep`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/pm.c -->
