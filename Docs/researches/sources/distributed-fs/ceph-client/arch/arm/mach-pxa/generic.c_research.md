<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.c

Purpose: common PXA machine code for reset status, timer/clock initialization, SMEMC helpers, and base IO mapping.

Important APIs: `clear_reset_status()` dispatches to PXA2xx RCSR or PXA3xx ARSR semantics. `pxa_timer_init()` initializes clocks per CPU family and starts the non-DT PXA timer. `pxa_smemc_set_pcmcia_timing()`, `pxa_smemc_set_pcmcia_socket()`, and `pxa_smemc_get_mdrefr()` are exported for PCMCIA/static-memory users. `pxa_map_io()` maps the common peripheral window and initializes debug IO.

Control flow: machine descriptors call `pxa_map_io()` through SoC-specific wrappers, then legacy init paths call `pxa_timer_init()`. SMEMC helpers are invoked later by drivers.

State and persistence: writes memory-controller registers `MCMEM`, `MCATT`, `MCIO`, `MECR`, and reset status registers. The common IO mapping remains permanent.

Dependencies and integration: uses CPU detection helpers, PXA clock init functions, `clocksource/pxa.h`, SMEMC register definitions, and address-map constants.

Risks and test signals: direct register writes assume the correct SoC family and mapped windows. Test early boot timer interrupts, clock registration, PCMCIA timing on boards using sockets, and reset-status clearing across reboot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.c -->
