# sources/distributed-fs/ceph-client/arch/mips/dec/time.c

Purpose: handles DECstation persistent RTC time, RTC updates, and platform timer initialization.

Important APIs: `read_persistent_clock64()` reads DS1287/CMOS time plus DEC real-year storage. `update_persistent_clock64()` updates minutes/seconds safely using RTC set/divider-reset sequencing. `plat_time_init()` configures DS1287 periodic interrupts, optional IOASIC clocksource, CP0 Count calibration, and DS1287 clockevent.

Control flow: persistent read loops until seconds are stable, converts BCD if needed, and reconstructs year from `RTC_DEC_YEAR`. Timer init measures CP0 Count over DS1287 ticks when available; on R4k DECstations with count errata, it may use CP0 Count only as clocksource and clears `mips_hpt_frequency` if no IOASIC clock exists.

State and integration: updates global `mips_hpt_frequency`, RTC registers, DS1287 clockevent on `dec_interrupt[DEC_IRQ_RTC]`, and optional IOASIC clocksource state.

Risks and test signals: RTC year storage and half-hour correction logic are platform-specific. Timer errata handling affects scheduling precision. Test persistent clock read/write, RTC interrupt delivery, stable timekeeping, and systems with and without IOASIC clocksource.
