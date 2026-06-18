<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mpc8xxx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mpc8xxx_wdt.c`

Purpose: watchdog driver for Freescale/NXP MPC8xx/MPC83xx/MPC86xx watchdogs with one-time enable/disable hardware behavior and Open Firmware matching.

Important APIs, types, and functions: `struct mpc8xxx_wdt_ddata` stores MMIO base, watchdog core device, spinlock, and computed SWTC count. `mpc8xxx_wdt_keepalive()` writes the required `0x556c`/`0xaa39` service sequence under spinlock. `mpc8xxx_wdt_start()` programs SWCRR with enable, prescaler, count, and reset/interrupt mode, verifies enable, marks `WDOG_HW_RUNNING`, and pings.

Control flow: `arch_initcall()` registers the platform driver early. Probe gets match data, system frequency, maps registers, rejects hardware-enabled-only variants if firmware has not enabled them, optionally maps reset status resource to set/clear bootstatus, initializes watchdog core timeout and nowayout, computes SWTC/max hardware heartbeat, starts if already enabled, registers, and stores drvdata.

State and persistence: hardware may only allow enable or disable once after power-on reset. For variants marked `hw_enabled`, software cannot enable if firmware did not. Reset-cause bits are read and cleared from an optional second memory resource. Logical timeout is adjusted to at least hardware minimum heartbeat.

Dependencies and integration points: depends on OF compatibles `mpc83xx_wdt`, `fsl,mpc8610-wdt`, `fsl,mpc823-wdt`, `fsl_get_sys_freq()`, big-endian MMIO access, watchdog core, and early platform-driver registration.

Risks and test signals: risks include one-time enable semantics, reset versus interrupt mode module parameter, system-frequency conversion, and bootstatus clear side effects. Test firmware-enabled and software-enabled variants, keepalive sequence, reset-status resource handling, timeout/SWTC calculation, nowayout, and mode selection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mpc8xxx_wdt.c -->
