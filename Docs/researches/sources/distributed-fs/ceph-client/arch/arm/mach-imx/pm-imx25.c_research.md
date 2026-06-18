# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx25.c

Purpose: Minimal i.MX25 suspend-to-memory registration.

Important APIs/types/functions: Defines `imx25_suspend_enter()`, `imx25_suspend_ops`, and `imx25_pm_init()`.

Control flow: Initialization installs suspend ops. Enter accepts only `PM_SUSPEND_MEM` and executes `cpu_do_idle()` when PM is enabled; unsupported states return `-EINVAL`.

State and persistence: No persistent software state beyond global suspend ops. Hardware state changes are whatever WFI/idle triggers on i.MX25.

Dependencies and integration points: Depends on Linux suspend core and ARM idle instruction; called from i.MX25 machine init.

Risks: This is shallow suspend support with no explicit wake/clock/memory sequencing. Platforms needing deeper retention depend on bootloader/SoC defaults and interrupt wake configuration.

Test signals: Build with `CONFIG_PM`, run `echo mem > /sys/power/state`, and validate wake sources and resume console.
