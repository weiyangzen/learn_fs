<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/reset.c

Purpose: Hooks Linux reboot, halt, and poweroff operations for Loongson2EF.

Important APIs/types/functions: `loongson_reboot()` jumps to `LOONGSON_BOOT_BASE`; `loongson_restart()`, `loongson_poweroff()`, `loongson_halt()`, and `mips_reboot_setup()`.

Control flow: Restart runs board `mach_prepare_reboot()` then jumps to boot ROM, optionally using inline assembly for CPU jump workarounds. Poweroff delegates to `mach_prepare_shutdown()` and returns to generic hang delay. Halt prints a notice and loops on `cpu_wait`.

State and persistence: Assigns global reboot hooks `_machine_restart`, `_machine_halt`, and `pm_power_off`.

Dependencies and integration: Board-specific reset files supply `mach_prepare_reboot()` and `mach_prepare_shutdown()`.

Risks: Ioremapping only 4 bytes at the boot base and executing it assumes firmware reset vector semantics. If board shutdown fails, power remains on and generic hang loop follows.

Test signals: `reboot`, `halt`, and `poweroff` should route through board-specific GPIO/EC preparation and either restart firmware or enter the expected halt state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/reset.c -->
