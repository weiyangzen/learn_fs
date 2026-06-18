# sources/distributed-fs/ceph-client/arch/m68k/apollo/config.c

Purpose: Apollo Domain workstation machine setup.

Important state includes physical address globals for serial, RTC, PIC A/B, CPU control, timer, and `apollo_model`. `apollo_parse_bootinfo()` reads `BI_APOLLO_MODEL`; `dn_setup_model()` maps supported model IDs to SAU7/SAU8 hardware address constants and rejects unsupported/unknown models. `config_apollo()` installs `mach_sched_init`, `mach_init_IRQ`, `mach_hwclk`, `mach_reset`, optional heartbeat, and model callbacks, then clears the DMA translation table.

Timer flow programs Apollo timer registers, unmasks a PIC B IRQ bit, requests `IRQ_APOLLO`, and `dn_timer_int()` calls `legacy_timer_tick(1)`, `timer_heartbeat()`, and reads timer bytes to clear/settle the interrupt. `dn_dummy_hwclk()` reads/writes RTC fields directly with a 1970/2000 adjustment for short years.

State/persistence is board address selection, `cpuctrl`, timer/RTC hardware registers, and the DMA address translation map. Reset is a stub that prints through serial and spins forever.

Dependencies include Apollo bootinfo, `asm/apollohw.h` mapped register macros, `dn_ints.c`, generic machdep hooks, and legacy timer APIs.

Risks and test signals: model array indexing assumes valid model range before printing; unsupported DN4500 panics; reset is not a real reboot. Test bootinfo parsing for each supported model, timer tick delivery, RTC read/write, heartbeat bit toggling, and DMA translation map clearing.
