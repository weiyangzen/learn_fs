# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pxa.c

Purpose: implements PXA27x/PXA3xx RTC support for the newer calendar registers while also initializing the SA1100-compatible sub-device block. It supports time, alarm 1, proc diagnostics, update/periodic interrupt reporting, and wakeup on alarm.

Important APIs/types/functions: `struct pxa_rtc` embeds `struct sa1100_rtc` and stores MMIO base, RTC, resource, and spinlock. `ryxr_calc()`, `rdxr_calc()`, and `tm_calc()` convert between split year/date and day/time registers. `rtsr_clear_bits()` and `rtsr_set_bits()` preserve trigger bits while updating enables. `pxa_rtc_irq()` reports alarm/update/periodic events. `pxa_rtc_read_time/set_time()` and `pxa_rtc_read_alarm/set_alarm()` implement RTC ops.

Control flow: probe allocates state, reads memory and IRQ resources, maps registers, requests the 1 Hz and alarm IRQs immediately through `pxa_rtc_open()`, wires SA1100 register pointers and calls `sa1100_rtc_init()`, clears interrupt enables, registers a separate `pxa-rtc` device, and marks wakeup capable. Remove frees both IRQs. Suspend/resume toggles wake on the alarm IRQ.

State and persistence: PXA hardware stores calendar time in `RYCR/RDCR`, alarm in `RYAR1/RDAR1`, and interrupt state/enables in `RTSR`. Driver state only protects register updates and keeps SA1100 integration data.

Dependencies and integration: depends on platform resources, OF compatible `marvell,pxa-rtc`, MMIO, RTC core, interrupt handling, proc output, PM sleep, and the local `rtc-sa1100.h` helper.

Risks: `pxa_rtc_open()` return value is ignored in probe, so IRQ request failure may not stop registration. The interrupt handler calls `rtc_update_irq()` even when `events` is zero. Both SA1100 and PXA RTC devices may expose overlapping hardware behavior. Test signals include IRQ request failure, SA1100 init failure, alarm/update/periodic interrupts, proc output, suspend wake, calendar conversion including weekday/month boundaries, and cleanup on probe errors.
