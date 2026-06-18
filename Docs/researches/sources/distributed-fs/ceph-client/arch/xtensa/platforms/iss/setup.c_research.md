# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/setup.c

Purpose: Provides ISS platform setup, command-line import from simulator argv, panic exit, restart, and power-off handlers.

Important APIs, types, and functions: `iss_power_off()`, `iss_restart()`, `iss_panic_event()`, `iss_panic_block`, and `platform_setup()`.

Control flow: `platform_setup()` queries simulator argc/argv size, imports argv into static buffers when more than one argument is present, joins argv[1..] into the kernel command line, registers a panic notifier that exits host with status 1, and registers restart/poweroff sys_off handlers. Restart calls `cpu_reset()`, poweroff calls `simc_exit(0)`.

State and persistence: Static initdata argv/cmdline buffers hold imported command line during boot; panic notifier and sys_off handlers persist after setup.

Dependencies and integration: Xtensa generic setup calls `platform_setup()`, ISS `simcall.h`, panic notifier chain, and sys-off framework.

Risks: Command-line concatenation relies on prior argv-size bound but still uses `strcat`; oversized argv logs an error and leaves original command line; panic exits simulator immediately, which may bypass normal shutdown.

Test signals: ISS boot with simulator arguments, long command-line rejection, panic exit status, `reboot`, and `poweroff`.
