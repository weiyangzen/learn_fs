# sources/distributed-fs/ceph-client/arch/sparc/kernel/reboot.c

Purpose: implements SPARC64 reboot, halt, and poweroff hooks using PROM services, plus the serial-console poweroff policy and `pm_power_off` compatibility symbol.

Important APIs/functions: defines `scons_pwroff`, `pm_power_off`, `machine_power_off()`, `machine_halt()`, and `machine_restart()`.

Control flow: poweroff calls `prom_halt_power_off()` unless the console is serial and `scons_pwroff` is disabled, then falls back to `prom_halt()`. Halt directly calls `prom_halt()` and panics if it returns. Restart strips a newline from `reboot_command`, tries the explicit command, then the configured command, then an empty PROM reboot command, and panics if all return.

State and persistence: runtime global `reboot_command` comes from setup/sysctl code, `scons_pwroff` controls serial-console poweroff behavior, and `pm_power_off` points to `machine_power_off`. No persistent state is modified.

Dependencies and integration points: depends on PROM reboot/halt/poweroff operations, OF console device type, generic reboot and PM hooks, and sysctl registration in `setup.c`.

Risks: PROM calls are expected not to return. Serial-console poweroff is policy-sensitive because powering off may remove the only management console. Command string mutation strips at the first newline.

Test signals: `reboot`, `halt`, and `poweroff` commands on serial and non-serial consoles; `/proc/sys/kernel/reboot-cmd`; `/proc/sys/kernel/scons-poweroff`; and panic fallback only if PROM unexpectedly returns.
