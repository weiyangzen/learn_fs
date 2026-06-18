# sources/distributed-fs/ceph-client/arch/sparc/kernel/setup.c

Purpose: registers SPARC kernel sysctls shared by 32-bit and 64-bit builds for reboot command, STOP-A behavior, serial-console poweroff, and 64-bit TSB ratio.

Important APIs/functions: defines `sparc_sysctl_table` and `init_sparc_sysctls()`, registered with `arch_initcall()`.

Control flow: at arch init time, `register_sysctl_init("kernel", sparc_sysctl_table)` exposes `/proc/sys/kernel/reboot-cmd`, `/proc/sys/kernel/stop-a`, `/proc/sys/kernel/scons-poweroff`, and on SPARC64 `/proc/sys/kernel/tsb-ratio`.

State and persistence: sysctls mutate runtime globals `reboot_command`, `stop_a_enabled`, `scons_pwroff`, and `sysctl_tsb_ratio`. Values are runtime kernel state; persistence is external if user space saves/restores sysctls.

Dependencies and integration points: integrates with generic sysctl registration, reboot/poweroff code, STOP-A PROM break handlers in setup files, and SPARC64 TSB management.

Risks: sysctl names are user-facing ABI. Buffer length for `reboot_command` must match command storage. Permissions allow root writes that directly affect reboot and PROM break behavior.

Test signals: presence and mutability of the sysctls under `/proc/sys/kernel`, reboot command honored by `machine_restart()`, STOP-A enable/disable behavior, serial console poweroff policy, and SPARC64 TSB ratio changes where applicable.
