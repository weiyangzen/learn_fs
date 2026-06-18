<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.c

Purpose: PXA restart support through soft restart, GPIO reset, or OS-timer watchdog reset.

Important APIs/functions: `init_gpio_reset()` requests and configures a reset GPIO. `pxa_restart()` disables IRQ/FIQ, clears reset status, and dispatches on reboot mode. `do_gpio_reset()` pulses the registered GPIO then falls back to hardware reset. `do_hw_reset()` arms the OS timer watchdog for roughly 100 ms and continuously writes `MDREFR_SLFRSH` to avoid the PXA270 SDRAM watchdog-reset erratum.

Control flow: machine descriptors set `.restart = pxa_restart`. Reboot paths invoke it with mode. GPIO reset requires prior `init_gpio_reset()` by board code; otherwise only hard/soft reset paths are safe.

State and persistence: static `reset_gpio` stores the registered reset line. Hardware reset status is cleared before restart; watchdog/timer and SDRAM refresh registers are mutated.

Dependencies and integration: depends on GPIO, ARM `soft_restart()`, OS timer registers, SMEMC `MDREFR`, and `clear_reset_status()`.

Risks and test signals: `REBOOT_GPIO` without initialization triggers `BUG_ON`. Hard reset intentionally never returns. Test soft restart, hard watchdog reset, GPIO reset board wiring, and PXA270 erratum path by observing successful reboot without SDRAM hang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.c -->
