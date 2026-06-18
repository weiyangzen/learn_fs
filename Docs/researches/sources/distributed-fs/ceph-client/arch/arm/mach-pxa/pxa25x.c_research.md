<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.c

Purpose: PXA21x/25x/26x SoC-specific init, IRQ wake, PM, IO mapping, default platform devices, and DMA slave map.

Important APIs/functions: `pxa25x_init_irq()` installs a 32-IRQ controller and `icip_handle_irq`; `pxa25x_map_io()` maps SMEMC and uncached alias regions and initializes clock frequency; PM callbacks save/restore `PSTR`, set `PSPR` resume address, and enter sleep via `pxa25x_finish_suspend()`. `pxa25x_set_wake()` routes GPIO0-84 to GPIO wake and RTC alarm to `PWER_RTC`.

Control flow: `postcore_initcall(pxa25x_init)` checks `cpu_is_pxa25x()`, registers watchdog reset status, installs PM hooks, registers IRQ/MFP syscore ops, and for non-DT boots registers GPIO software node, DMA controller info, and platform devices.

State and persistence: persistent PM table assignment, syscore registrations, platform devices, DMA slave map, and watchdog reset-status platform data. Sleep state uses `PSPR` and PXA power registers.

Dependencies and integration: depends on PXA2xx registers, MFP syscore, DMAengine, GPIO, reset, PM, SMEMC, and `devices.c`.

Risks and test signals: non-DT gating prevents duplicate devices under DT. Wake support is limited to hardware-supported GPIOs and RTC. Test PXA25x boot, DMA clients, UDC/RTC/SSP/PWM probes, suspend/resume, RTC wake, and watchdog reset-status reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.c -->
